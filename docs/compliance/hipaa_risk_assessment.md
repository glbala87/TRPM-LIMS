# HIPAA Security Risk Assessment

**Document ID:** HRA-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

Required by 45 CFR §164.308(a)(1)(ii)(A). Review annually and after any
significant change.

## 1. PHI inventory

| Data element | Stored where | Encrypted at rest? | Encrypted in transit? |
|---|---|---|---|
| Patient name | `lab_management.Patient` | TODO (depends on DB) | TLS via nginx |
| Date of birth / age | `lab_management.Patient.age` | TODO | TLS |
| Contact info | `lab_management.Patient.phone_no` | TODO | TLS |
| Genomic data | `molecular_diagnostics.VariantCall` | TODO | TLS |
| Result reports (PDFs) | `media/` | TODO | TLS |

## 2. Technical safeguards (§164.312)

| Requirement | Control | Status | Gap |
|---|---|---|---|
| Access control (§164.312(a)(1)) | Django auth + JWT | Partial | RBAC matrix needed |
| Unique user identification (§164.312(a)(2)(i)) | Django `User.username` unique | ✅ | — |
| Emergency access (§164.312(a)(2)(ii)) | Break-glass admin account procedure | TODO | Runbook |
| Automatic logoff (§164.312(a)(2)(iii)) | JWT 15-min access token + session timeout | ✅ | — |
| Encryption/decryption (§164.312(a)(2)(iv)) | Postgres TDE or LUKS volume | TODO | Infra |
| Audit controls (§164.312(b)) | `audit` app | ✅ | OQ test needed |
| Integrity (§164.312(c)(1)) | `AuditTrail` snapshots + e-signature integrity hash | ✅ | — |
| Authentication (§164.312(d)) | Django auth; MFA planned | Partial | MFA not yet required |
| Transmission security (§164.312(e)(1)) | TLS via nginx/ALB; HSTS | ✅ | Cert provisioning |

## 3. Administrative safeguards (§164.308)

| Requirement | Status | Doc |
|---|---|---|
| Security management process | TODO | — |
| Workforce security & training | TODO | `training_log.md` |
| Information access management | TODO | RBAC matrix |
| Security awareness & training | TODO | `training_log.md` |
| Contingency plan | TODO | DR runbook |
| Business associate agreements | TODO | Legal |

## 4. Physical safeguards (§164.310)

| Requirement | Status | Doc |
|---|---|---|
| Facility access controls | TODO | Facilities SOP |
| Workstation use & security | TODO | IT policy |
| Device & media controls | TODO | IT policy |

## 5. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Security Officer | | | |
| Privacy Officer | | | |
| System Owner | | | |
