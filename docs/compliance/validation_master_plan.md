# Validation Master Plan (VMP)

**Document ID:** VMP-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)
**Effective date:** TODO
**Approval status:** DRAFT — not yet approved

> This is a template. Fill in every `TODO` and obtain signatures before
> using TRPM-LIMS for regulated work.

## 1. Purpose

Define the validation strategy, scope, and responsibilities for TRPM-LIMS
at [TODO: lab name].

## 2. Scope

- In scope: TRPM-LIMS application, all 26 modules (list in Appendix A),
  production deployment on [TODO: infrastructure], integrations with
  [TODO: HL7/FHIR endpoints, instrument vendors].
- Out of scope: third-party instruments' internal firmware, cloud provider
  underlying infrastructure (covered by the provider's SOC2/HITRUST).

## 3. System classification

- GAMP 5 category: [TODO — likely Category 4 (configured) or 5 (custom)]
- Patient-impact risk: [TODO — High / Medium / Low]
- Regulatory drivers: [TODO — CLIA, CAP, 21 CFR Part 11, HIPAA, GDPR, etc.]

## 4. Roles & responsibilities

| Role | Name | Responsibility |
|---|---|---|
| System Owner | TODO | Overall accountability |
| Process Owner | TODO | Day-to-day lab operations |
| Quality Assurance | TODO | Approves validation deliverables |
| IT / Infrastructure | TODO | Server, backup, DR |
| Validation Lead | TODO | Authors IQ/OQ/PQ, runs tests |
| Developer(s) | TODO | Implements changes under change control |

## 5. Deliverables

See `README.md` document inventory. Each deliverable must be written,
reviewed, executed, and approved in the order listed.

## 6. Validation lifecycle

1. URS approved
2. VMP approved (this document)
3. System installed per IQ; IQ executed and approved
4. System functionality tested per OQ; OQ executed and approved
5. Intended use tested per PQ; PQ executed and approved
6. Traceability matrix populated
7. Training completed and logged
8. Go-live authorization signed
9. Change control active; periodic review annually

## 7. Acceptance criteria for go-live

- All IQ/OQ/PQ test cases executed with zero Critical or Major defects
  open.
- Training log shows 100% coverage of users with their respective roles.
- `ENABLE_PART11=True` and `ENABLE_HIPAA_MODE=True` set in production env.
- `python manage.py check --deploy` returns 0 warnings.
- Backup + restore drill completed within the last 30 days.
- Disaster recovery runbook reviewed and tested.

## 8. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| System Owner | | | |
| Quality Assurance | | | |
| Process Owner | | | |
