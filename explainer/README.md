# Standalone explainer

Open `clebsch-explorer.html` directly in a browser; no server is needed.
Edit `clebsch-explorer.template.html`, then run `just explainer` from the
repository root (requires Node.js).

`build.mjs` embeds the graph and coordinates using only checked-in `data/` inputs.
It checks the 192-part table, symmetry, internal blow-ups, and promoted pairs.
The output HTML is checked in for convenient offline reading.
