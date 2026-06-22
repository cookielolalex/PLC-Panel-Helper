# Drawing Model Spec

`drawing_model_<工程編號>.json` is the only source for required PDF rendering.
It records project ID, source `job_spec` hash, panels, dimensions, materials,
devices, cutouts, output visibility, provenance, conflicts, unresolved fields,
units, and model version.

Every critical value must be source-supported, derived by an approved rule, or
marked `TBD`, `UNVERIFIED`, `CONFLICT`, or `HUMAN_REVIEW_REQUIRED`.

