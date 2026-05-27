# frontend

React + TypeScript + Vite + Three.js frontend for tempest-watch.

## Setup

```bash
npm install
npm run dev          # dev server with HMR
npm run build        # production build
npm run lint
npm run format
npm run typecheck
```

Three.js code is isolated in `src/three/` per `docs/CONVENTIONS.md` — scene, shader, and render-loop code must never leak into React component render paths.
