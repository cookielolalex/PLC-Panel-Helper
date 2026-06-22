# Evaluation Harness Spec

The harness uses separate generator, output, reviewer, and reference roots.
Generator roots must not contain reference files, target names, hashes,
reviewer findings, scores, expected answers, or reference-only sentinels.

Every run records a run manifest, visible-file manifest, contamination check,
validation results, output hashes, trajectory, grading result, and immutable
artifact manifest.

