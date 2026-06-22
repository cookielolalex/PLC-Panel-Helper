# Source Roots

All declared source locations are READ-ONLY by policy. Do not write into these
paths and do not extract archives back into them.

| id | declared path | role | exact-path probe | policy |
|---|---|---|---|---|
| SRC-115-ZIP | `C:\Users\alex1\OneDrive\Desktop\115年度工作.zip` | Active yearly jobs archive | MISSING on 2026-06-22 | READ_ONLY |
| SRC-ST-BLOCK1 | `C:\Users\alex1\OneDrive\Desktop\案件備份\ST-Block1` | CAD block/reference library | MISSING on 2026-06-22 | READ_ONLY |
| SRC-VENDOR-CATALOGS | `C:\Users\alex1\OneDrive\Desktop\案件備份\器材型錄` | Vendor/equipment catalogs | MISSING on 2026-06-22 | READ_ONLY |
| SRC-LEGACY-PREP | `C:\Users\alex1\OneDrive\Desktop\案件備份_GPT整理` | Legacy prepared package when present | MISSING on 2026-06-22 | READ_ONLY |
| SRC-ALL-PROJECTS | `C:\Users\alex1\OneDrive\Desktop\All Projects` | Human-approved consolidated project root | EXISTS on 2026-06-22; 5 yearly directories observed | READ_ONLY |

Nearby unapproved clue: `C:\Users\alex1\OneDrive\Desktop\115年度工作` exists,
but it is not declared by the master specification and is not generator-eligible
without an explicit source-root decision.

Human update on 2026-06-22: the user stated, "All projects are now located at
`C:\Users\alex1\OneDrive\Desktop\All Projects`." The coordinator records this
as an approved project-evidence source root. CAD block and vendor catalog roots
remain unresolved unless separately found or approved.
