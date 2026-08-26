#!/usr/bin/env python3
"""Offline integrity checks for the 2026-08-26 accepted-current snapshot."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
TEMPLATES = HERE.parent.parent / "templates"

CANONICAL_FILES = {
    "qweb/vat/report_invoice_document_vat.xml":
        TEMPLATES / "vat/VAT_ARCH_barani_vat.report_invoice_document_vat.xml",
    "qweb/vat/external_layout_standard_titled.xml":
        TEMPLATES / "vat/LAYOUT_ARCH_barani_vat.external_layout_standard_titled.xml",
    "qweb/commercial/report_saleorder_document.xml":
        TEMPLATES / "commercial/BODY_ARCH_barani_commercial.report_saleorder_document.xml",
    "qweb/commercial/external_layout_standard_titled.xml":
        TEMPLATES / "commercial/LAYOUT_ARCH_barani_commercial.external_layout_standard_titled.xml",
    "qweb/commercial/report_saleorder.xml":
        TEMPLATES / "commercial/WRAPPER_ARCH_barani_commercial.report_saleorder.xml",
    "qweb/commercial/report_saleorder_proforma.xml":
        TEMPLATES / "commercial/WRAPPER_ARCH_barani_commercial.report_saleorder_proforma.xml",
    "qweb/delivery-note/report_delivery_note_2026.xml":
        TEMPLATES / "delivery-note/DELIVERY_ARCH_barani_delivery.report_delivery_note_2026.xml",
    "qweb/delivery-note/external_layout_delivery_2026.xml":
        TEMPLATES / "delivery-note/LAYOUT_ARCH_barani_delivery.external_layout_delivery_2026.xml",
    "qweb/delivery-note/report_sale_order_delivery_note_2026.xml":
        TEMPLATES / "delivery-note/SO_BRIDGE_ARCH_barani_delivery.report_sale_order_delivery_note_2026.xml",
    "qweb/pick-list/report_picking_operations_2026.xml":
        TEMPLATES / "pick-list/PICKOPS_ARCH_barani_delivery.report_picking_operations_2026.xml",
    "qweb/pick-list/external_layout_picking_operations_2026.xml":
        TEMPLATES / "pick-list/LAYOUT_ARCH_barani_delivery.external_layout_picking_operations_2026.xml",
}

PORTABLE_REPLACEMENTS = {
    "SK1483300000002401465895": "XX0000000000000000000000",
    "FIOZSKBAXXX": "YOURBICXXX",
    "Brectanova 2353/1, 83101 Bratislava, SVK": "YOUR_EXW_DEFAULT_LOCATION",
}


def exact_arch(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise ValueError(f"{path}: expected exactly one publication LF")
    return text[:-1]


def md5(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def storage_md5(text: str) -> str:
    raw = json.dumps(
        {"en_US": text}, ensure_ascii=False, separators=(", ", ": ")
    )
    return md5(raw.encode("utf-8"))


def main() -> int:
    errors: list[str] = []
    qweb_meta = json.loads(
        (HERE / "metadata/qweb_target.json").read_text(encoding="utf-8")
    )
    action_meta = json.loads(
        (HERE / "metadata/report_actions_target.json").read_text(encoding="utf-8")
    )
    paper_meta = json.loads(
        (HERE / "metadata/paperformats.json").read_text(encoding="utf-8")
    )

    if len(qweb_meta.get("views", [])) != 11:
        errors.append("qweb_target.json must describe exactly 11 views")
    if len(action_meta.get("actions", [])) != 11:
        errors.append("report_actions_target.json must describe exactly 11 actions")
    if len(action_meta.get("filename_expressions", {})) != 6:
        errors.append("report_actions_target.json must contain 6 expression families")
    if len(paper_meta) != 4:
        errors.append("paperformats.json must describe exactly 4 paper formats")

    expressions = action_meta.get("filename_expressions", {})
    expression_hashes = action_meta.get("filename_expression_sha256", {})
    if set(expressions) != set(expression_hashes):
        errors.append("filename expression and hash keys differ")
    for name, expression in expressions.items():
        actual = sha256(expression.encode("utf-8"))
        if actual != expression_hashes.get(name):
            errors.append(f"filename expression hash mismatch: {name}")

    roles: set[str] = set()
    for action in action_meta.get("actions", []):
        role = action.get("role", "")
        if not role or role in roles:
            errors.append(f"missing or duplicate report-action role: {role!r}")
        roles.add(role)
        if action.get("filename_expression") not in expressions:
            errors.append(f"{role}: unknown filename expression")
        for field in ("label_storage_md5", "filename_storage_md5"):
            value = action.get(field, "")
            if len(value) != 32 or any(c not in "0123456789abcdef" for c in value):
                errors.append(f"{role}: invalid {field}")

    seen_files: set[str] = set()
    for view in qweb_meta.get("views", []):
        rel = view["file"]
        seen_files.add(rel)
        path = HERE / rel
        try:
            arch = exact_arch(path)
            ET.fromstring(arch)
        except (OSError, ValueError, ET.ParseError) as exc:
            errors.append(f"{rel}: {exc}")
            continue
        raw = arch.encode("utf-8")
        checks = {
            "chars": len(arch),
            "plain_md5": md5(raw),
            "plain_sha256": sha256(raw),
            "storage_md5": storage_md5(arch),
        }
        for field, actual in checks.items():
            if actual != view[field]:
                errors.append(
                    f"{rel}: {field}={actual!r}, expected {view[field]!r}"
                )

        portable = arch
        for source, replacement in PORTABLE_REPLACEMENTS.items():
            portable = portable.replace(source, replacement)
        canonical_path = CANONICAL_FILES.get(rel)
        if canonical_path is None:
            errors.append(f"{rel}: no canonical template mapping")
        else:
            try:
                canonical = exact_arch(canonical_path)
            except (OSError, ValueError) as exc:
                errors.append(f"{canonical_path}: {exc}")
            else:
                if canonical != portable:
                    errors.append(
                        f"{rel}: canonical template differs beyond approved substitutions"
                    )

    if seen_files != set(CANONICAL_FILES):
        errors.append("QWeb metadata and canonical mappings do not cover the same files")

    vat = exact_arch(HERE / "qweb/vat/report_invoice_document_vat.xml")
    commercial = exact_arch(HERE / "qweb/commercial/report_saleorder_document.xml")
    delivery = exact_arch(HERE / "qweb/delivery-note/report_delivery_note_2026.xml")
    required_tokens = {
        "VAT shipping": (vat, 't-if="o.partner_shipping_id"'),
        "VAT 10 mm gutter": (vat, "padding-left: 10mm"),
        "Commercial 10 mm gutter": (commercial, "padding-left: 10mm"),
        "Delivery L2.2 marker": (delivery, "addrlabels_32_shipalways_10mm_windowrefs"),
        "Delivery always-shipping policy": (delivery, "bool(barani_shipping)"),
        "Delivery window information": (delivery, "barani_dn_window_information"),
        "Delivery Incoterms": (delivery, "barani_incoterms_code"),
    }
    for label, (content, token) in required_tokens.items():
        if token not in content:
            errors.append(f"missing semantic token: {label}")

    expected_menu = ["Packages", "Delivery Slip", "Picking Operations"]
    if action_meta.get("stock_print_menu", {}).get("visible_labels") != expected_menu:
        errors.append("stock Print-menu contract differs from accepted order")

    if errors:
        print("FAIL — accepted-current snapshot validation")
        for error in errors:
            print(f"- {error}")
        return 1

    print("PASS — 11 QWeb views, 11 report actions, 4 paper formats")
    print("PASS — exact target hashes and XML parsing")
    print("PASS — portable canonical sources differ only by approved constants")
    print("PASS — semantic and stock Print-menu contracts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
