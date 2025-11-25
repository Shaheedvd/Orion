Backend (FastAPI)

Files:
- app.py: main FastAPI app and endpoints
- config/: settings and default settings
- memory/: SQLite schema, memory store, exporter
- models/: model loader and README
- tools/: automation, file tools, web research, image, voice
- utils/: logger, security, sandbox

Notes:
- Secrets are stored encrypted in `data/secret.key` using Fernet. For production, prompt user passphrase and store derived key.
