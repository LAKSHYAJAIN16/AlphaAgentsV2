# AlphaAgentsV2 desktop app

Electron + React/TypeScript frontend for AlphaAgentsV2. Talks to the local
FastAPI backend (`../backend/api.py`) over `http://127.0.0.1:8765`, which
the Electron main process spawns and manages automatically.

See the repo root [DESIGN.md](../DESIGN.md#desktop-app-frontend) for the
visual direction and architecture notes, and [PRODUCT.md](../PRODUCT.md)
for product context.

## Develop

```bash
pip install -r ../requirements.txt   # backend deps
npm install
npm run electron:dev
```

## Build

```bash
npm run build          # renderer only (dist/)
npm run electron:build # packaged desktop app (release/) — untested in this
                        # environment; SocialLang's sandbox hit a Windows
                        # EPERM extracting Electron's distribution in a
                        # sandboxed session, try a fresh session/machine
                        # first if this recurs
```
