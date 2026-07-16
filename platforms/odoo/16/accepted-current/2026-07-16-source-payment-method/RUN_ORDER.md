# Run order and recovery

## Fresh application

Use only on a database whose current QWeb bytes match the S00 preflight
expectations.

```text
1. S00 dry run
2. S00 apply
3. S01 dry run
4. S01 apply
5. Print commercial acceptance set
6. S01A dry run
7. S01A apply
8. Reprint long Customer Ref. test
9. S01B dry run
10. S01B apply
11. Reprint Q/SO/PF typography acceptance set
12. S02 dry run
13. S02 apply
14. Print RI/DPI/Credit Note acceptance set
15. Run S03 v5 read-only
```

## Accepted final audit

```text
SUMMARY problems=0 warnings=0 WRITE ACTIONS PERFORMED: NONE
RESULT: CONFIGURATION PASS
```

## Emergency rollback

Run S99 first as a dry run. Apply it only when rollback is explicitly required
and the S00 restore point is present and valid.

Do not delete the S00 restore parameters while this milestone remains active.
