# V2 Zero-Promotion Diagnosis

- status: `V2_ZERO_PROMOTION_DIAGNOSIS_COMPLETE`
- reviewed projects: `18`
- promotions: `0`
- files considered by existing isolated reviews: `282`
- pages counted from existing v2 classifications: `618`
- stored raw reference text/images/thumbnails: `false`

## Root Causes

- `classifier_seeing_metadata_and_transient_embedded_text_only`: `True`. All reviewed projects detected only SHEET_METAL; no v2 result recorded page_ranges from page text or visual page evidence.
- `inability_to_render_or_inspect_raster_pdfs`: `True`. V2 policy and classifier did not render pages or crop title blocks; image-only PDFs could not contribute visual role evidence.
- `overly_restrictive_document_level_contract`: `True`. Results are file/classification-level; no effective page-level target-output set, combined package registry, or supersession result exists.
- `one_file_one_type_or_metadata_type_bias`: `True`. Metadata/file role created whole-file SHEET_METAL classifications even for multipage files; missing types were not recoverable inside combined files.
- `revision_and_combined_pdf_handling_absent`: `True`. V2 wrote UNKNOWN_OR_NOT_METADATA_DETECTED and NOT_DETERMINED_METADATA_ONLY for revision/supersession.
- `target_drawings_under_generator_forbidden_folder_names_not_reviewed_as_reference_evidence`: `True`. V2 excluded forbidden production-control/electrical roles before page-level role confirmation.
- `genuinely_missing_drawing_types`: `NOT_PROVEN`. V2 produced insufficient content and page-level evidence to distinguish true absence from classification blindness.

Conclusion: zero promotion must be treated as a detector-contract failure until v3 page-level reference-vault review proves otherwise. V2 did not provide enough evidence to conclude that the missing target types are genuinely absent.

## Reviewed Projects

| project_id | decision | files | pages counted | detected types | missing types | v3 could resolve | incomplete likelihood |
|---|---|---:|---:|---|---|---|---|
| `1120801` | `PARTIAL_REFERENCE_SET` | 28 | 83 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1120902` | `PARTIAL_REFERENCE_SET` | 49 | 113 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1121102` | `PARTIAL_REFERENCE_SET` | 12 | 16 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1121107` | `PARTIAL_REFERENCE_SET` | 27 | 47 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1130610` | `PARTIAL_REFERENCE_SET` | 5 | 4 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `NOT_ESTABLISHED_BY_V2` |
| `1141201` | `PARTIAL_REFERENCE_SET` | 52 | 138 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1120706` | `PARTIAL_REFERENCE_SET` | 13 | 24 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1130104` | `PARTIAL_REFERENCE_SET` | 1 | 3 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `POSSIBLE_BUT_NOT_PROVEN` |
| `1140201` | `PARTIAL_REFERENCE_SET` | 11 | 21 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1140706` | `PARTIAL_REFERENCE_SET` | 12 | 30 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1141106` | `PARTIAL_REFERENCE_SET` | 12 | 24 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1150104` | `PARTIAL_REFERENCE_SET` | 21 | 53 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1121201` | `PARTIAL_REFERENCE_SET` | 16 | 37 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `UNLIKELY_TO_BE_PROVEN_BY_METADATA_ONLY; V3_REQUIRED` |
| `1130505` | `PARTIAL_REFERENCE_SET` | 6 | 10 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `NOT_ESTABLISHED_BY_V2` |
| `1130901` | `PARTIAL_REFERENCE_SET` | 5 | 3 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `NOT_ESTABLISHED_BY_V2` |
| `1131105` | `PARTIAL_REFERENCE_SET` | 6 | 6 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `NOT_ESTABLISHED_BY_V2` |
| `1140606` | `PARTIAL_REFERENCE_SET` | 3 | 3 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `POSSIBLE_BUT_NOT_PROVEN` |
| `1150103` | `PARTIAL_REFERENCE_SET` | 3 | 3 | `SHEET_METAL` | `PRODUCTION,PUNCH` | `POSSIBLE` | `POSSIBLE_BUT_NOT_PROVEN` |

## Shared Blocker

Every reviewed project was blocked because v2 accepted only sheet-metal evidence and did not persist page-level evidence for production or punch pages. The existing review artifacts also lack rendered-page, title-block-crop, duplicate, combined-package, and revision-supersession records.

## Data Minimization

This diagnosis intentionally uses neutral file IDs, counts, role hints, and classifier metadata only. It does not include absolute private paths, completed-reference hashes, raw extracted text, rendered pages, crops, dimensions, component names, quantities, layout descriptions, or expected answers.
