# Run order — BARANI report routing + Preview

1. Pull latest GitHub main and record HEAD.
2. Run P01 read-only, all pages.
3. Run P03 read-only, all pages.
4. Choose C10 WITHOUT_PAYMENT_MODE from P03.
5. Run B10 dry-run; apply after review.
6. Run C10 dry-run; apply after review.
7. Run C20 dry-run; apply after review.
8. Run V30.
9. Manually test standard Print, Send & Print, email attachments and Preview for RI/DPI/Credit Note.
10. Set all C30 manual gates True; dry-run; apply.
11. Verify final menus.
12. Run C31 dry-run; apply last.
13. Export current state and create a new restore point/GitHub milestone.
14. Use R10 if any acceptance gate fails.
