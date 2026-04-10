# SOP-003: Security Incident Response

**Version:** 0.1 (DRAFT) | **Effective:** TODO | **Review due:** TODO

## 1. Purpose
Define the steps for detecting, containing, investigating, and remediating security incidents affecting TRPM-LIMS and the data it holds.

## 2. Scope
Any event that threatens the confidentiality, integrity, or availability of TRPM-LIMS data, including but not limited to: unauthorized access, data breach, malware, ransomware, denial of service, insider threat.

## 3. Procedure

### 3.1 Detection
- Sentry alerts, audit log anomalies, user reports, external notification.

### 3.2 Containment (within 1 hour of detection)
1. Disable affected user account(s).
2. Revoke active JWT tokens (add to SimpleJWT blacklist).
3. If infrastructure is compromised, isolate the affected container/VM.

### 3.3 Investigation
1. Preserve audit logs (`AuditLog`, `AuditTrail`), web server access logs, Sentry events.
2. Determine scope: what data was accessed/modified, which users affected.
3. Check ElectronicSignature integrity (`verify_integrity()` on recent signatures).

### 3.4 Notification (within 24 hours)
- Notify TODO: [privacy officer, legal, affected patients, HHS if HIPAA breach > 500 records].

### 3.5 Remediation
1. Patch vulnerability or revoke compromised credentials.
2. Restore from backup if data integrity is compromised (use `scripts/restore_drill.sh`).
3. Document all actions in Change Control Log.

### 3.6 Post-mortem (within 7 days)
1. Write incident report: timeline, root cause, impact, remediation, lessons learned.
2. Update RBAC, firewall rules, training materials as needed.
3. Review and revise this SOP if gaps were found.

## 4. Records
- Incident report (retained 7 years)
- Change Control Log entries
- HHS breach notification (if applicable)

## 5. References
- HIPAA §164.308(a)(6): Security incident procedures
- HIPAA §164.404–408: Breach notification
- SOP-002

## 6. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Security Officer | | | |
| QA | | | |
| System Owner | | | |
