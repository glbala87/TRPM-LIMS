# 21 CFR Part 11 Assessment

**Document ID:** P11-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

Assessment of TRPM-LIMS against each applicable section of 21 CFR Part 11.

| Section | Requirement | TRPM-LIMS control | Status | Evidence / gap |
|---|---|---|---|---|
| 11.10(a) | System validation | IQ/OQ/PQ executed | TODO | IQ/OQ/PQ docs |
| 11.10(b) | Ability to generate human-readable copies | PDF report generation (`weasyprint`) | TODO | PDF export OQ test |
| 11.10(c) | Protection of records for the retention period | Postgres + backup + audit trail | TODO | Backup runbook |
| 11.10(d) | System access limited to authorized individuals | Django auth + RBAC + JWT | Partial | Need RBAC matrix doc |
| 11.10(e) | Secure, computer-generated audit trail | `audit.AuditLog` + `audit.AuditTrail`; post_save signals on all business models | TODO | OQ-009 |
| 11.10(f) | Operational system checks enforcing sequencing | Workflow step transitions (`molecular_diagnostics.WorkflowDefinition`) | Partial | Need OQ test |
| 11.10(g) | Authority checks | Role-based permissions | TODO | RBAC matrix |
| 11.10(h) | Device (terminal) checks (if required) | N/A — web app, no fixed terminals | N/A | — |
| 11.10(i) | Training records | `docs/compliance/training_log.md` | TODO | Training log |
| 11.10(j) | Written policies on signatures | TODO | TODO | Policy doc |
| 11.10(k) | Document change controls | `docs/compliance/change_control_log.md` | TODO | Log |
| 11.30 | Controls for open systems | TLS + auth; no open-system exposure | TODO | Network diagram |
| 11.50(a) | Signature manifestations include name, date/time, meaning | `ElectronicSignature` captures all three | ✅ | Model |
| 11.50(b) | Signed records include same info | `ElectronicSignature.record_snapshot` + linked record | ✅ | Model |
| 11.70 | Signature-to-record linking | Immutable `ElectronicSignature` + snapshot + integrity hash | ✅ | Model tests |
| 11.100(a) | Each signature unique to one individual | Django `User` uniqueness + no shared accounts policy | TODO | Policy |
| 11.100(b) | Verify identity before issuance | Identity verification procedure | TODO | Onboarding doc |
| 11.200(a)(1) | Non-biometric signatures use two identification components | Re-auth with username + password before signing | Partial | Need OQ test of sign-flow re-auth |
| 11.200(a)(2) | Distinct first-signing vs subsequent-signing controls | TODO | TODO | |
| 11.200(a)(3) | Only genuine owner can use | Session + password policy | TODO | |
| 11.300(a) | Maintain uniqueness of ID codes | Django unique username | ✅ | Model |
| 11.300(b) | Periodic password aging | TODO — not yet enforced | Gap | Need to implement password aging |
| 11.300(c) | Loss management procedures | TODO | TODO | |
| 11.300(d) | Use of transaction safeguards to prevent unauthorized use | JWT short TTL + refresh rotation + blacklist | ✅ | settings.py `SIMPLE_JWT` |
| 11.300(e) | Initial and periodic testing of devices | TODO | TODO | |

## Identified gaps

1. **Password aging** — Django does not enforce aging out of the box;
   we'd need `django-password-validators` or similar before going
   clinical.
2. **Formal policies** — written SOPs for signature issuance, loss of
   credentials, and device control must exist as separate documents.
3. **RBAC matrix** — the `users` app has a role model, but a formal RBAC
   matrix mapping roles → permissions → screens/actions has not been
   written.

## Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| QA | | | |
| System Owner | | | |
