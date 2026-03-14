# TRPM-LIMS Complete Standard Operating Procedures Manual

**Document Number:** SOP-TRPM-MASTER-001
**Version:** 2.0
**Effective Date:** 2026-02-28
**Review Date:** 2027-02-28
**Classification:** Controlled Document

---

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                              TRPM-LIMS                                      │
│                                                                             │
│            COMPREHENSIVE STANDARD OPERATING PROCEDURES MANUAL               │
│                                                                             │
│                     Laboratory Information Management System                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Document Control Information

| Field | Value |
|-------|-------|
| **Document Title** | TRPM-LIMS Complete SOP Manual |
| **Document Number** | SOP-TRPM-MASTER-001 |
| **Version** | 2.0 |
| **Effective Date** | 2026-02-28 |
| **Review Date** | 2027-02-28 |
| **Document Owner** | Laboratory Director |
| **Classification** | Internal - Controlled |
| **Supersedes** | SOP-TRPM-001 v1.0, MET-SOP-001 v1.0 |

---

## Approval Signatures

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Author** | _________________ | _________________ | __________ |
| **Technical Reviewer** | _________________ | _________________ | __________ |
| **Quality Manager** | _________________ | _________________ | __________ |
| **Laboratory Director** | _________________ | _________________ | __________ |

---

## Revision History

| Version | Date | Author | Summary of Changes | Sections Affected |
|---------|------|--------|-------------------|-------------------|
| 1.0 | 2026-02-16 | TRPM-LIMS Team | Initial SOP release | All |
| 1.1 | 2026-02-28 | TRPM-LIMS Team | Added Documentation Methodology | Part I |
| 2.0 | 2026-02-28 | TRPM-LIMS Team | Consolidated into complete manual | All |

---

## Table of Contents

### PART I: DOCUMENT GOVERNANCE & METHODOLOGY
1. [Introduction and Regulatory Foundation](#1-introduction-and-regulatory-foundation)
2. [Document Governance Framework](#2-document-governance-framework)
3. [SOP Taxonomy and Classification](#3-sop-taxonomy-and-classification)
4. [Document Structure Standards](#4-document-structure-standards)
5. [Writing Guidelines](#5-writing-guidelines)
6. [Document Lifecycle Management](#6-document-lifecycle-management)
7. [Version Control Methodology](#7-version-control-methodology)
8. [Review and Approval Workflow](#8-review-and-approval-workflow)

### PART II: SYSTEM OVERVIEW & ACCESS
9. [System Overview](#9-system-overview)
10. [User Roles and Responsibilities](#10-user-roles-and-responsibilities)
11. [System Access and Security](#11-system-access-and-security)
12. [Initial Setup Procedures](#12-initial-setup-procedures)

### PART III: CORE LABORATORY OPERATIONS
13. [Patient Management](#13-patient-management)
14. [Lab Order Management](#14-lab-order-management)
15. [Reagent Inventory Management](#15-reagent-inventory-management)

### PART IV: MOLECULAR DIAGNOSTICS
16. [Molecular Diagnostics Workflow](#16-molecular-diagnostics-workflow)
17. [PCR and NGS Procedures](#17-pcr-and-ngs-procedures)
18. [Result Entry and Reporting](#18-result-entry-and-reporting)

### PART V: SPECIALIZED MODULES
19. [Microbiology Module](#19-microbiology-module)
20. [Pathology Module](#20-pathology-module)

### PART VI: QUALITY MANAGEMENT
21. [Quality Control Procedures](#21-quality-control-procedures)
22. [Quality Management System (QMS)](#22-quality-management-system-qms)
23. [Compliance and Consent Management](#23-compliance-and-consent-management)

### PART VII: INFRASTRUCTURE MANAGEMENT
24. [Equipment Management](#24-equipment-management)
25. [Sample Storage Management](#25-sample-storage-management)

### PART VIII: SYSTEM ADMINISTRATION
26. [Audit Trail and Logging](#26-audit-trail-and-logging)
27. [Reporting and Analytics](#27-reporting-and-analytics)
28. [Data Backup and Recovery](#28-data-backup-and-recovery)
29. [Change Control](#29-change-control)

### PART IX: APPENDICES
30. [Templates and Forms](#30-templates-and-forms)
31. [Reference Tables](#31-reference-tables)
32. [Glossary and Abbreviations](#32-glossary-and-abbreviations)

---

# PART I: DOCUMENT GOVERNANCE & METHODOLOGY

---

## 1. Introduction and Regulatory Foundation

### 1.1 Purpose

This comprehensive Standard Operating Procedures (SOP) Manual provides:
- Complete guidelines for operating TRPM-LIMS
- Standardized framework for developing and maintaining SOPs
- Compliance requirements for regulatory standards
- Consistent, efficient laboratory operations across all modules

### 1.2 Scope

This manual applies to:
- All laboratory personnel using TRPM-LIMS
- IT administrators responsible for system maintenance
- Quality assurance personnel
- Laboratory directors and managers
- Document authors and reviewers

**Covered Modules:**
- Core Laboratory Management
- Molecular Diagnostics
- Microbiology
- Pathology
- Equipment Management
- Sample Storage
- Quality Management System
- Analytics and Reporting
- Compliance Management

### 1.3 Regulatory Foundation

This manual aligns with:

| Standard | Description |
|----------|-------------|
| **ISO 15189:2022** | Medical Laboratories Requirements |
| **ISO 17025:2017** | Testing and Calibration Laboratories |
| **CAP** | College of American Pathologists Accreditation Standards |
| **CLIA** | Clinical Laboratory Improvement Amendments (42 CFR Part 493) |
| **21 CFR Part 11** | Electronic Records; Electronic Signatures |
| **FDA GxP** | Good Practice Regulations |
| **HIPAA** | Privacy and Security Rules |

### 1.4 Definitions

| Term | Definition |
|------|------------|
| **SOP** | Standard Operating Procedure - detailed written instructions for routine operations |
| **Work Instruction** | Step-by-step procedure for specific tasks |
| **Policy** | High-level statement defining organizational intent |
| **Protocol** | Scientific procedure for testing or analysis |
| **Guideline** | Recommended practices (non-mandatory) |
| **Document Owner** | Person responsible for document content accuracy |
| **Document Controller** | Person managing document lifecycle |
| **LIMS** | Laboratory Information Management System |

---

## 2. Document Governance Framework

### 2.1 Governance Structure

```
┌─────────────────────────────────────────────────────┐
│              DOCUMENT GOVERNANCE HIERARCHY          │
├─────────────────────────────────────────────────────┤
│  Level 1: POLICIES                                  │
│  └── Strategic direction, organizational intent    │
├─────────────────────────────────────────────────────┤
│  Level 2: STANDARD OPERATING PROCEDURES            │
│  └── Departmental processes, workflows             │
├─────────────────────────────────────────────────────┤
│  Level 3: WORK INSTRUCTIONS                         │
│  └── Step-by-step task procedures                  │
├─────────────────────────────────────────────────────┤
│  Level 4: FORMS, CHECKLISTS, TEMPLATES             │
│  └── Supporting documentation                       │
└─────────────────────────────────────────────────────┘
```

### 2.2 Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Laboratory Director** | Final approval authority, policy decisions, QC oversight, compliance |
| **Quality Manager** | QMS oversight, document control, compliance verification |
| **Laboratory Manager** | Staff supervision, workflow management, section oversight |
| **Document Owner** | Content accuracy, periodic review, updates |
| **Technical Reviewer** | Technical accuracy verification |
| **Quality Reviewer** | Compliance and format verification |
| **Document Controller** | Version management, distribution, archiving |
| **End Users** | Compliance with procedures, feedback |

### 2.3 Document Control Authority Matrix

| Document Type | Author | Technical Review | Quality Review | Final Approval |
|---------------|--------|------------------|----------------|----------------|
| Policy | Lab Director | N/A | Quality Manager | Lab Director |
| SOP | Subject Expert | Supervisor | Quality Manager | Lab Director |
| Work Instruction | Technician | Supervisor | Quality Manager | Lab Manager |
| Protocol | Scientist | Lead Scientist | Quality Manager | Lab Director |
| Form/Template | Process Owner | Supervisor | Quality Manager | Lab Manager |

---

## 3. SOP Taxonomy and Classification

### 3.1 Document Numbering System

**Format:** `[TYPE]-[MODULE]-[SEQUENCE]-[VERSION]`

**Examples:**
```
SOP-LAB-001-v1.0      Laboratory Management SOP #1, Version 1.0
SOP-MOL-015-v2.1      Molecular Diagnostics SOP #15, Version 2.1
WI-MIC-003-v1.2       Microbiology Work Instruction #3, Version 1.2
POL-QMS-002-v1.0      QMS Policy #2, Version 1.0
PRO-NGS-001-v3.0      NGS Protocol #1, Version 3.0
```

### 3.2 Type Codes

| Code | Document Type |
|------|--------------|
| POL | Policy |
| SOP | Standard Operating Procedure |
| WI | Work Instruction |
| PRO | Protocol |
| GUI | Guideline |
| FRM | Form |
| CHK | Checklist |
| TMP | Template |
| MAN | Manual |
| TRN | Training Material |

### 3.3 Module Codes

| Code | Module |
|------|--------|
| LAB | Core Lab Management |
| MOL | Molecular Diagnostics |
| MIC | Microbiology |
| PAT | Pathology |
| QMS | Quality Management |
| EQP | Equipment Management |
| STO | Sample Storage |
| REA | Reagent Management |
| ANA | Analytics & Reporting |
| USR | User Management |
| SEC | Security & Access |
| DAT | Data Management |
| COM | Compliance |
| BIO | Bioinformatics |
| PGX | Pharmacogenomics |

### 3.4 Document Categories

| Category | Description | Review Frequency |
|----------|-------------|------------------|
| **Administrative** | Management and organizational SOPs | Annual |
| **Pre-Analytical** | Sample collection, handling, reception | Annual |
| **Analytical** | Testing procedures, methods | Annual |
| **Post-Analytical** | Reporting, interpretation, release | Annual |
| **Quality Control** | QC procedures, validation | Annual |
| **Equipment** | Instrument operation, maintenance | Annual |
| **Safety** | Biosafety, chemical safety, emergency | Annual |
| **Training** | Competency, onboarding, continuing education | As needed |
| **IT/Technical** | System administration, data management | Annual |

### 3.5 Criticality Classification

| Level | Description | Review Cycle | Approval Level |
|-------|-------------|--------------|----------------|
| **Critical** | Patient safety, regulatory compliance | 12 months | Lab Director |
| **Major** | Quality impact, significant processes | 12 months | Lab Manager |
| **Standard** | Routine operations | 18 months | Supervisor |
| **Minor** | Administrative, supporting | 24 months | Process Owner |

---

## 4. Document Structure Standards

### 4.1 Standard SOP Template Structure

Every SOP must contain the following sections:

```
1. HEADER BLOCK
   ├── Document Title
   ├── Document Number
   ├── Version Number
   ├── Effective Date
   ├── Review Date
   ├── Page Numbers (Page X of Y)
   └── Department/Module

2. APPROVAL SIGNATURES
   ├── Author (Name, Signature, Date)
   ├── Reviewer (Name, Signature, Date)
   └── Approver (Name, Signature, Date)

3. REVISION HISTORY
   └── Table: Version | Date | Author | Changes

4. TABLE OF CONTENTS
   └── Numbered sections with page references

5. PURPOSE
   └── Clear statement of why this SOP exists

6. SCOPE
   └── What/who this SOP applies to

7. DEFINITIONS
   └── Technical terms and abbreviations

8. RESPONSIBILITIES
   └── Roles and their obligations

9. REFERENCES
   └── Related documents, standards, regulations

10. MATERIALS/EQUIPMENT
    └── Required resources (if applicable)

11. SAFETY PRECAUTIONS
    └── Hazards and protective measures (if applicable)

12. PROCEDURE
    └── Numbered, step-by-step instructions

13. QUALITY CONTROL
    └── QC requirements and acceptance criteria

14. DOCUMENTATION/RECORDS
    └── What records to maintain

15. APPENDICES
    └── Supporting forms, flowcharts, examples
```

### 4.2 Header Block Specifications

```
┌─────────────────────────────────────────────────────────────────┐
│ [ORGANIZATION LOGO]        STANDARD OPERATING PROCEDURE        │
├─────────────────────────────────────────────────────────────────┤
│ Title: [Full Document Title]                                    │
│ Document Number: SOP-MOL-001        Version: 2.0               │
│ Department: Molecular Diagnostics   Page: 1 of 15              │
│ Effective Date: 2026-02-28          Review Date: 2027-02-28    │
├─────────────────────────────────────────────────────────────────┤
│ Supersedes: SOP-MOL-001-v1.5 dated 2025-08-15                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.3 Procedure Section Formatting

**Step Numbering Convention:**
```
1.0 MAJOR PROCEDURE SECTION
    1.1 Sub-procedure
        1.1.1 Detailed step
        1.1.2 Detailed step
            a. Sub-step
            b. Sub-step
    1.2 Sub-procedure

2.0 NEXT MAJOR SECTION
    2.1 Sub-procedure
```

**Action Verb Standards:**

| Category | Verbs |
|----------|-------|
| **Physical Actions** | Collect, Transfer, Mix, Centrifuge, Pipette, Label |
| **System Actions** | Navigate, Click, Select, Enter, Save, Submit |
| **Verification** | Verify, Confirm, Ensure, Check, Review |
| **Documentation** | Record, Document, Note, Sign, Date |
| **Communication** | Notify, Report, Escalate, Contact |

---

## 5. Writing Guidelines

### 5.1 Language Standards

| Principle | Guideline | Example |
|-----------|-----------|---------|
| **Clarity** | Use simple, direct language | "Add 100 µL of buffer" not "The addition of 100 µL buffer is required" |
| **Precision** | Be specific with quantities and times | "Incubate for 30±2 minutes at 37°C" not "Incubate for approximately 30 minutes" |
| **Consistency** | Use same terms throughout | Always "sample" not sometimes "specimen" |
| **Active Voice** | Subject performs action | "The technician processes the sample" not "The sample is processed" |
| **Imperative Mood** | Direct commands | "Verify patient identity" not "Patient identity should be verified" |

### 5.2 Technical Writing Rules

**Rule 1: One Action Per Step**
- Bad: "Centrifuge the sample at 3000 rpm for 10 minutes, then transfer supernatant to a new tube and label appropriately"
- Good:
  - Step 1: Centrifuge the sample at 3000 rpm for 10 minutes
  - Step 2: Transfer supernatant to a new tube
  - Step 3: Label the tube with [required information]

**Rule 2: Include Decision Points**
```
5.3 Review QC Results
    5.3.1 If QC passes (within ±2 SD): Proceed to step 6.0
    5.3.2 If QC fails:
          a. Document failure in QC log
          b. Notify supervisor
          c. Proceed to troubleshooting (Appendix A)
```

**Rule 3: Critical Steps Highlighting**
```
⚠️ CRITICAL: Verify patient identity using TWO independent identifiers
before proceeding.

⚠️ SAFETY: Perform all steps in biosafety cabinet with appropriate PPE.

⚠️ TIME-SENSITIVE: Complete within 4 hours of sample collection.
```

### 5.3 TRPM-LIMS Specific Instructions

**System Navigation Format:**
```
1. Log into TRPM-LIMS at [URL]
2. Navigate to: Molecular Diagnostics → Molecular Samples
3. Click "Add Molecular Sample"
4. Complete the following fields:
   - Lab Order: [Select from dropdown or enter order ID]
   - Sample Type: [Select appropriate type]
   - Test Panel: [Select required panel]
   - Collection DateTime: [Enter or select]
```

**Field-Specific Instructions:**
```
Field Name          Required    Format/Values
─────────────────────────────────────────────
Sample ID           Auto        MOL-YYYYMMDD-XXXX
Patient             Yes         Search by OP_NO or name
Workflow Status     Auto        RECEIVED (default)
Volume (µL)         Yes         Numeric, > 0
Concentration       No          ng/µL
A260/280            No          Ratio, typically 1.8-2.0
```

---

## 6. Document Lifecycle Management

### 6.1 Document States

```
┌─────────┐    ┌──────────────┐    ┌──────────┐    ┌───────────┐
│  DRAFT  │───▶│ UNDER_REVIEW │───▶│ APPROVED │───▶│ PUBLISHED │
└─────────┘    └──────────────┘    └──────────┘    └───────────┘
     │                │                                   │
     │                ▼                                   ▼
     │         ┌──────────┐                        ┌──────────┐
     └────────▶│ REJECTED │                        │ OBSOLETE │
               └──────────┘                        └──────────┘
```

| State | Description | Access |
|-------|-------------|--------|
| **DRAFT** | Document in development | Author only |
| **UNDER_REVIEW** | Submitted for review | Reviewers |
| **REJECTED** | Review failed, needs revision | Author |
| **APPROVED** | Technically and quality approved | Awaiting publication |
| **PUBLISHED** | Active, effective document | All authorized users |
| **OBSOLETE** | Superseded or retired | Read-only archive |

### 6.2 Lifecycle Phases

**Phase 1: Initiation**
1. Identify need for new/revised SOP
2. Assign document owner
3. Determine document type and classification
4. Assign document number (via TRPM-LIMS QMS)

**Phase 2: Development**
1. Research regulatory requirements
2. Consult subject matter experts
3. Draft content using approved template
4. Include supporting materials

**Phase 3: Review**
1. Technical review (content accuracy)
2. Quality review (format, compliance)
3. Address review comments
4. Final revision

**Phase 4: Approval**
1. Submit for final approval
2. Obtain required signatures
3. Set effective date

**Phase 5: Publication**
1. Upload to TRPM-LIMS QMS
2. Set document permissions
3. Notify affected users
4. Mark previous version obsolete

**Phase 6: Maintenance**
1. Periodic review per schedule
2. Update as processes change
3. Track revisions

**Phase 7: Retirement**
1. Mark as obsolete
2. Archive per retention policy
3. Maintain audit trail

### 6.3 TRPM-LIMS Document Management

**Creating Documents:**
```
1. Navigate to: QMS → Documents → Add Document
2. Select Category (e.g., "SOP")
3. Enter Document Number per naming convention
4. Assign to Folder (department/module)
5. Set Editor Type:
   - RICHTEXT: For web-based editing
   - MARKDOWN: For technical documentation
   - PDF: For uploaded finalized documents
6. Add Authors and Readers
7. Set Review Interval (days)
8. Save as Draft
```

**Creating Versions:**
```
1. Open existing document
2. Click "Create New Version"
3. Enter Version Number (e.g., 1.1, 2.0)
4. Mark as Major Version if significant changes
5. Enter Change Summary
6. Upload/Edit content
7. Save
```

**Submitting for Review:**
```
1. Open document in DRAFT state
2. Click "Submit for Review"
3. System creates Review Cycle
4. Reviewers receive notification
5. Track review progress in QMS → Reviews
```

---

## 7. Version Control Methodology

### 7.1 Version Numbering Schema

**Format:** `MAJOR.MINOR`

| Change Type | Version Change | Example |
|-------------|---------------|---------|
| Initial release | 1.0 | First publication |
| Minor correction (typo, clarification) | +0.1 | 1.0 → 1.1 |
| Procedural update (same intent) | +0.1 | 1.1 → 1.2 |
| Significant change (new requirements) | +1.0 | 1.2 → 2.0 |
| Complete rewrite | +1.0 | 2.0 → 3.0 |

### 7.2 Change Classification

| Classification | Description | Version Impact | Review Required |
|----------------|-------------|----------------|-----------------|
| **Editorial** | Spelling, grammar, formatting | +0.1 | Quality only |
| **Clarification** | Rewording for clarity (no change in intent) | +0.1 | Quality only |
| **Minor Update** | Updated references, contact info | +0.1 | Technical + Quality |
| **Procedural Change** | Modified steps, new requirements | +0.5 or +1.0 | Full review |
| **Major Revision** | Significant content overhaul | +1.0 | Full review + validation |

### 7.3 Multi-Laboratory Version Control

```
Master SOP (Corporate)
├── SOP-MOL-001-v2.0 (Master)
│
├── Laboratory A (Customization)
│   └── SOP-MOL-001-A-v2.0.1 (Local adaptation)
│
├── Laboratory B (Uses Master)
│   └── SOP-MOL-001-v2.0 (No local changes)
│
└── Laboratory C (Customization)
    └── SOP-MOL-001-C-v2.0.3 (Local adaptation)
```

---

## 8. Review and Approval Workflow

### 8.1 Review Types

| Review Type | Purpose | Participants |
|-------------|---------|--------------|
| **Technical Review** | Verify scientific/technical accuracy | Subject matter experts |
| **Quality Review** | Ensure compliance with format/standards | Quality team |
| **Regulatory Review** | Verify regulatory compliance | Compliance officer |
| **Cross-Functional Review** | Assess impact on other departments | Department representatives |
| **Final Approval** | Authorize for implementation | Lab Director |

### 8.2 Review Cycle Workflow

```
┌──────────────────────────────────────────────────────────────┐
│                    REVIEW CYCLE WORKFLOW                      │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Author submits document                                     │
│         │                                                    │
│         ▼                                                    │
│  ┌────────────────┐                                         │
│  │ Review Cycle   │◀─────────────────┐                      │
│  │ Created        │                   │                      │
│  └───────┬────────┘                   │                      │
│          │                            │                      │
│          ▼                            │                      │
│  ┌────────────────┐                   │                      │
│  │ Assigned to    │                   │                      │
│  │ Reviewers      │                   │                      │
│  └───────┬────────┘                   │                      │
│          │                            │                      │
│          ▼                            │                      │
│  ┌────────────────┐    ┌──────────┐  │                      │
│  │ Each Reviewer  │───▶│ Comments │──┘                      │
│  │ Reviews        │    │ /Reject  │   (Revision needed)     │
│  └───────┬────────┘    └──────────┘                         │
│          │                                                   │
│          ▼ (All Approved)                                    │
│  ┌────────────────┐                                         │
│  │ Final Approver │                                         │
│  │ Review         │                                         │
│  └───────┬────────┘                                         │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                         │
│  │ PUBLISHED      │                                         │
│  └────────────────┘                                         │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 8.3 Review Timelines

| Document Criticality | Technical Review | Quality Review | Final Approval | Total Target |
|---------------------|------------------|----------------|----------------|--------------|
| Critical | 5 business days | 3 business days | 2 business days | 10 business days |
| Major | 5 business days | 3 business days | 2 business days | 10 business days |
| Standard | 3 business days | 2 business days | 1 business day | 6 business days |
| Minor | 2 business days | 1 business day | 1 business day | 4 business days |

### 8.4 Review Checklists

**Technical Review:**
- [ ] Procedure is scientifically accurate
- [ ] Steps are in correct sequence
- [ ] Equipment/materials are correctly specified
- [ ] QC requirements are appropriate
- [ ] Safety precautions are adequate
- [ ] References are current

**Quality Review:**
- [ ] Document follows standard template
- [ ] Numbering system is correct
- [ ] Language meets standards
- [ ] Cross-references are accurate
- [ ] Revision history is complete
- [ ] Regulatory requirements addressed

---

# PART II: SYSTEM OVERVIEW & ACCESS

---

## 9. System Overview

### 9.1 System Description

TRPM-LIMS is a comprehensive, multi-tenant Laboratory Information Management System built on Django framework. It supports clinical laboratory testing, molecular diagnostics, microbiology, pathology, and quality management.

### 9.2 Core Modules

| Module | Description |
|--------|-------------|
| **Lab Management** | Patient registration, lab orders, test results |
| **Molecular Diagnostics** | PCR, NGS, sequencing workflows |
| **Microbiology** | Culture, sensitivity, organism identification |
| **Pathology** | Histopathology, block/slide tracking |
| **Equipment** | Instrument tracking, maintenance scheduling |
| **Storage** | Sample storage locations, audit logging |
| **Reagents** | Inventory, lot tracking, expiration management |
| **QMS** | Document control, SOPs, review workflows |
| **Analytics** | Dashboards, TAT monitoring, metrics |
| **Billing** | Invoice and payment management |
| **Bioinformatics** | Pipeline and analysis management |
| **Pharmacogenomics** | Drug-gene interaction analysis |
| **Sensors** | Environmental monitoring |

### 9.3 Multi-Tenant Architecture

TRPM-LIMS supports multiple organizations and laboratories with complete data isolation:

```
Organization (e.g., Hospital Network)
├── Laboratory 1 (e.g., Main Campus Lab)
│   ├── Users with lab-specific roles
│   └── Lab-specific data
├── Laboratory 2 (e.g., Satellite Lab)
│   ├── Users with lab-specific roles
│   └── Lab-specific data
└── Shared configurations
```

### 9.4 System Requirements

| Component | Requirement |
|-----------|-------------|
| **Server** | Python 3.10+, Django 6.0+ |
| **Database** | PostgreSQL (production) or SQLite (development) |
| **Dependencies** | Pillow, python-barcode, qrcode, weasyprint |

---

## 10. User Roles and Responsibilities

### 10.1 Organization-Level Roles

| Role | Permissions | Responsibilities |
|------|-------------|------------------|
| **Owner** | Full administrative access | Organization configuration, billing, user management |
| **Administrator** | Administrative access | User management, laboratory setup, settings |
| **Manager** | Supervisory access | Workflow oversight, reporting, approvals |
| **Member** | Standard access | Day-to-day operations |
| **Viewer** | Read-only access | View data, generate reports |

### 10.2 Laboratory-Level Roles

| Role | Permissions | Responsibilities |
|------|-------------|------------------|
| **Laboratory Director** | Full lab authority | Final approvals, QC oversight, compliance |
| **Laboratory Manager** | Lab administration | Staff supervision, workflow management |
| **Supervisor** | Section oversight | Section management, result review |
| **Senior Technician** | Advanced testing | Complex testing, troubleshooting, training |
| **Technician** | Standard testing | Sample processing, testing, data entry |
| **Trainee** | Limited access | Supervised operations only |
| **Viewer** | Read-only | View results and reports |

### 10.3 Role Assignment Procedure

**Procedure:**
1. **Request:** Department head submits user access request form
2. **Review:** Laboratory Manager reviews and approves role assignment
3. **Creation:** Administrator creates user account with appropriate role
4. **Training:** User completes required training modules
5. **Activation:** Account activated after training verification
6. **Documentation:** Access documented in user management records

---

## 11. System Access and Security

### 11.1 Account Creation

**Procedure:**
1. Navigate to Admin Panel → Users → Add User
2. Enter required information:
   - Username (unique identifier)
   - Email address
   - Initial password (temporary)
   - First and last name
3. Assign organization membership
4. Assign laboratory membership(s) with appropriate roles
5. Save and notify user

### 11.2 Password Requirements

| Requirement | Specification |
|-------------|---------------|
| Minimum length | 12 characters |
| Uppercase letters | At least one |
| Lowercase letters | At least one |
| Numbers | At least one |
| Special characters | At least one |
| Password expiration | Every 90 days |
| Password history | Cannot reuse last 12 passwords |

### 11.3 Login Procedure

**Procedure:**
1. Navigate to system URL
2. Enter username and password
3. Complete multi-factor authentication (if enabled)
4. System logs login with IP address and timestamp
5. User directed to default laboratory dashboard

### 11.4 Session Management

| Parameter | Setting |
|-----------|---------|
| Session timeout | 30 minutes of inactivity |
| Concurrent session limit | 2 per user |
| Browser close behavior | Automatic logout |

### 11.5 Account Lockout

| Condition | Action |
|-----------|--------|
| 5 failed login attempts | 15-minute lockout |
| 10 failed attempts | 24-hour lockout |
| 15 failed attempts | Administrator intervention required |

All failed attempts are logged in the audit trail.

---

## 12. Initial Setup Procedures

### 12.1 Organization Setup

**Procedure:**
1. Navigate to Admin → Tenants → Organizations
2. Click "Add Organization"
3. Complete required fields:
   - Name and Code
   - Contact information
   - Subscription tier
   - Maximum laboratories/users/samples
4. Save organization

### 12.2 Laboratory Setup

**Procedure:**
1. Navigate to Admin → Tenants → Laboratories
2. Click "Add Laboratory"
3. Select parent organization
4. Complete required fields:
   - Name and Code
   - Laboratory type (Clinical, Research, Molecular, etc.)
   - Accreditation information
   - Contact details
   - Timezone
5. Configure feature flags as needed
6. Save laboratory

### 12.3 Initial Configuration Checklist

| Item | Module | Priority |
|------|--------|----------|
| Create Instrument Types | Equipment | High |
| Add Instruments | Equipment | High |
| Configure Storage Units | Storage | High |
| Create Sample Types | Molecular Diagnostics | High |
| Define Gene Targets | Molecular Diagnostics | Medium |
| Create Workflow Definitions | Molecular Diagnostics | Medium |
| Set up Test Panels | Molecular Diagnostics | Medium |
| Configure QC Metrics | Molecular Diagnostics | Medium |
| Create Consent Protocols | Compliance | High |
| Set up Reagent Categories | Reagents | Medium |

---

# PART III: CORE LABORATORY OPERATIONS

---

## 13. Patient Management

### 13.1 Patient Registration

**Procedure:**
1. Navigate to Lab Management → Patients
2. Click "Add Patient"
3. Enter patient information:
   - **OP_NO** (Outpatient Number) - unique identifier
   - First Name, Last Name
   - Date of Birth
   - Gender
   - Contact Information
   - Address
   - Emergency Contact
4. Verify no duplicate entries exist
5. Save patient record
6. System automatically generates barcode

### 13.2 Patient Search

**Methods:**
| Method | Description |
|--------|-------------|
| OP_NO | Exact match search |
| Name | Partial match search |
| Date of Birth | Date-based search |
| Barcode | Scan barcode (if equipped) |

### 13.3 Patient Update

**Procedure:**
1. Search and locate patient record
2. Click to edit
3. Update required fields
4. Add note explaining change
5. Save changes
6. System logs all modifications in audit trail

### 13.4 Patient Merge (Duplicate Resolution)

**Authorization:** Laboratory Manager or higher

**Procedure:**
1. Identify duplicate patient records
2. Determine primary record (most complete)
3. Document rationale for merge
4. Execute merge (transfers all orders/samples to primary)
5. Audit trail maintains both record histories

---

## 14. Lab Order Management

### 14.1 Creating a Lab Order

**Procedure:**
1. Navigate to Lab Management → Lab Orders
2. Click "Add Lab Order"
3. Select or search for patient
4. Enter order details:
   - Test type (Chemistry, Hematology, Molecular, etc.)
   - Specific test name
   - Priority (Routine, Urgent, STAT)
   - Clinical information
   - Ordering physician
5. System auto-populates sample type and container
6. Save order
7. System generates order barcode

### 14.2 Order Priorities

| Priority | Definition | TAT Target |
|----------|------------|------------|
| **STAT** | Life-threatening situation | < 1 hour |
| **Urgent** | Results needed same day | < 4 hours |
| **Routine** | Standard processing | Per test TAT |

### 14.3 Order Modification

**Authorization:** Technician or higher

**Restrictions:**
- Cannot modify orders with final results
- All changes logged in audit trail
- Reason for modification required

### 14.4 Order Cancellation

**Authorization:** Supervisor or higher

**Procedure:**
1. Open order record
2. Select "Cancel Order"
3. Enter cancellation reason
4. Confirm cancellation
5. System updates order status
6. Notifications sent to relevant parties

---

## 15. Reagent Inventory Management

### 15.1 Reagent Categories

| Category | Description |
|----------|-------------|
| **General** | Common lab chemicals, buffers |
| **Molecular** | Primers, probes, polymerases |
| **Kits** | Complete test kits |
| **Controls** | QC materials |
| **Calibrators** | Calibration materials |

### 15.2 Reagent Receipt

**Procedure:**
1. Receive shipment
2. Verify against order:
   - Item description
   - Quantity
   - Lot numbers
3. Inspect for damage
4. Navigate to Reagents → Add Reagent
5. Enter reagent details:
   - Name and catalog number
   - Manufacturer
   - Lot number
   - Quantity received
   - Expiration date
   - Storage requirements
6. Store reagent appropriately
7. Save record

### 15.3 Reagent Usage

**Procedure:**
1. Retrieve reagent from storage
2. Verify not expired
3. Document usage:
   - Navigate to reagent record
   - Update quantity on hand
4. Link usage to sample/run if applicable
5. Return to storage

### 15.4 Expiration Management

**Daily Review:**
1. Run expiration report
2. Review reagents expiring within 30 days
3. Plan usage or reorder
4. Remove expired reagents:
   - Mark as expired in system
   - Physically remove from inventory
   - Document disposal

### 15.5 Reorder Process

**Procedure:**
1. Monitor inventory levels
2. When below reorder point:
   - Generate purchase request
   - Submit for approval
   - Place order with vendor
3. Document order in system
4. Update records upon receipt

---

# PART IV: MOLECULAR DIAGNOSTICS

---

## 16. Molecular Diagnostics Workflow

### 16.1 Sample Registration

**Procedure:**
1. Navigate to Molecular Diagnostics → Molecular Samples
2. Click "Add Molecular Sample"
3. Link to existing Lab Order
4. Select Sample Type
5. Select Test Panel
6. Enter collection datetime
7. Record sample volume
8. System generates sample ID (format: MOL-YYYYMMDD-XXXX)
9. Save sample
10. Print sample label

### 16.2 Workflow States

| Status | Description | Next Steps |
|--------|-------------|------------|
| **RECEIVED** | Sample received in lab | Extraction |
| **EXTRACTED** | DNA/RNA extraction complete | Amplification or Sequencing |
| **AMPLIFIED** | PCR amplification complete | Analysis |
| **SEQUENCED** | Sequencing complete | Analysis |
| **ANALYZED** | Bioinformatics analysis complete | Reporting |
| **REPORTED** | Final report generated | Archive |
| **CANCELLED** | Sample cancelled | N/A |
| **FAILED** | Processing failed | Review/Retest |

### 16.3 Workflow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   RECEIVED  │────▶│  EXTRACTED  │────▶│  AMPLIFIED  │
└─────────────┘     └─────────────┘     └─────────────┘
                           │                    │
                           ▼                    ▼
                    ┌─────────────┐     ┌─────────────┐
                    │   FAILED    │     │  SEQUENCED  │
                    └─────────────┘     └─────────────┘
                                               │
                           ┌───────────────────┘
                           ▼
                    ┌─────────────┐     ┌─────────────┐
                    │  ANALYZED   │────▶│  REPORTED   │
                    └─────────────┘     └─────────────┘
```

### 16.4 Status Transition Procedure

**Procedure:**
1. Select sample(s) in sample list
2. Choose appropriate action:
   - "Mark as Extracted"
   - "Mark as Amplified"
   - "Mark as Sequenced"
   - "Mark as Analyzed"
   - "Mark as Reported"
3. Click "Go"
4. System validates transition is permitted
5. Status updated with timestamp
6. Workflow history recorded

### 16.5 Sample Derivation

#### Creating Aliquots

**Procedure:**
1. Open parent sample record
2. Select "Create Aliquot"
3. Enter aliquot volume
4. Add notes (optional)
5. Save
6. System creates child sample with:
   - Derivation type: ALIQUOT
   - Link to parent sample
   - Sequential aliquot number

#### Creating Extracts

**Procedure:**
1. Open parent sample record
2. Select "Create Extract"
3. Enter extraction details:
   - Volume (µL)
   - Concentration (ng/µL)
   - A260/280 ratio
4. Save
5. System creates child sample with:
   - Derivation type: EXTRACT
   - Status: EXTRACTED
   - Link to parent sample

---

## 17. PCR and NGS Procedures

### 17.1 PCR Plate Management

**Procedure:**
1. Navigate to Molecular Diagnostics → PCR Plates
2. Click "Add PCR Plate"
3. Enter plate details:
   - Plate barcode
   - Plate format (96-well or 384-well)
   - Instrument Run (if applicable)
4. Add wells:
   - Position (A1-H12 for 96-well)
   - Sample or Control
   - Target gene(s)
5. Save plate
6. Link to instrument run

### 17.2 NGS Library Preparation

**Procedure:**
1. Navigate to Molecular Diagnostics → NGS Libraries
2. Create new library record
3. Enter library details:
   - Library ID
   - Source sample(s)
   - Library prep kit
   - Index sequences
   - Concentration
4. Pool libraries as needed
5. Link to sequencing run

### 17.3 NGS Workflow Template

```
Workflow: NGS Testing
Steps:
1. Sample Receipt (RECEIVED)
   - QC Required: No
   - Estimated Duration: 1 hour

2. DNA Extraction (EXTRACTED)
   - QC Required: Yes
   - QC Metrics: Concentration, A260/280, DIN
   - Estimated Duration: 4 hours

3. Library Preparation (AMPLIFIED)
   - QC Required: Yes
   - QC Metrics: Library Size, Concentration
   - Estimated Duration: 8 hours

4. Sequencing (SEQUENCED)
   - QC Required: Yes
   - QC Metrics: Q30, Cluster Density
   - Required Instrument: NextSeq 2000
   - Estimated Duration: 24 hours

5. Analysis (ANALYZED)
   - QC Required: Yes
   - Estimated Duration: 4 hours

6. Reporting (REPORTED)
   - Terminal: Yes
```

---

## 18. Result Entry and Reporting

### 18.1 PCR Results

**Procedure:**
1. Navigate to Molecular Diagnostics → Molecular Results
2. Create new result linked to sample
3. Add PCR Result entries:
   - Target gene
   - Ct value
   - Detection status (auto-determined: Ct ≤ 40 = Detected)
   - Melting temperature (if applicable)
4. Review and save

### 18.2 Variant Calls

**Procedure:**
1. Navigate to Molecular Results → Variant Calls
2. Create variant call entry:
   - Gene name
   - Chromosome and position
   - Reference and alternate alleles
   - HGVS nomenclature (c. and p. notation)
   - Allele frequency
   - Read depth
   - ACMG classification
3. Add interpretation notes
4. Save

### 18.3 ACMG Classification Guide

| Classification | Description |
|----------------|-------------|
| **Pathogenic** | Causes disease |
| **Likely Pathogenic** | >90% certainty of pathogenicity |
| **VUS** | Variant of Uncertain Significance |
| **Likely Benign** | >90% certainty of benign nature |
| **Benign** | Does not cause disease |

### 18.4 Result Review and Approval

**Authorization:** Supervisor or Laboratory Director

**Procedure:**
1. Open result record
2. Review all data:
   - QC metrics passed
   - Results within expected ranges
   - No technical issues flagged
3. Set result status:
   - **Preliminary:** Initial entry, not verified
   - **Verified:** Technically verified
   - **Final:** Approved for release
   - **Amended:** Corrected after finalization
4. Add reviewer comments
5. Save
6. For Final status, result is released for reporting

### 18.5 Report Generation

**Procedure:**
1. Ensure result status is "Final"
2. Select result(s) in list view
3. Choose "Generate Reports" action
4. Click "Go"
5. System generates PDF report with:
   - Laboratory header and accreditation
   - Patient demographics
   - Sample information
   - Test results and interpretation
   - Reviewer signatures
   - Report timestamp
6. Download PDF from result detail page

---

# PART V: SPECIALIZED MODULES

---

## 19. Microbiology Module

### 19.1 Culture Sample Registration

**Procedure:**
1. Navigate to Microbiology → Microbiology Samples
2. Create new sample linked to lab order
3. Enter sample details:
   - Specimen type (Blood, Urine, Wound, etc.)
   - Collection site
   - Culture type
4. Save sample

### 19.2 Culture Processing

**Procedure:**
1. Plate sample on appropriate media
2. Record plating details in system
3. Incubate per protocol
4. Record daily observations:
   - Growth: None, Light, Moderate, Heavy
   - Colony morphology
   - Gram stain results
5. Update sample status

### 19.3 Organism Identification

**Procedure:**
1. Select isolate for identification
2. Perform identification testing (manual or automated)
3. Record organism identification:
   - Organism name (genus/species)
   - Identification method
   - Confidence level
4. Link to taxonomic database

### 19.4 Antibiotic Susceptibility Testing (AST)

**Procedure:**
1. Navigate to Microbiology → AST Results
2. Select organism identification
3. Select AST panel appropriate for organism
4. Enter results for each antibiotic:
   - MIC value or zone size
   - Interpretation (S/I/R)
5. System applies breakpoints automatically
6. Review and save

### 19.5 Breakpoint Configuration

**Authorization:** Laboratory Director

**Procedure:**
1. Navigate to Microbiology → Antibiotic Panels
2. Select or create panel
3. For each antibiotic, configure:
   - MIC breakpoints (S, I, R thresholds)
   - Zone diameter breakpoints
   - Source (CLSI, EUCAST)
4. Save configuration

---

## 20. Pathology Module

### 20.1 Case Registration

**Procedure:**
1. Navigate to Pathology → Cases
2. Create new case linked to patient
3. Enter case information:
   - Specimen type
   - Clinical history
   - Pre-operative diagnosis
   - Surgeon/referring physician
4. Save case

### 20.2 Specimen Accessioning

**Procedure:**
1. Receive specimen in laboratory
2. Verify patient identification
3. Assign case number
4. Document specimen condition
5. Photograph specimen (if required)
6. Enter gross description

### 20.3 Grossing Procedure

**Procedure:**
1. Perform gross examination
2. Document gross findings:
   - Dimensions and weight
   - Color and consistency
   - Lesion descriptions
   - Margin status (if applicable)
3. Submit tissue sections
4. Create blocks:
   - Navigate to Pathology → Histology Blocks
   - Enter block designation (A1, A2, B1, etc.)
   - Record tissue type per block
5. Save gross description

### 20.4 Slide Preparation

**Procedure:**
1. Create slides from blocks
2. Navigate to Pathology → Histology Slides
3. Enter slide information:
   - Block reference
   - Stain type (H&E, IHC, Special stain)
   - Level/serial number
4. Apply staining protocol
5. Record staining completion
6. Deliver to pathologist

### 20.5 Diagnosis Entry

**Authorization:** Pathologist

**Procedure:**
1. Review slides
2. Enter microscopic description
3. Enter diagnosis:
   - Primary diagnosis
   - Secondary findings
   - TNM staging (if applicable)
   - Prognostic markers
4. Add comments and recommendations
5. Sign out case
6. Generate pathology report

---

# PART VI: QUALITY MANAGEMENT

---

## 21. Quality Control Procedures

### 21.1 QC Metric Definition

**Authorization:** Laboratory Manager

**Procedure:**
1. Navigate to Molecular Diagnostics → QC Metric Definitions
2. Click "Add QC Metric Definition"
3. Define metric:
   - Name (e.g., "DNA Concentration")
   - Unit of measurement
   - Minimum acceptable value
   - Maximum acceptable value
   - Warning threshold (% of range)
   - Is critical (yes/no)
4. Save definition

### 21.2 QC Recording

**Procedure:**
1. Navigate to QC Records
2. Create new QC record linked to:
   - Instrument Run, or
   - PCR Plate, or
   - Sample batch
3. Enter measured values for each metric
4. System automatically calculates:
   - Pass/fail status
   - Warning flags
   - Deviation from target
5. Save record
6. Review any failures immediately

### 21.3 QC Failure Handling

**Procedure:**
1. Document failure details
2. Investigate root cause
3. Determine corrective action:
   - Repeat testing
   - Recalibrate instrument
   - Replace reagents
4. Document corrective action
5. Re-run QC
6. If pass, proceed with patient testing
7. If fail, escalate to supervisor

### 21.4 Control Materials

**Daily Controls:**
- Run positive and negative controls each day
- Document control results
- Review Levey-Jennings charts
- Document any out-of-range controls

**Procedure:**
1. Prepare control materials per SOP
2. Run controls with patient samples
3. Review control results before releasing patient results
4. Document any deviations
5. Reject batch if controls fail

### 21.5 Proficiency Testing

**Procedure:**
1. Receive PT samples
2. Treat as unknown patient samples
3. Test per standard procedures
4. Enter results in TRPM-LIMS
5. Submit results before deadline
6. Review PT report when received
7. Document any unacceptable results
8. Implement corrective actions if needed

---

## 22. Quality Management System (QMS)

### 22.1 Document Categories

| Category | Description | Review Frequency |
|----------|-------------|------------------|
| **SOP** | Standard Operating Procedures | Annual |
| **Policy** | Laboratory policies | Annual |
| **Form** | Blank forms and templates | As needed |
| **Work Instruction** | Step-by-step procedures | Annual |
| **Reference** | Reference materials | As needed |

### 22.2 Document Creation

**Authorization:** Document owner with QMS access

**Procedure:**
1. Navigate to QMS → Documents
2. Click "Add Document"
3. Enter document details:
   - Title
   - Document number
   - Category
   - Author
   - Effective date
4. Upload document file
5. Set review cycle
6. Submit for review

### 22.3 Document Review Workflow

**States:**
1. **Draft** - Initial creation
2. **Under Review** - Submitted for review
3. **Approved** - Approved for use
4. **Obsolete** - No longer current

**Procedure:**
1. Author submits document for review
2. Reviewers receive notification
3. Reviewers add comments/approve
4. Document owner addresses comments
5. Final approver (Lab Director) approves
6. Document becomes effective
7. Previous version marked obsolete

### 22.4 Document Access

**Procedure:**
1. Navigate to QMS → Documents
2. Search by title, number, or category
3. View current effective version
4. Access version history if needed
5. Print controlled copies (with watermark)

### 22.5 Annual Document Review

**Procedure:**
1. Generate documents due for review report
2. Assign reviewers
3. Reviewers assess document:
   - Still accurate and current?
   - Any updates needed?
   - References current?
4. Update document if needed
5. Approve or submit revision
6. Document review completion

---

## 23. Compliance and Consent Management

### 23.1 Consent Protocol Setup

**Authorization:** Compliance Officer

**Procedure:**
1. Navigate to Compliance → Consent Protocols
2. Click "Add Consent Protocol"
3. Enter protocol details:
   - Name and version
   - Protocol type (General, Genetic, Biobank, etc.)
   - IRB number and dates
   - Effective and expiration dates
4. Configure requirements:
   - Requires witness (yes/no)
   - Requires legal representative (yes/no)
   - Minimum age for direct consent
5. Upload consent document
6. Save protocol

### 23.2 Obtaining Patient Consent

**Procedure:**
1. Identify applicable consent protocol(s)
2. Verify protocol is active and not expired
3. Navigate to Compliance → Patient Consents
4. Create new consent record:
   - Select patient
   - Select protocol
   - Select consent method
5. Obtain patient signature
6. If witness required, obtain witness information
7. If legal representative, document representative details
8. Upload signed consent form
9. Set status to "Consented"
10. Save record

### 23.3 Consent Status Values

| Status | Description |
|--------|-------------|
| **Pending** | Consent not yet obtained |
| **Consented** | Patient gave consent |
| **Declined** | Patient declined consent |
| **Withdrawn** | Patient withdrew consent |
| **Expired** | Protocol has expired |

### 23.4 Consent Verification

**Before testing genetic/research samples:**
1. Verify patient has valid consent for protocol
2. Confirm consent is not expired
3. Confirm consent not withdrawn
4. Document verification
5. Proceed only if valid consent confirmed

---

# PART VII: INFRASTRUCTURE MANAGEMENT

---

## 24. Equipment Management

### 24.1 Instrument Registration

**Procedure:**
1. Navigate to Equipment → Instruments
2. Click "Add Instrument"
3. Enter instrument details:
   - Name and model
   - Serial number
   - Manufacturer
   - Instrument type (select from types)
   - Location
   - Installation date
   - Status (Active, In Maintenance, Out of Service)
4. Set maintenance schedule
5. Set calibration schedule
6. Save instrument

### 24.2 Instrument Status Codes

| Status | Definition | Action Required |
|--------|------------|-----------------|
| **Active** | Operational for testing | None |
| **In Maintenance** | Undergoing maintenance | Complete maintenance |
| **Calibration Due** | Calibration scheduled | Perform calibration |
| **Out of Service** | Not operational | Repair or replace |
| **Retired** | Permanently removed | Archive records |

### 24.3 Maintenance Scheduling

**Procedure:**
1. Navigate to Equipment → Maintenance Records
2. Click "Add Maintenance Record"
3. Select instrument
4. Enter maintenance details:
   - Maintenance type (Preventive, Corrective, Calibration)
   - Scheduled date
   - Assigned technician
   - Checklist items
5. Save record
6. System sends reminders before due date

### 24.4 Performing Maintenance

**Procedure:**
1. Open maintenance record
2. Perform maintenance activities per protocol
3. Document actions taken:
   - Parts replaced
   - Adjustments made
   - Tests performed
4. Update status to "Completed"
5. Enter completion date
6. Upload any documentation (calibration certificates)
7. Set next maintenance date
8. Save record

### 24.5 Out of Service Procedure

**Procedure:**
1. Identify instrument issue
2. Set instrument status to "Out of Service"
3. Add note explaining issue
4. Notify supervisor
5. Create corrective action record
6. Arrange repair or replacement
7. Document all repair activities
8. Upon repair, perform verification testing
9. If verification passes, return to Active status
10. Document return to service

---

## 25. Sample Storage Management

### 25.1 Storage Unit Configuration

**Procedure:**
1. Navigate to Storage → Storage Units
2. Click "Add Storage Unit"
3. Enter unit details:
   - Name (e.g., "Freezer-01")
   - Type (Freezer, Refrigerator, Nitrogen Tank, Ambient)
   - Location
   - Temperature range
   - Capacity
4. Add racks to unit:
   - Rack name/position
   - Row and column configuration
5. Save configuration

### 25.2 Sample Storage Assignment

**Procedure:**
1. Open sample record
2. Navigate to storage location field
3. Select:
   - Storage unit
   - Rack
   - Position (row/column)
4. System validates position availability
5. Save assignment
6. System logs storage event

### 25.3 Sample Retrieval

**Procedure:**
1. Search for sample by ID
2. Note current storage location
3. Retrieve sample from storage
4. Document retrieval in system:
   - Clear storage location, or
   - Update to new location
5. System logs retrieval event
6. Return sample to appropriate storage when finished

### 25.4 Storage Audit

**Frequency:** Monthly

**Procedure:**
1. Generate storage inventory report
2. Physical verification:
   - Verify samples in documented locations
   - Note any discrepancies
3. Document audit findings
4. Investigate discrepancies
5. Update records as needed
6. Report findings to Laboratory Manager

### 25.5 Temperature Monitoring

**Procedure:**
1. Record temperatures per schedule (or automated)
2. Navigate to Sensors → Temperature Readings
3. Verify temperatures within acceptable range
4. Document any excursions
5. For excursions:
   - Notify supervisor immediately
   - Assess sample integrity
   - Document impact assessment
   - Take corrective action

---

# PART VIII: SYSTEM ADMINISTRATION

---

## 26. Audit Trail and Logging

### 26.1 Audit Log Contents

All system activities are logged with:
- Timestamp
- User information
- Action type (Create, Update, Delete, View, etc.)
- Object affected
- Before/after values for changes
- IP address
- User agent

### 26.2 Auditable Actions

| Action | Description |
|--------|-------------|
| **CREATE** | New record created |
| **UPDATE** | Record modified |
| **DELETE** | Record deleted |
| **VIEW** | Record viewed (sensitive data) |
| **EXPORT** | Data exported |
| **IMPORT** | Data imported |
| **LOGIN** | User logged in |
| **LOGOUT** | User logged out |
| **LOGIN_FAILED** | Failed login attempt |
| **APPROVE** | Record approved |
| **REJECT** | Record rejected |
| **TRANSITION** | Workflow status change |
| **PRINT** | Document printed |
| **EMAIL** | Document emailed |

### 26.3 Viewing Audit Logs

**Authorization:** Administrator, Laboratory Manager, or higher

**Procedure:**
1. Navigate to Audit → Audit Logs
2. Filter by:
   - Date range
   - User
   - Action type
   - Object type
3. Review log entries
4. Export if needed for investigation

### 26.4 Audit Trail Retention

| Item | Retention Period |
|------|-----------------|
| Audit logs | Minimum 10 years |
| Archive frequency | Annual |
| Archive storage | Securely off-site |
| Restoration testing | Annual |

---

## 27. Reporting and Analytics

### 27.1 Turnaround Time (TAT) Monitoring

**TAT Status Indicators:**

| Status | Definition | Action |
|--------|------------|--------|
| **On Track** | Within normal processing time | Continue processing |
| **Warning** | 75%+ of TAT target consumed | Prioritize |
| **Critical** | 90%+ of TAT target consumed | Immediate attention |
| **Overdue** | TAT target exceeded | Escalate |

**Accessing TAT Dashboard:**
1. Navigate to Molecular → TAT Dashboard
2. View at-risk samples
3. Filter by test panel
4. Review daily metrics
5. Export reports as needed

### 27.2 Standard Reports

| Report | Description | Frequency |
|--------|-------------|-----------|
| **Sample Volume** | Daily/weekly/monthly sample counts | Daily |
| **TAT Compliance** | % samples meeting TAT targets | Weekly |
| **QC Summary** | QC pass/fail rates | Weekly |
| **Workload Distribution** | Samples by technician | Weekly |
| **Equipment Utilization** | Instrument usage rates | Monthly |
| **Reagent Consumption** | Reagent usage trends | Monthly |

### 27.3 Generating Reports

**Procedure:**
1. Navigate to Analytics → Reports
2. Select report type
3. Configure parameters:
   - Date range
   - Laboratory
   - Test panel
   - Additional filters
4. Generate report
5. View on screen or export (PDF, Excel, CSV)

### 27.4 Custom Dashboards

**Authorization:** Laboratory Manager

**Procedure:**
1. Navigate to Analytics → Dashboards
2. Create new dashboard
3. Add widgets:
   - Charts
   - Metrics
   - Tables
   - Alerts
4. Configure refresh intervals
5. Share with appropriate users

---

## 28. Data Backup and Recovery

### 28.1 Backup Schedule

| Type | Frequency | Retention |
|------|-----------|-----------|
| **Full Backup** | Weekly (Sunday 2 AM) | 12 weeks |
| **Incremental Backup** | Daily (2 AM) | 4 weeks |
| **Transaction Logs** | Every 15 minutes | 1 week |

### 28.2 Backup Verification

**Weekly Procedure:**
1. Verify backup completion status
2. Check backup file integrity
3. Document verification results
4. Report any failures immediately

### 28.3 Disaster Recovery Testing

**Quarterly Procedure:**
1. Restore backup to test environment
2. Verify data integrity
3. Test critical functions
4. Document test results
5. Address any issues identified

### 28.4 Recovery Procedure

**Authorization:** IT Administrator with Laboratory Director approval

**Procedure:**
1. Document incident requiring recovery
2. Determine recovery point needed
3. Notify affected users of downtime
4. Execute recovery:
   - Stop application services
   - Restore database from backup
   - Verify data integrity
   - Restart services
5. Verify system function
6. Notify users of restoration
7. Document recovery actions

---

## 29. Change Control

### 29.1 Change Categories

| Category | Description | Approval |
|----------|-------------|----------|
| **Emergency** | Critical fix needed immediately | IT Manager + Lab Director |
| **Standard** | Normal enhancement or fix | Change Advisory Board |
| **Minor** | Minimal impact changes | IT Manager |

### 29.2 Change Request Process

**Procedure:**
1. Submit change request documenting:
   - Description of change
   - Reason/justification
   - Impact assessment
   - Testing plan
   - Rollback plan
2. Review by IT team
3. Impact assessment completed
4. Submit to Change Advisory Board
5. CAB reviews and approves/rejects
6. Schedule change window
7. Implement change
8. Verify function
9. Document completion
10. Close change request

### 29.3 Emergency Change Process

**Procedure:**
1. Document emergency situation
2. Obtain verbal approval from:
   - IT Manager
   - Laboratory Director
3. Implement fix
4. Document all actions
5. Submit retroactive change request
6. Review in next CAB meeting

### 29.4 Software Updates

**Procedure:**
1. Test update in development environment
2. Document test results
3. Submit change request
4. Schedule maintenance window
5. Notify users of downtime
6. Apply update:
   - Stop services
   - Backup database
   - Apply update
   - Run migrations
   - Verify function
   - Start services
7. Verify system operation
8. Document completion

---

# PART IX: APPENDICES

---

## 30. Templates and Forms

### 30.1 Blank SOP Template

```
┌─────────────────────────────────────────────────────────────────┐
│ [ORGANIZATION LOGO]        STANDARD OPERATING PROCEDURE        │
├─────────────────────────────────────────────────────────────────┤
│ Title: _______________________                                  │
│ Document Number: SOP-___-___     Version: _._                  │
│ Department: ___________________  Page: ___ of ___              │
│ Effective Date: ____-__-__       Review Date: ____-__-__       │
├─────────────────────────────────────────────────────────────────┤
│ Supersedes: _______________________ dated __________           │
└─────────────────────────────────────────────────────────────────┘

## APPROVAL SIGNATURES

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | | | |
| Technical Reviewer | | | |
| Quality Reviewer | | | |
| Final Approver | | | |

## REVISION HISTORY

| Version | Date | Author | Summary of Changes | Sections |
|---------|------|--------|-------------------|----------|
| | | | | |

---

## 1. PURPOSE
[State why this procedure exists]

## 2. SCOPE
[Define what/who this applies to]

## 3. DEFINITIONS
| Term | Definition |
|------|------------|
| | |

## 4. RESPONSIBILITIES
| Role | Responsibility |
|------|---------------|
| | |

## 5. REFERENCES
- [Related documents]
- [Standards]

## 6. MATERIALS AND EQUIPMENT
| Item | Specification |
|------|--------------|
| | |

## 7. SAFETY PRECAUTIONS
⚠️ [Hazards and precautions]

## 8. PROCEDURE
### 8.1 [Section Title]
1. [Step]
2. [Step]

## 9. QUALITY CONTROL
| QC Check | Acceptance Criteria | Frequency |
|----------|-------------------|-----------|
| | | |

## 10. DOCUMENTATION
[What records to maintain]

## 11. APPENDICES
```

### 30.2 SOP Review Form

See Appendix in QMS module for complete review form template.

### 30.3 SOP Change Request Form

See Appendix in QMS module for complete change request form template.

---

## 31. Reference Tables

### 31.1 Module-Specific Required SOPs

#### Core Lab Management
| SOP Number | Title |
|------------|-------|
| SOP-LAB-001 | Patient Registration |
| SOP-LAB-002 | Lab Order Management |
| SOP-LAB-003 | Sample Collection |
| SOP-LAB-004 | Result Entry and Release |
| SOP-LAB-005 | Specimen Rejection Criteria |

#### Molecular Diagnostics
| SOP Number | Title |
|------------|-------|
| SOP-MOL-001 | Sample Receipt and Registration |
| SOP-MOL-002 | DNA/RNA Extraction |
| SOP-MOL-003 | PCR Amplification |
| SOP-MOL-004 | NGS Library Preparation |
| SOP-MOL-005 | Sequencing Run Execution |
| SOP-MOL-006 | Bioinformatics Analysis |
| SOP-MOL-007 | Result Interpretation |
| SOP-MOL-008 | Report Generation |
| SOP-MOL-009 | Sample Derivation |
| SOP-MOL-010 | Quality Control Procedures |

#### Microbiology
| SOP Number | Title |
|------------|-------|
| SOP-MIC-001 | Culture Sample Registration |
| SOP-MIC-002 | Specimen Processing and Plating |
| SOP-MIC-003 | Culture Reading and Interpretation |
| SOP-MIC-004 | Organism Identification |
| SOP-MIC-005 | Antibiotic Susceptibility Testing |
| SOP-MIC-006 | AST Result Interpretation |
| SOP-MIC-007 | Breakpoint Configuration |

#### Pathology
| SOP Number | Title |
|------------|-------|
| SOP-PAT-001 | Specimen Accessioning |
| SOP-PAT-002 | Gross Examination |
| SOP-PAT-003 | Tissue Processing |
| SOP-PAT-004 | Block Management |
| SOP-PAT-005 | Slide Preparation |
| SOP-PAT-006 | Staining Procedures |
| SOP-PAT-007 | Pathology Sign-Out |

#### Equipment Management
| SOP Number | Title |
|------------|-------|
| SOP-EQP-001 | Instrument Qualification |
| SOP-EQP-002 | Daily Maintenance |
| SOP-EQP-003 | Preventive Maintenance |
| SOP-EQP-004 | Calibration Procedures |
| SOP-EQP-005 | Instrument Troubleshooting |
| SOP-EQP-006 | Out-of-Service Procedures |
| SOP-EQP-007 | Equipment Decommissioning |

#### Sample Storage
| SOP Number | Title |
|------------|-------|
| SOP-STO-001 | Storage Unit Configuration |
| SOP-STO-002 | Sample Storage Assignment |
| SOP-STO-003 | Sample Retrieval |
| SOP-STO-004 | Temperature Monitoring |
| SOP-STO-005 | Storage Audit Procedures |
| SOP-STO-006 | Temperature Excursion Response |

#### Quality Management
| SOP Number | Title |
|------------|-------|
| SOP-QMS-001 | Document Control |
| SOP-QMS-002 | Document Review Process |
| SOP-QMS-003 | Internal Audit |
| SOP-QMS-004 | Corrective Action |
| SOP-QMS-005 | Preventive Action |
| SOP-QMS-006 | Proficiency Testing |
| SOP-QMS-007 | Customer Complaint Handling |
| SOP-QMS-008 | Nonconforming Work |

### 31.2 Regulatory Cross-Reference Matrix

| SOP Category | ISO 15189 | CAP | CLIA | 21 CFR 11 |
|--------------|-----------|-----|------|-----------|
| Pre-analytical | 7.1 | GEN | 493.1241 | 11.10 |
| Analytical | 7.2 | Discipline-specific | 493.1251 | 11.10 |
| Post-analytical | 7.3, 7.4 | GEN | 493.1291 | 11.10 |
| Quality Management | 8.1-8.9 | QM | 493.1701 | 11.10 |
| Equipment | 6.4 | GEN | 493.1254 | 11.10 |
| Personnel | 6.2 | GEN | 493.1451 | 11.10 |
| Document Control | 8.3 | GEN | 493.1250 | 11.10 |

### 31.3 URL Quick Reference

| Function | URL |
|----------|-----|
| Admin Interface | `/admin/` |
| Molecular Dashboard | `/molecular/dashboard/` |
| Sample List | `/molecular/samples/` |
| PCR Plates | `/molecular/plates/` |
| TAT Monitoring | `/molecular/tat/` |
| Report Generation | `/molecular/reports/<id>/generate/` |
| Report Download | `/molecular/reports/<id>/download/` |
| QMS Documents | `/qms/documents/` |
| Audit Logs | `/audit/logs/` |
| Analytics Dashboard | `/analytics/` |

### 31.4 Training Checklist

| Module | Required For | Duration |
|--------|-------------|----------|
| System Navigation | All users | 1 hour |
| Patient/Order Management | All users | 2 hours |
| Molecular Diagnostics | Molecular techs | 4 hours |
| Microbiology | Micro techs | 4 hours |
| Pathology | Pathology staff | 4 hours |
| QC Procedures | All techs | 2 hours |
| Equipment Management | Senior techs | 2 hours |
| QMS | QA staff | 2 hours |
| Administration | Admins | 4 hours |

---

## 32. Glossary and Abbreviations

### 32.1 Abbreviations

| Abbreviation | Definition |
|--------------|------------|
| ACMG | American College of Medical Genetics |
| AST | Antibiotic Susceptibility Testing |
| CAP | College of American Pathologists |
| CAPA | Corrective and Preventive Action |
| CLIA | Clinical Laboratory Improvement Amendments |
| DIN | DNA Integrity Number |
| GxP | Good Practice regulations (GLP, GMP, GCP) |
| HIPAA | Health Insurance Portability and Accountability Act |
| IHC | Immunohistochemistry |
| IQ/OQ/PQ | Installation/Operational/Performance Qualification |
| LIMS | Laboratory Information Management System |
| MIC | Minimum Inhibitory Concentration |
| NGS | Next-Generation Sequencing |
| PCR | Polymerase Chain Reaction |
| PT | Proficiency Testing |
| QC | Quality Control |
| QMS | Quality Management System |
| SOP | Standard Operating Procedure |
| TAT | Turnaround Time |
| VUS | Variant of Uncertain Significance |

### 32.2 Contact Information

**System Administration:**
- IT Help Desk: [Contact Info]
- LIMS Administrator: [Contact Info]

**Laboratory Management:**
- Laboratory Director: [Contact Info]
- Laboratory Manager: [Contact Info]
- Quality Manager: [Contact Info]

**Vendor Support:**
- TRPM-LIMS Support: [Contact Info]

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | _________________ | _________________ | __________ |
| Technical Reviewer | _________________ | _________________ | __________ |
| Quality Manager | _________________ | _________________ | __________ |
| Laboratory Director | _________________ | _________________ | __________ |

---

## Document Control Statement

This document is controlled. Printed copies are for reference only. The current version is available in TRPM-LIMS QMS module. Verify version before use.

**Confidentiality:**
This document contains proprietary information. Do not distribute outside the organization without authorization.

---

*© 2026 TRPM-LIMS. All rights reserved.*

---

**END OF DOCUMENT**
