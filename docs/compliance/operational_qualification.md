# Operational Qualification (OQ)

**Document ID:** OQ-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

## 1. Purpose

Confirm that TRPM-LIMS functions as intended for each critical workflow,
independent of real laboratory data.

## 2. Test case template

Copy and fill in one block per test case. Each OQ test case must map to
one or more URS requirements in the Traceability Matrix.

```
Test Case ID: OQ-XXX
Linked URS:   URS-XXX
Title:        <short description>
Preconditions:
  - <setup step>
Test steps:
  1. <action>
  2. <action>
Expected result:
  - <observable outcome>
Actual result:
  - <filled in at execution>
Pass/Fail:
  -
Executed by / date:
  -
```

## 3. Critical workflows to test (minimum)

| ID | Workflow | Module |
|---|---|---|
| OQ-001 | User creation, login, password change, account lockout | `users` |
| OQ-002 | Role assignment and permission enforcement | `users` |
| OQ-003 | Patient registration with barcode generation | `lab_management` |
| OQ-004 | Lab order creation and sample receipt | `lab_management` |
| OQ-005 | Molecular sample accessioning | `molecular_diagnostics` |
| OQ-006 | Instrument run creation and QC record | `instruments`, `molecular_diagnostics` |
| OQ-007 | Result entry, review, approval (with e-signature in clinical mode) | `molecular_diagnostics`, `compliance` |
| OQ-008 | Electronic signature immutability | `compliance` |
| OQ-009 | Audit trail records CREATE/UPDATE/DELETE with correct user and timestamp | `audit` |
| OQ-010 | Patient consent tracking and revocation | `compliance` |
| OQ-011 | Storage unit temperature alarm | `sensors`, `storage` |
| OQ-012 | Reagent lot tracking and expiration alerting | `reagents` |
| OQ-013 | PDF report generation for an approved result | `molecular_diagnostics` |
| OQ-014 | HL7/FHIR outbound message for a released result | `data_exchange` |
| OQ-015 | Backup restore into a scratch database | ops |

## 4. Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| Executor | | | |
| QA Reviewer | | | |
| System Owner | | | |
