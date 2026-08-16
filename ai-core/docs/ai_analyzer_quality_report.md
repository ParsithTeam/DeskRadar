# AI Analyzer Quality Report

- Evaluation samples: 64
- Category accuracy: 62/64 (96.9%)
- Intent accuracy: 62/64 (96.9%)
- Urgency exact match: 46/64 (71.9%)
- Urgency near match: 64/64 (100.0%)

## Frequent category errors

- account -> permission: 1
- permission -> account: 1

## Mismatched samples

- EVAL-ACCOUNT-07: category account -> permission; intent account_access_issue -> permission_denied; urgency medium -> medium
- EVAL-PERMISSION-05: category permission -> account; intent permission_denied -> account_access_issue; urgency medium -> medium

## Calibration guidance

Review wrong high-confidence predictions first. Keep category threshold changes category-specific and rerun this set after every rule or model update.
