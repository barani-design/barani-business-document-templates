# Publish changes to GitHub

Canonical public repository:

```text
barani-design/barani-business-document-templates
```

Use a branch and pull request from the current `main` branch. Before publishing:

- run the milestone validator and all checksum manifests;
- parse all QWeb XML and JSON metadata;
- inspect the complete diff for customer data, credentials, database identity, backups, restore evidence, and logs;
- confirm any accepted-current business payment identifiers are covered by an explicit publication notice;
- keep tenant-bound production actions out of the public repository;
- open and review a pull request before merging.
