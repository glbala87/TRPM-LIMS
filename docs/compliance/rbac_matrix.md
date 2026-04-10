# RBAC Matrix — TRPM-LIMS

**Document ID:** RBAC-TRPM-LIMS-001
**Version:** 0.1 (DRAFT)

## Role definitions

| Code | Display name | Scope |
|---|---|---|
| ADMIN | Administrator | Full system access; user management, settings, audit review |
| LAB_MANAGER | Lab Manager | Manage lab operations, approve results, reagent ordering |
| SUPERVISOR | Supervisor | Oversee technicians, review results, QC sign-off |
| TECHNICIAN | Technician | Perform tests, enter results, reagent usage |
| READER | Reader | View-only access to results and reports |
| PHYSICIAN | Physician | View patient results, request tests |

## Permission matrix

**C** = Create, **R** = Read, **U** = Update, **D** = Delete, **A** = Approve/Sign, **—** = No access

| Module / Resource | ADMIN | LAB_MANAGER | SUPERVISOR | TECHNICIAN | READER | PHYSICIAN |
|---|---|---|---|---|---|---|
| **lab_management** | | | | | | |
| Patient | CRUD | CRUD | CRU | CRU | R | R |
| LabOrder | CRUD | CRUD | CRU | CR | R | CR |
| TestResult | CRUD | CRUD | CRU | CRU | R | R |
| **molecular_diagnostics** | | | | | | |
| MolecularSample | CRUD | CRUD | CRU | CRU | R | — |
| MolecularResult | CRUD | CRUA | CRUA | CRU | R | R |
| VariantCall | CRUD | CRU | CRU | CRU | R | R |
| InstrumentRun | CRUD | CRUD | CRU | CRU | R | — |
| **audit** | | | | | | |
| AuditLog | R | R | R | — | — | — |
| AuditTrail | R | R | R | — | — | — |
| **compliance** | | | | | | |
| ConsentProtocol | CRUD | CRU | R | R | R | R |
| PatientConsent | CRUD | CRU | CRU | CRU | R | R |
| ElectronicSignature | R | RA | RA | — | — | — |
| **equipment** | | | | | | |
| Instrument | CRUD | CRUD | CRU | R | R | — |
| MaintenanceRecord | CRUD | CRUD | CRU | CRU | R | — |
| **reagents** | | | | | | |
| Reagent | CRUD | CRUD | CRU | RU (usage) | R | — |
| MolecularReagent | CRUD | CRUD | CRU | RU (usage) | R | — |
| **storage** | | | | | | |
| StorageUnit | CRUD | CRUD | CRU | R | R | — |
| StoragePosition | CRUD | CRU | CRU | CRU | R | — |
| **billing** | | | | | | |
| PriceList | CRUD | CRU | R | — | — | — |
| Invoice | CRUD | CRU | R | — | — | R |
| **instruments** | | | | | | |
| InstrumentConnection | CRUD | CRU | R | R | — | — |
| **users** | | | | | | |
| User management | CRUD | R | R | — | — | — |
| Role assignment | CRUD | R | — | — | — | — |

## Notes

1. "A" (Approve/Sign) requires an ElectronicSignature when `ENABLE_PART11=True`.
2. LAB_MANAGER and SUPERVISOR can approve results; TECHNICIAN can only enter.
3. READER and PHYSICIAN have no write access anywhere.
4. Audit logs are immutable — even ADMIN cannot modify/delete.

## Approval

| Role | Name | Signature | Date |
|---|---|---|---|
| System Owner | | | |
| Quality Assurance | | | |
