# TRPM-LIMS Compliance Documentation

This folder contains templates for the regulatory documents that accompany
a validated LIMS deployment. These are **templates only** — each document
must be filled in, reviewed, and approved by the responsible parties before
the LIMS can be used for regulated work (clinical, CLIA, CAP, Part 11,
HIPAA, etc.).

## Scope decision

TRPM-LIMS supports two deployment modes via the `ENABLE_PART11` and
`ENABLE_HIPAA_MODE` environment flags (see `.env.example`):

| Mode | `ENABLE_PART11` | `ENABLE_HIPAA_MODE` | Intended use |
|---|---|---|---|
| Research | `False` | `False` | De-identified data, no patient care decisions |
| Research → clinical (this deployment) | `False` today, `True` before go-live | `False` today | Same codebase; flip flags + complete this documentation set before clinical go-live |
| Clinical | `True` | `True` | Full 21 CFR Part 11 + HIPAA enforcement |

This deployment is currently configured as **research now, clinical later**.
The ElectronicSignature model is present and functional, but signatures
are not *enforced* on result-release workflows until `ENABLE_PART11=True`.

## Document inventory

Complete each document below before enabling clinical mode.

| # | Document | Template | Status |
|---|---|---|---|
| 1 | Validation Master Plan (VMP) | [`validation_master_plan.md`](./validation_master_plan.md) | TODO |
| 2 | User Requirements Specification (URS) | [`user_requirements_specification.md`](./user_requirements_specification.md) | TODO |
| 3 | Installation Qualification (IQ) | [`installation_qualification.md`](./installation_qualification.md) | TODO |
| 4 | Operational Qualification (OQ) | [`operational_qualification.md`](./operational_qualification.md) | TODO |
| 5 | Performance Qualification (PQ) | [`performance_qualification.md`](./performance_qualification.md) | TODO |
| 6 | Requirements Traceability Matrix | [`traceability_matrix.md`](./traceability_matrix.md) | TODO |
| 7 | Training Log | [`training_log.md`](./training_log.md) | TODO |
| 8 | Change Control Log | [`change_control_log.md`](./change_control_log.md) | TODO |
| 9 | Part 11 Assessment | [`part11_assessment.md`](./part11_assessment.md) | TODO |
| 10 | HIPAA Security Risk Assessment | [`hipaa_risk_assessment.md`](./hipaa_risk_assessment.md) | TODO |

## Cross-reference: regulations → controls

- **21 CFR Part 11.10(a)** — System validation → VMP, IQ, OQ, PQ
- **21 CFR Part 11.10(e)** — Audit trails → `audit` app (AuditLog, AuditTrail)
- **21 CFR Part 11.50** — Signature manifestations → `compliance.ElectronicSignature.meaning`
- **21 CFR Part 11.70** — Signature/record linking → immutable ElectronicSignature + `record_snapshot`
- **21 CFR Part 11.100(b)** — Unique individual IDs → `users` app + RBAC
- **21 CFR Part 11.200(a)** — Non-biometric signings require two components → re-authentication before calling `ElectronicSignature.sign()`
- **21 CFR Part 11.300** — Controls for identification codes/passwords → Django password validators + session timeout
- **HIPAA §164.312(a)(1)** — Access control → RBAC + `ENABLE_HIPAA_MODE`
- **HIPAA §164.312(b)** — Audit controls → `audit` app
- **HIPAA §164.312(c)(1)** — Integrity → ElectronicSignature integrity hash + audit trail snapshots
- **HIPAA §164.312(e)(1)** — Transmission security → HSTS + TLS termination (see `nginx.conf`, `settings.py` security block)
