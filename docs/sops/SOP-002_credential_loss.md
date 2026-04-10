# SOP-002: Credential Loss / Compromise

**Version:** 0.1 (DRAFT) | **Effective:** TODO | **Review due:** TODO

## 1. Purpose
Define the response procedure when a user's credentials (password, TOTP device) are lost, stolen, or suspected compromised.

## 2. Scope
All TRPM-LIMS users.

## 3. Procedure

1. **User reports** incident to IT admin and supervisor immediately.
2. **Admin verifies** reporter's identity via out-of-band channel (phone call, in-person).
3. **Admin resets password** and sets `require_password_change=True` on the user profile.
4. **Admin revokes TOTP** devices if compromise is suspected (`TOTPDevice.objects.filter(user=...).delete()`).
5. **Admin reviews audit log** (`AuditLog.objects.filter(user=...)`) for any suspicious actions since the suspected compromise window.
6. **Admin documents** findings and remediation in the Change Control Log.
7. **User re-enrolls** — sets new password, re-provisions TOTP per SOP-001 step 5.
8. **If malicious activity is found** — escalate to SOP-003 (Incident Response).

## 4. Records
- AuditLog entries for password reset, device revocation
- Change Control Log entry

## 5. References
- 21 CFR 11.300(c): loss management procedures
- SOP-001, SOP-003

## 6. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| QA | | | |
| System Owner | | | |
