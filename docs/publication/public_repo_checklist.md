# Public repository checklist

Before publishing:

- [ ] Keep reusable-source bank constants as placeholders.
- [ ] Confirm license.
- [ ] Remove private PDFs and logs.
- [ ] Ensure templates do not contain live customer data.
- [ ] Decide whether to include BARANI-specific names or fully generic names.
- [ ] Run accepted-current validators and checksum manifests.
- [ ] Prepare and review a controlled local branch from the exact current `main` commit.
- [ ] Use GitHub Desktop only for Publish/Push/Fetch; do not use terminal network Git.
- [ ] Verify the fetched remote branch before fast-forwarding and pushing `main`.
- [ ] Do not create a pull request unless an explicit owner decision requests one.
- [ ] Exclude production database identity, backup/restore evidence, and tenant-bound actions.
