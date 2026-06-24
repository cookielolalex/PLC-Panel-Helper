# Source Fact Authority Matrix

Status: ACCEPTED FOUNDATION V1.

This matrix defines authority by fact family. It supersedes any single global
document-precedence rule for sheetmetal-v1.

| fact family | primary authority | secondary authority | forbidden resolver |
|---|---|---|---|
| project identity | explicit project requirement or accepted current decision | cross-source identity match | completed drawing title block |
| required quantity | `CONTRACT_REQUIREMENT` or `MATERIAL_REQUIREMENT` | explicit current correction | procurement ordered quantity |
| ordered quantity | `PROCUREMENT_EVIDENCE` | explicit current correction | material requirement |
| received quantity | `PROCUREMENT_EVIDENCE` | explicit receiving evidence | completed drawing |
| customer supplied status | `CUSTOMER_SUPPLIED_LIST` | explicit current correction | procurement assumption |
| functional connectivity | `APPROVED_FUNCTIONAL_ENGINEERING_SOURCE` | approved engineering rule | co-occurrence in material list |
| component family/model | approved material or functional source | verified component library normalization | completed drawing labels |
| footprint and mounting geometry | verified component library | model-specific approved rule | historical drawing geometry |
| compatible accessories | explicit source accessory | model-specific verified library rule, then approved family rule | duplicate inference |
| panel assignment | `PANEL_ALLOCATION_SOURCE` with pre-design chronology | approved deterministic assignment rule | completed sheet-metal drawing |
| panel dimensions | explicit project requirement or approved sizing rule | selected standard cabinet candidate | historical cabinet size copy |
| placement coordinates | generated design choice satisfying hard constraints | human correction | completed drawing coordinates |
| cutout size | explicit source or verified model/rule output | unresolved `UNVERIFIED` | guessed from symbol name |
| material/thickness | explicit project requirement | approved company default labelled as default | completed reference |

Every critical fact must carry one of:

- explicit source evidence;
- approved rule;
- verified component-library entry;
- design choice;
- `TBD`;
- `UNVERIFIED`;
- `CONFLICT`;
- `HUMAN_REVIEW_REQUIRED`;
- `NOT_APPLICABLE`.

