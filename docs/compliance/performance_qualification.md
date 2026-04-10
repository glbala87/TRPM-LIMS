# Performance Qualification (PQ)

**Document ID:** PQ-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

## 1. Purpose

Confirm that TRPM-LIMS performs reliably under real-world laboratory
conditions with real users, instruments, and sample volumes.

## 2. Entry criteria

- IQ and OQ executed with 0 Critical / 0 Major open defects.
- All users trained and logged in the Training Log.
- Environment is the production environment (not staging).
- Backup + restore drill completed within the last 30 days.

## 3. PQ period

PQ runs for [TODO: 2–4 weeks] in parallel with the incumbent system,
after which results are reconciled.

## 4. Sample volumes

| Workflow | Target daily volume | Actual | Pass/Fail |
|---|---|---|---|
| Patient registrations | TODO | | |
| Molecular samples accessioned | TODO | | |
| Instrument runs | TODO | | |
| Results approved & released | TODO | | |

## 5. Observed defects

| ID | Severity | Description | Status |
|---|---|---|---|
| | | | |

## 6. Performance metrics

| Metric | Target | Actual | Pass/Fail |
|---|---|---|---|
| API p50 latency | < 500 ms | | |
| API p95 latency | < 2 s | | |
| Uptime during PQ | ≥ 99.5% | | |
| Audit log entries generated | > 0 per day | | |

## 7. Go-live decision

- Reconciliation with incumbent system: ☐ match / ☐ discrepancies logged
- Open Critical defects: TODO
- Open Major defects: TODO
- Decision: ☐ Approved for go-live ☐ Hold

## 8. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Process Owner | | | |
| Quality Assurance | | | |
| System Owner | | | |
