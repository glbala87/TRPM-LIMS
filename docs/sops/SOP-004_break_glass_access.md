# SOP-004: Break-Glass Emergency Access

**Version:** 0.1 (DRAFT) | **Effective:** TODO | **Review due:** TODO

## 1. Purpose
Define the procedure for granting emergency superuser access to TRPM-LIMS when normal access channels are unavailable (e.g., AD/LDAP outage, all admins locked out, critical patient-safety need).

## 2. Scope
Only invoked during a declared emergency by an authorized individual (see section 3.1).

## 3. Procedure

### 3.1 Authorization
Break-glass access may only be authorized by:
- Laboratory Director, OR
- IT Security Manager, OR
- On-call supervisor (after hours)

### 3.2 Access
1. Authorized person retrieves the sealed break-glass envelope from TODO: [secure location].
2. Envelope contains: superuser username + initial password.
3. Person logs in, performs the minimum actions required to resolve the emergency.
4. All actions are automatically captured by the `audit` app.

### 3.3 Closure (within 4 hours)
1. Superuser password is changed immediately after use.
2. The sealed envelope is replaced with a new one.
3. Authorized person documents: date/time, emergency justification, actions taken, duration.

### 3.4 Audit review (within 24 hours)
1. IT admin reviews `AuditLog.objects.filter(user__username='break_glass_admin')`.
2. Any actions beyond the declared scope are escalated to SOP-003.
3. Review documented in Change Control Log.

## 4. Records
- Break-glass usage form (retained 7 years)
- AuditLog entries
- Change Control Log entry

## 5. References
- HIPAA §164.312(a)(2)(ii): Emergency access procedure
- 21 CFR 11.10(d): Limiting system access to authorized individuals

## 6. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Laboratory Director | | | |
| IT Security Manager | | | |
| QA | | | |
