# Licensing

This project (`projects/soarm101/` in wk-robotics) is a mixed hardware / software / documentation project and uses the
**tri-licence** standard for open-source hardware, matching the rest of the family
([`common.md`](../../docs/common.md#licensing)):

| Area | Covers | Licence | SPDX |
|------|--------|---------|------|
| **Original hardware** | New parts, mounts or fixtures designed independently for this build (none yet) | CERN Open Hardware Licence v2 – Strongly Reciprocal | `CERN-OHL-S-2.0` |
| **Upstream-derived CAD** | `cad/lightweight-v1/step/`, `stl/`, including modified and unchanged SO-101 parts | Apache License 2.0, retained from upstream | `Apache-2.0` |
| **Software** | Host-side scripts and tooling, including CAD generation and analysis scripts | MIT | `MIT` |
| **Docs & media** | Documentation, diagrams, photographs (`docs/`) | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |

**Note on the arm:** the SO-101 design — CAD, STLs, bill of materials, assembly guide — is
**upstream's work under Apache-2.0**. The baseline repository is cloned alongside as a
sibling. Since 2026-09-21, the local [lightweight study](cad/lightweight-v1/README.md)
carries a derived STEP/STL set with its own Apache-2.0 licence copy and modification
notice. Nothing here relicenses that geometry under CERN-OHL. The study's README,
report and figures use the documentation licence; `comparison.ini` is explicitly
CC0-1.0. Original, independently designed hardware remains under CERN-OHL-S.

Each source file SHOULD carry an `SPDX-License-Identifier:` header naming its licence.
All three full licence texts are included verbatim in `LICENSES/` in this folder. The wk-robotics root `LICENSE` (CC-BY-SA-4.0) covers the family index and `docs/`, not this folder.
