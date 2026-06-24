# Sheetmetal V1 Qualification Policy

Status: ACCEPTED FOUNDATION V1.

`SHEETMETAL_ALLOWED_EVAL` is a new qualification class. No project is
automatically grandfathered from `LEGACY_THREE_OUTPUT_ALLOWED_EVAL`.

## Required Gates

A project may become `SHEETMETAL_ALLOWED_EVAL` only when:

1. a complete effective sheet-metal reference package exists;
2. project identity is confirmed;
3. revision and supersession are resolved;
4. chronologically prior project sources exist;
5. completed sheet-metal, production-control, and punch outputs are excluded
   from generator input;
6. post-design filled or allocation files are excluded unless proven pre-design;
7. source-role and chronology review passes;
8. deterministic source guard passes;
9. approved source-review quorum passes;
10. a sanitized bundle is built;
11. bundle hashes, worksheet fingerprints, links, formulas, macros, and hidden
   sheet rules pass;
12. reference content remains isolated from the generator;
13. source coverage is sufficient for component-register and panel-assignment
   scoring.

The new first baseline must not start in the migration task.

## Module-Level Evaluation

Sheetmetal-v1 reports performance separately for:

- source extraction;
- component normalization;
- panel assignment;
- relationship graph;
- accessory inference;
- panel sizing;
- component placement;
- drawing quality;
- human utility.

The historical 42-point / 38-percent three-output baseline remains preserved
evidence and must not be directly compared to the new modular baseline.

