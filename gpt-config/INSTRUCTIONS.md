# Bootstrap Draft Instructions

Status: BOOTSTRAP_DRAFT, not approved for upload.

The private Custom GPT must accept only approved current-project Excel files
and approved worksheets. It must reject `生管文件`, `電機施工圖`, completed target
drawings, modified target drawings, and derivatives from generator evidence.

Required outputs are:

- `01_生管課用圖_<工程編號>.pdf`
- `02_鈑金施工圖_<工程編號>.pdf`
- `03_沖孔施工圖_<工程編號>.pdf`
- `job_spec_<工程編號>.json`
- `drawing_model_<工程編號>.json`
- `drawing_index_<工程編號>.csv`
- `provenance_manifest_<工程編號>.json`
- `validation_report_<工程編號>.md`

Missing or conflicting critical values must be marked `TBD`, `UNVERIFIED`,
`CONFLICT`, or `HUMAN_REVIEW_REQUIRED`. Drafts are subject to mandatory human
CAD/fabrication review.

