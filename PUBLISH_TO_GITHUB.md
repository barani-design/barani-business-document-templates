# Publish changes to GitHub

Canonical public repository:

```text
barani-design/barani-business-document-templates
```

Prepare and verify changes on a controlled local branch from the exact current `main` commit.
All network publication is manual and visible in GitHub Desktop:

1. Run the controlled local preparation script; it must perform no network operation.
2. In GitHub Desktop, verify the repository, branch, and commit, then click **Publish branch**
   (or **Push origin** only when the branch is already published).
3. Click **Fetch origin** once and run the separate read-only published-branch verifier.
4. Only after that verifier passes, fast-forward local `main` with the controlled script.
5. In GitHub Desktop, push `main`, click **Fetch origin** once, and run the read-only
   published-`main` verifier.

Do not use terminal `git push`, `git fetch`, or `git pull`. Do not create a pull request unless
an explicit owner decision requests one. Stop on **Pull origin**, unexpected changes, a conflict
or rebase prompt, the wrong repository/branch/commit, or **Preview Pull Request** as the proposed
next action.

Before publishing:

- run the milestone validator and all checksum manifests;
- parse all QWeb XML and JSON metadata;
- inspect the complete diff for customer data, credentials, database identity, backups, restore evidence, and logs;
- confirm any accepted-current business payment identifiers are covered by an explicit publication notice;
- keep tenant-bound production actions out of the public repository;
- verify the fetched remote-tracking ref against the exact authorized commit and tree after each
  GitHub Desktop publication step.
