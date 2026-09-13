# Licensing

This project (`projects/soarm101/` in wk-robotics) is a mixed hardware / software / documentation project and uses the
**tri-licence** standard for open-source hardware, matching the rest of the family
([`common.md`](../../docs/common.md#licensing)):

| Area | Covers | Licence | SPDX |
|------|--------|---------|------|
| **Hardware** | Any part, mount or fixture designed for this build (none yet) | CERN Open Hardware Licence v2 – Strongly Reciprocal | `CERN-OHL-S-2.0` |
| **Software** | Host-side scripts and tooling (`software/`) | MIT | `MIT` |
| **Docs & media** | Documentation, diagrams, photographs (`docs/`) | Creative Commons Attribution-ShareAlike 4.0 | `CC-BY-SA-4.0` |

**Note on the arm:** the SO-101 design — CAD, STLs, bill of materials, assembly guide — is
**upstream's work under Apache-2.0** and is **not carried in this repository**. It is
cloned alongside as a sibling. Nothing here relicenses it; the hardware licence covers only
parts designed for this build, of which there are currently none.

Each source file SHOULD carry an `SPDX-License-Identifier:` header naming its licence.
All three full licence texts are included verbatim in `LICENSES/` in this folder. The wk-robotics root `LICENSE` (CC-BY-SA-4.0) covers the family index and `docs/`, not this folder.
