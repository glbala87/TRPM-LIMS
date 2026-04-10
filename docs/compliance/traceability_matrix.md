# Requirements Traceability Matrix

**Document ID:** RTM-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

Every URS requirement must trace forward to at least one test case, and
every test case must trace back to a requirement. Maintain this matrix as
URS and test cases evolve.

| URS ID | Requirement (short) | Code / Module | IQ Test | OQ Test | PQ Evidence | Status |
|---|---|---|---|---|---|---|
| URS-001 | Unique user accounts | `users` | IQ-4 | OQ-001 | PQ-log | TODO |
| URS-002 | Audit trail on CRUD | `audit.AuditLog` / `AuditTrail` | — | OQ-009 | PQ-log | TODO |
| URS-003 | E-signature on approval (clinical) | `compliance.ElectronicSignature` | IQ-3 | OQ-007 | PQ-log | TODO |
| URS-004 | E-signature immutability | `compliance.ElectronicSignature.save/delete` | — | OQ-008 | — | TODO |
| URS-005 | TLS 1.2+ | nginx + Django `SECURE_*` | IQ-2 | — | — | TODO |
| URS-006 | Nightly DB backup | infra runbook | IQ-6 | — | PQ-log | TODO |
| REG-001 | 21 CFR 11.10(e) audit trail | `audit` app | — | OQ-009 | — | TODO |
| REG-002 | 21 CFR 11.50 signature meaning | `ElectronicSignature.meaning` | — | OQ-007 | — | TODO |
| REG-003 | 21 CFR 11.70 record binding | `ElectronicSignature.record_snapshot` | — | OQ-008 | — | TODO |
| REG-004 | HIPAA §164.312(b) audit controls | `audit` app | — | OQ-009 | — | TODO |
