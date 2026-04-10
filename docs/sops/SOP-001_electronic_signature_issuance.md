# SOP-001: Electronic Signature Issuance

**Version:** 0.1 (DRAFT) | **Effective:** TODO | **Review due:** TODO

## 1. Purpose
Define the process for issuing electronic signature authority to TRPM-LIMS users per 21 CFR 11.100(a)–(b) and 11.200(a).

## 2. Scope
Applies to all users who will approve, review, or release results when `ENABLE_PART11=True`.

## 3. Procedure

1. **Identity verification** — TODO: HR/manager presents government-issued ID; two witnesses sign verification form.
2. **Account creation** — Admin creates user with unique username; assigns role per RBAC matrix.
3. **Training** — User completes modules TRN-01 + TRN-06 (see training_log.md); trainer signs log.
4. **Initial password** — Admin sets `require_password_change=True`; user changes password on first login.
5. **TOTP MFA setup** — User scans QR code in admin panel and verifies a 6-digit code.
6. **Signature authority granted** — Admin sets user's role to LAB_MANAGER/SUPERVISOR (or as appropriate); documents in this log.
7. **Annual recertification** — TODO: define schedule.

## 4. Records
- Identity verification form (paper/PDF, retained 7 years)
- Training log entry
- AuditLog entry for account creation and role assignment

## 5. References
- 21 CFR 11.100(a)–(b), 11.200(a)
- RBAC matrix (docs/compliance/rbac_matrix.md)
- Training log (docs/compliance/training_log.md)

## 6. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| QA | | | |
| System Owner | | | |
