# User Requirements Specification (URS)

**Document ID:** URS-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

> Each requirement must have a unique ID (e.g., `URS-001`) and be
> traceable through the Requirements Traceability Matrix to IQ/OQ/PQ
> test cases.

## 1. Business drivers

TODO — describe the business need.

## 2. Functional requirements

| ID | Requirement | Priority | Module |
|---|---|---|---|
| URS-001 | The system shall uniquely identify each user with an individual account (no shared logins). | MUST | `users` |
| URS-002 | The system shall log every create/update/delete of patient and result data with timestamp and user. | MUST | `audit` |
| URS-003 | The system shall require electronic signature on result approval when clinical mode is active. | MUST | `compliance` |
| URS-004 | The system shall prevent modification of electronic signatures after creation. | MUST | `compliance` |
| URS-005 | The system shall enforce TLS 1.2+ for all external connections. | MUST | infra |
| URS-006 | The system shall back up the database at least every 24 hours. | MUST | ops |
| URS-007 | TODO | | |

## 3. Non-functional requirements

| ID | Requirement | Target |
|---|---|---|
| NFR-001 | Availability | 99.5% |
| NFR-002 | API median latency | < 500 ms |
| NFR-003 | Max concurrent users | TODO |
| NFR-004 | Audit log retention | 7 years (clinical) / 3 years (research) |
| NFR-005 | TODO | |

## 4. Regulatory requirements

| ID | Regulation | Control |
|---|---|---|
| REG-001 | 21 CFR 11.10(e) | Immutable audit trail — `audit.AuditLog` + `AuditTrail` |
| REG-002 | 21 CFR 11.50 | Signature meaning captured — `ElectronicSignature.meaning` |
| REG-003 | 21 CFR 11.70 | Signature/record binding — `ElectronicSignature.record_snapshot` |
| REG-004 | HIPAA §164.312(b) | Audit controls — `audit` app |
| REG-005 | TODO | |

## 5. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Process Owner | | | |
| Quality Assurance | | | |
