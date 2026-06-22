# Project Charter

Build a private-pilot Custom GPT package and reproducible local evaluation
harness for PLC/control-panel drawing drafts.

The generator accepts only approved current-project Excel workbook worksheets,
explicit current user corrections, frozen reusable Knowledge, approved rules,
schemas, renderers, and approved reusable metadata. It must never receive
`生管文件`, `電機施工圖`, completed target drawings, modified target drawings, or
any derivatives of those references.

Automated outputs are drafts for mandatory human CAD/fabrication review. No
automated component may claim fabrication release, certification, or production
approval.

