# Privacy & Security

This project accesses files, screen, and can run automation. The app will always ask for explicit permission in the UI before performing such actions. Permission grants are recorded in the local SQLite DB and can be revoked.

To delete all local data, remove the `backend/data` directory and any exported files. Encrypted API keys are stored in `backend/data/secret.key` and will be unrecoverable without the passphrase.

Do not add credentials for systems you do not control.
