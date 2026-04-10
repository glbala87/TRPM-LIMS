# Change Control Log

**Document ID:** CCL-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

Every code change that affects a validated workflow must be logged here,
risk-assessed, tested, and approved by QA before deployment.

## Change control procedure

1. Developer opens a change request describing the change and its impact.
2. Impact on validated workflows is assessed: none / minor / major.
3. If minor or major, an updated OQ/PQ test plan is written.
4. Change is implemented in a feature branch with tests.
5. CI (`.github/workflows/ci.yml`) must pass.
6. Peer review.
7. QA reviews updated test plan and signs off.
8. Deployment via change window; deployment evidence (git SHA, timestamp,
   deployer) logged below.
9. Post-deployment smoke test.

## Log

| Date | Change ID | Description | Git SHA | Impact | OQ re-run? | Approved by | Deployed by |
|---|---|---|---|---|---|---|---|
| | | | | | | | |
| | | | | | | | |
