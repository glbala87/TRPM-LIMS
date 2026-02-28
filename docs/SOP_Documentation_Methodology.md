# TRPM-LIMS SOP Documentation Methodology

**Document Number:** MET-SOP-001
**Version:** 1.0
**Effective Date:** 2026-02-28
**Review Date:** 2027-02-28
**Classification:** Internal Use

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [Document Governance Framework](#2-document-governance-framework)
3. [SOP Taxonomy and Classification](#3-sop-taxonomy-and-classification)
4. [Document Structure Standards](#4-document-structure-standards)
5. [Writing Guidelines](#5-writing-guidelines)
6. [Document Lifecycle Management](#6-document-lifecycle-management)
7. [Version Control Methodology](#7-version-control-methodology)
8. [Review and Approval Workflow](#8-review-and-approval-workflow)
9. [Module-Specific SOP Development](#9-module-specific-sop-development)
10. [Regulatory Compliance Integration](#10-regulatory-compliance-integration)
11. [Training and Competency Linkage](#11-training-and-competency-linkage)
12. [Audit Trail Requirements](#12-audit-trail-requirements)
13. [Templates and Forms](#13-templates-and-forms)
14. [Continuous Improvement Process](#14-continuous-improvement-process)
15. [Appendices](#15-appendices)

---

## 1. Introduction

### 1.1 Purpose

This methodology document establishes a standardized framework for developing, managing, and maintaining Standard Operating Procedures (SOPs) within TRPM-LIMS. It ensures consistency, compliance, and quality across all documentation.

### 1.2 Scope

This methodology applies to:
- All SOP documentation within TRPM-LIMS
- Work instructions, policies, and guidelines
- Technical procedures and protocols
- User guides and training materials
- Quality management documentation

### 1.3 Definitions

| Term | Definition |
|------|------------|
| **SOP** | Standard Operating Procedure - detailed written instructions for routine operations |
| **Work Instruction** | Step-by-step procedure for specific tasks |
| **Policy** | High-level statement defining organizational intent |
| **Protocol** | Scientific procedure for testing or analysis |
| **Guideline** | Recommended practices (non-mandatory) |
| **Document Owner** | Person responsible for document content accuracy |
| **Document Controller** | Person managing document lifecycle |

### 1.4 Regulatory Foundation

This methodology aligns with:
- ISO 15189:2022 (Medical Laboratories)
- ISO 17025:2017 (Testing and Calibration Laboratories)
- CAP Accreditation Standards
- CLIA Regulations (42 CFR Part 493)
- 21 CFR Part 11 (Electronic Records)
- FDA GxP Requirements
- HIPAA Privacy and Security Rules

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
| **Laboratory Director** | Final approval authority, policy decisions |
| **Quality Manager** | QMS oversight, document control, compliance |
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

**Type Codes:**

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

**Module Codes:**

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

### 3.2 Document Categories in TRPM-LIMS

Based on the QMS module structure (`qms/models/documents.py`):

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

### 3.3 Criticality Classification

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

### 4.3 Revision History Table Format

| Version | Date | Author | Summary of Changes | Sections Affected |
|---------|------|--------|-------------------|-------------------|
| 1.0 | 2025-01-15 | J. Smith | Initial release | All |
| 1.1 | 2025-06-20 | J. Smith | Updated QC acceptance criteria | 13 |
| 2.0 | 2026-02-28 | M. Johnson | Major revision - added NGS workflow | 5, 11, 12 |

### 4.4 Procedure Section Formatting

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

Use imperative mood with consistent action verbs:

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

1. **One Action Per Step**
   - Bad: "Centrifuge the sample at 3000 rpm for 10 minutes, then transfer supernatant to a new tube and label appropriately"
   - Good:
     - Step 1: Centrifuge the sample at 3000 rpm for 10 minutes
     - Step 2: Transfer supernatant to a new tube
     - Step 3: Label the tube with [required information]

2. **Include Decision Points**
   ```
   5.3 Review QC Results
       5.3.1 If QC passes (within ±2 SD): Proceed to step 6.0
       5.3.2 If QC fails:
             a. Document failure in QC log
             b. Notify supervisor
             c. Proceed to troubleshooting (Appendix A)
   ```

3. **Critical Steps Highlighting**
   ```
   ⚠️ CRITICAL: Verify patient identity using TWO independent identifiers
   before proceeding.

   ⚠️ SAFETY: Perform all steps in biosafety cabinet with appropriate PPE.

   ⚠️ TIME-SENSITIVE: Complete within 4 hours of sample collection.
   ```

4. **Cross-References**
   ```
   Refer to SOP-MOL-003 "DNA Extraction Procedure" for detailed extraction protocol.
   ```

### 5.3 TRPM-LIMS Specific Instructions

When writing SOPs for TRPM-LIMS, include:

**System Navigation:**
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

**Workflow State Transitions:**
```
To transition sample status:
1. Select sample(s) in the list view
2. From "Action" dropdown, select:
   - "Mark as Extracted" (from RECEIVED)
   - "Mark as Amplified" (from EXTRACTED)
   - "Mark as Sequenced" (from AMPLIFIED)
3. Click "Go"
4. System validates and updates status with timestamp
```

### 5.4 Visual Elements

**Flowcharts:** Include for complex workflows

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

**Tables:** For reference data, parameters, acceptance criteria

**Screenshots:** Annotated TRPM-LIMS interface images (update with each version)

---

## 6. Document Lifecycle Management

### 6.1 Document States

Based on TRPM-LIMS QMS workflow states:

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

```
Creating Documents in TRPM-LIMS:
────────────────────────────────
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

Creating Versions:
──────────────────
1. Open existing document
2. Click "Create New Version"
3. Enter Version Number (e.g., 1.1, 2.0)
4. Mark as Major Version if significant changes
5. Enter Change Summary
6. Upload/Edit content
7. Save

Submitting for Review:
──────────────────────
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

### 7.3 Parallel Version Control (Multi-Laboratory)

For multi-tenant environments:

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

### 7.4 TRPM-LIMS Version Tracking

The system automatically tracks via `DocumentVersion` model:

```python
# From qms/models/documents.py
DocumentVersion:
├── document (FK to Document)
├── version_number (e.g., "2.0")
├── is_major_version (Boolean)
├── content (Text or File)
├── change_summary (Required for each version)
├── created_at (Timestamp)
├── created_by (User)
└── checksum (SHA-256 for integrity)
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

### 8.2 Review Cycle in TRPM-LIMS

Based on `qms/models/workflow.py`:

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

### 8.3 Review Checklist

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

### 8.4 Review Timelines

| Document Criticality | Technical Review | Quality Review | Final Approval | Total Target |
|---------------------|------------------|----------------|----------------|--------------|
| Critical | 5 business days | 3 business days | 2 business days | 10 business days |
| Major | 5 business days | 3 business days | 2 business days | 10 business days |
| Standard | 3 business days | 2 business days | 1 business day | 6 business days |
| Minor | 2 business days | 1 business day | 1 business day | 4 business days |

### 8.5 Expedited Review Process

For urgent updates (safety, critical corrections):

1. Document owner initiates "Urgent Review"
2. Notify reviewers via TRPM-LIMS messaging
3. Concurrent technical and quality review (24 hours)
4. Same-day final approval
5. Immediate publication
6. Post-hoc documentation of expedited rationale

---

## 9. Module-Specific SOP Development

### 9.1 Core Lab Management (lab_management/)

**Required SOPs:**

| SOP Number | Title | Key Elements |
|------------|-------|--------------|
| SOP-LAB-001 | Patient Registration | Identity verification, OP_NO assignment, barcode generation |
| SOP-LAB-002 | Lab Order Management | Order creation, modification, cancellation |
| SOP-LAB-003 | Sample Collection | Collection types, container selection, labeling |
| SOP-LAB-004 | Result Entry and Release | Data entry, verification, approval |
| SOP-LAB-005 | Specimen Rejection Criteria | Insufficient sample, labeling errors |

**TRPM-LIMS Fields Reference:**
```
Patient Model:
├── OP_NO (unique identifier)
├── Demographics (name, age, gender)
├── Contact Information
└── Barcode Image (auto-generated)

LabOrder Model:
├── Patient (FK)
├── Test Type/Name
├── Sample Type
├── Container
└── Status flags (collected, insufficient)
```

### 9.2 Molecular Diagnostics (molecular_diagnostics/)

**Required SOPs:**

| SOP Number | Title | Workflow States |
|------------|-------|-----------------|
| SOP-MOL-001 | Sample Receipt and Registration | RECEIVED |
| SOP-MOL-002 | DNA/RNA Extraction | RECEIVED → EXTRACTED |
| SOP-MOL-003 | PCR Amplification | EXTRACTED → AMPLIFIED |
| SOP-MOL-004 | NGS Library Preparation | EXTRACTED → SEQUENCED |
| SOP-MOL-005 | Sequencing Run Execution | AMPLIFIED → SEQUENCED |
| SOP-MOL-006 | Bioinformatics Analysis | SEQUENCED → ANALYZED |
| SOP-MOL-007 | Result Interpretation | ANALYZED |
| SOP-MOL-008 | Report Generation | ANALYZED → REPORTED |
| SOP-MOL-009 | Sample Derivation (Aliquots/Extracts) | Any → Derived |
| SOP-MOL-010 | Quality Control Procedures | All states |

**Workflow Definition Template:**
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

### 9.3 Microbiology (microbiology/)

**Required SOPs:**

| SOP Number | Title |
|------------|-------|
| SOP-MIC-001 | Culture Sample Registration |
| SOP-MIC-002 | Specimen Processing and Plating |
| SOP-MIC-003 | Culture Reading and Interpretation |
| SOP-MIC-004 | Organism Identification |
| SOP-MIC-005 | Antibiotic Susceptibility Testing |
| SOP-MIC-006 | AST Result Interpretation |
| SOP-MIC-007 | Breakpoint Configuration |

### 9.4 Pathology (pathology/)

**Required SOPs:**

| SOP Number | Title |
|------------|-------|
| SOP-PAT-001 | Specimen Accessioning |
| SOP-PAT-002 | Gross Examination |
| SOP-PAT-003 | Tissue Processing |
| SOP-PAT-004 | Block Management |
| SOP-PAT-005 | Slide Preparation |
| SOP-PAT-006 | Staining Procedures |
| SOP-PAT-007 | Pathology Sign-Out |

### 9.5 Equipment Management (equipment/)

**Required SOPs:**

| SOP Number | Title | Frequency |
|------------|-------|-----------|
| SOP-EQP-001 | Instrument Qualification | Initial/Annual |
| SOP-EQP-002 | Daily Maintenance | Daily |
| SOP-EQP-003 | Preventive Maintenance | Per schedule |
| SOP-EQP-004 | Calibration Procedures | Per schedule |
| SOP-EQP-005 | Instrument Troubleshooting | As needed |
| SOP-EQP-006 | Out-of-Service Procedures | As needed |
| SOP-EQP-007 | Equipment Decommissioning | As needed |

### 9.6 Sample Storage (storage/)

**Required SOPs:**

| SOP Number | Title |
|------------|-------|
| SOP-STO-001 | Storage Unit Configuration |
| SOP-STO-002 | Sample Storage Assignment |
| SOP-STO-003 | Sample Retrieval |
| SOP-STO-004 | Temperature Monitoring |
| SOP-STO-005 | Storage Audit Procedures |
| SOP-STO-006 | Temperature Excursion Response |

### 9.7 Quality Management (qms/)

**Required SOPs:**

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

---

## 10. Regulatory Compliance Integration

### 10.1 Compliance Mapping

**ISO 15189:2022 Requirements:**

| Clause | Requirement | Related SOPs |
|--------|-------------|--------------|
| 7.1 | Pre-examination | SOP-LAB-001 to 003 |
| 7.2 | Examination | All analytical SOPs |
| 7.3 | Post-examination | SOP-LAB-004, SOP-MOL-008 |
| 7.4 | Reporting | SOP-MOL-008, SOP-MIC-006 |
| 7.5 | Quality assurance | SOP-QMS-001 to 008 |

**21 CFR Part 11 Compliance:**

| Requirement | TRPM-LIMS Implementation |
|-------------|-------------------------|
| Audit trails | AuditLog model with timestamp, user, changes |
| Electronic signatures | User authentication with signature meaning |
| Access controls | Role-based permissions per laboratory |
| System validation | Documented IQ/OQ/PQ protocols |

**HIPAA Compliance:**

| Requirement | SOP Coverage |
|-------------|--------------|
| Access controls | SOP-SEC-001 |
| Audit controls | SOP-SEC-002 |
| Integrity controls | SOP-DAT-001 |
| Transmission security | SOP-SEC-003 |

### 10.2 Regulatory Reference Section Template

```markdown
## REGULATORY REFERENCES

### Applicable Standards
- ISO 15189:2022, Section 7.2.3 (Examination processes)
- CAP Checklist MIC.XXXXX (Reference to specific requirement)
- CLIA 42 CFR 493.XXX (Specific regulation)

### Compliance Requirements
This procedure addresses the following regulatory requirements:
1. [Specific requirement 1]
2. [Specific requirement 2]

### Change Impact Assessment
Any modification to this procedure requires:
- [ ] Regulatory notification (if applicable)
- [ ] Method validation (if analytical change)
- [ ] Competency reassessment (if procedural change)
```

---

## 11. Training and Competency Linkage

### 11.1 SOP-Training Matrix

Each SOP must specify:

| Training Element | Description |
|------------------|-------------|
| **Target Audience** | Roles/positions requiring training |
| **Prerequisites** | Prior training/competencies required |
| **Training Method** | Read-only, Demonstration, Hands-on |
| **Competency Assessment** | Test, Observation, Practical exam |
| **Retraining Trigger** | Annual, After revision, After error |

### 11.2 Training Documentation Integration

```
SOP Revision → Training Impact Assessment
                    │
                    ▼
    ┌───────────────────────────────────┐
    │ Determine if retraining required  │
    └───────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
    No Impact              Retraining Required
        │                       │
        ▼                       ▼
    Document in             Create Training
    Revision Notes          Assignment in TRPM-LIMS
                                │
                                ▼
                          Track Completion
                                │
                                ▼
                          Update Competency Records
```

### 11.3 Training Checklist in SOP

```markdown
## APPENDIX: TRAINING REQUIREMENTS

### Required Training
| Role | Training Type | Duration | Assessment |
|------|---------------|----------|------------|
| Technician | Hands-on demonstration | 4 hours | Practical observation |
| Senior Technician | Read + Review | 1 hour | Written acknowledgment |
| Supervisor | Read only | 30 minutes | Electronic signature |

### Competency Assessment Criteria
1. Perform procedure independently without errors
2. Correctly interpret results
3. Identify and respond to quality failures
4. Document properly in TRPM-LIMS

### Retraining Requirements
- Annual refresher
- After any SOP revision affecting procedure
- After competency failure or error
```

---

## 12. Audit Trail Requirements

### 12.1 TRPM-LIMS Audit Logging

Based on `audit/models.py`, the system logs:

```python
AuditLog:
├── timestamp (auto)
├── user (FK)
├── username (snapshot)
├── action (CREATE, UPDATE, DELETE, VIEW, APPROVE, etc.)
├── content_type (model type)
├── object_id (record ID)
├── object_repr (string representation)
├── changed_fields (JSON: {field: {old, new}})
├── ip_address
├── user_agent
├── request_path
└── notes
```

### 12.2 Document-Specific Audit Requirements

Each SOP must document:

| Audit Element | Description | Retention |
|---------------|-------------|-----------|
| Version history | All versions with changes | Permanent |
| Review records | Reviewer comments, decisions | 7 years |
| Training records | Who was trained, when, assessment | Active + 7 years |
| Access logs | Who accessed document | 3 years |
| Print/download logs | Controlled copy distribution | 3 years |

### 12.3 Audit Trail SOP Section Template

```markdown
## DOCUMENTATION AND RECORDS

### Required Records
| Record Type | Location in TRPM-LIMS | Retention |
|-------------|----------------------|-----------|
| Sample processing | Molecular → Samples → History | 10 years |
| QC records | Molecular → QC Records | 10 years |
| Result entry | Molecular → Results | 10 years |
| Approval | Result → Status History | 10 years |

### Audit Trail Verification
1. All actions automatically logged by TRPM-LIMS
2. Audit logs accessible via: Audit → Audit Logs
3. Filter by: Date range, User, Action type, Object type
4. Export capability for compliance audits

### Record Corrections
- System prevents deletion of finalized records
- Corrections require amendment (new entry with reference to original)
- All corrections logged with reason
```

---

## 13. Templates and Forms

### 13.1 SOP Template (Blank)

```markdown
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

## TABLE OF CONTENTS
[Auto-generate]

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

### 8.2 [Section Title]
1. [Step]
2. [Step]

## 9. QUALITY CONTROL
| QC Check | Acceptance Criteria | Frequency |
|----------|-------------------|-----------|
| | | |

## 10. DOCUMENTATION
[What records to maintain]

## 11. APPENDICES
### Appendix A: [Title]
### Appendix B: [Title]
```

### 13.2 SOP Review Form

```markdown
# SOP REVIEW FORM

**Document:** SOP-___-___
**Version Under Review:** _._
**Review Date:** ____-__-__
**Reviewer:** _______________
**Reviewer Role:** □ Technical  □ Quality  □ Final Approver

---

## REVIEW CHECKLIST

### Format and Structure
- [ ] Follows standard template
- [ ] Document number correct
- [ ] Version number appropriate
- [ ] All sections complete
- [ ] Page numbers correct
- [ ] Table of contents accurate

### Content Quality
- [ ] Purpose clearly stated
- [ ] Scope appropriately defined
- [ ] Definitions adequate
- [ ] Responsibilities clear
- [ ] References current
- [ ] Procedure steps logical
- [ ] QC requirements specified
- [ ] Documentation requirements clear

### Technical Accuracy
- [ ] Procedure is scientifically accurate
- [ ] Equipment correctly specified
- [ ] Reagents correctly identified
- [ ] Parameters within specifications
- [ ] Safety precautions adequate

### Regulatory Compliance
- [ ] Meets ISO 15189 requirements
- [ ] Meets CAP requirements
- [ ] Meets CLIA requirements
- [ ] HIPAA considerations addressed

---

## REVIEW DECISION

□ **APPROVED** - No changes required
□ **APPROVED WITH MINOR COMMENTS** - Proceed with noted corrections
□ **REVISION REQUIRED** - Return to author for revision
□ **REJECTED** - Document requires significant rework

---

## COMMENTS

| Section | Comment | Priority |
|---------|---------|----------|
| | | □ Critical □ Major □ Minor |
| | | □ Critical □ Major □ Minor |

---

**Reviewer Signature:** _________________ **Date:** __________
```

### 13.3 SOP Change Request Form

```markdown
# SOP CHANGE REQUEST FORM

**Request Number:** CR-____-____
**Date Submitted:** ____-__-__
**Requestor:** _______________
**Department:** _______________

---

## DOCUMENT INFORMATION

**Document Number:** SOP-___-___
**Current Version:** _._
**Document Title:** _______________________

---

## CHANGE DETAILS

### Change Type
□ Editorial (typo, grammar, formatting)
□ Clarification (rewording, no procedural change)
□ Minor Update (references, contacts)
□ Procedural Change (modified steps)
□ Major Revision (significant content change)
□ New Document

### Proposed Changes
[Describe the changes in detail]

### Rationale for Change
[Explain why changes are needed]

### Sections Affected
[List section numbers]

---

## IMPACT ASSESSMENT

### Regulatory Impact
□ None  □ Notification required  □ Approval required

### Training Impact
□ None  □ Read acknowledgment  □ Retraining required

### Validation Impact
□ None  □ Verification required  □ Revalidation required

### Equipment/System Impact
□ None  □ Configuration change  □ Software update

---

## APPROVAL ROUTING

| Approver | Decision | Date |
|----------|----------|------|
| Document Owner | □ Approve □ Reject | |
| Quality Manager | □ Approve □ Reject | |
| Lab Director (if major) | □ Approve □ Reject | |

---

**Requestor Signature:** _________________ **Date:** __________
```

---

## 14. Continuous Improvement Process

### 14.1 Document Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Review completion on time | >95% | Reviews completed by due date |
| Document revisions per year | <3 per document | Average revisions |
| User feedback resolution | <30 days | Time to resolve feedback |
| Training completion rate | 100% | Affected users trained |
| Audit findings related to SOPs | 0 critical | Audit results |

### 14.2 Feedback Collection

```
User Feedback Channels:
────────────────────────
1. TRPM-LIMS: QMS → Document Feedback
2. Direct email to Document Owner
3. Quality meeting discussions
4. Internal audit findings
5. External audit observations
```

### 14.3 Annual SOP Review Process

```
Annual Review Calendar
──────────────────────
Month 1-2:   Generate documents due for review
Month 2-3:   Assign reviewers, distribute documents
Month 3-6:   Complete technical reviews
Month 6-8:   Address comments, revise documents
Month 8-10:  Quality review and approval
Month 10-12: Publish, train, archive old versions
```

### 14.4 SOP Effectiveness Evaluation

| Evaluation Method | Frequency | Responsible |
|-------------------|-----------|-------------|
| User competency assessment | Per training | Supervisor |
| Deviation/error analysis | Ongoing | Quality Manager |
| Internal audit | Annual | Quality Team |
| User survey | Annual | Quality Manager |
| Process performance review | Quarterly | Lab Manager |

---

## 15. Appendices

### Appendix A: Document Type Decision Tree

```
START: Do you need to create documentation?
│
├─▶ Is it a high-level organizational statement?
│   └─▶ YES → Create POLICY (POL)
│   └─▶ NO ↓
│
├─▶ Does it describe a complete process with multiple tasks?
│   └─▶ YES → Create SOP
│   └─▶ NO ↓
│
├─▶ Does it describe step-by-step tasks for one activity?
│   └─▶ YES → Create WORK INSTRUCTION (WI)
│   └─▶ NO ↓
│
├─▶ Is it a scientific/analytical method?
│   └─▶ YES → Create PROTOCOL (PRO)
│   └─▶ NO ↓
│
├─▶ Is it a data collection tool?
│   └─▶ YES → Create FORM (FRM) or CHECKLIST (CHK)
│   └─▶ NO ↓
│
└─▶ Is it educational material?
    └─▶ YES → Create TRAINING MATERIAL (TRN)
    └─▶ NO → Consult Quality Manager
```

### Appendix B: TRPM-LIMS QMS Quick Reference

**Accessing QMS:**
```
Main Menu → QMS → Documents
```

**Document Actions:**
| Action | Navigation |
|--------|------------|
| Create Document | QMS → Documents → Add Document |
| Edit Document | QMS → Documents → [Select] → Edit |
| Create Version | QMS → Documents → [Select] → Versions → Add |
| Submit for Review | QMS → Documents → [Select] → Actions → Submit |
| View Reviews | QMS → Review Cycles |
| View Audit Trail | QMS → Documents → [Select] → Audit History |

### Appendix C: Regulatory Cross-Reference Matrix

| SOP Category | ISO 15189 | CAP | CLIA | 21 CFR 11 |
|--------------|-----------|-----|------|-----------|
| Pre-analytical | 7.1 | GEN | 493.1241 | 11.10 |
| Analytical | 7.2 | Discipline-specific | 493.1251 | 11.10 |
| Post-analytical | 7.3, 7.4 | GEN | 493.1291 | 11.10 |
| Quality Management | 8.1-8.9 | QM | 493.1701 | 11.10 |
| Equipment | 6.4 | GEN | 493.1254 | 11.10 |
| Personnel | 6.2 | GEN | 493.1451 | 11.10 |
| Document Control | 8.3 | GEN | 493.1250 | 11.10 |

### Appendix D: Common SOP Writing Mistakes to Avoid

| Mistake | Example | Correction |
|---------|---------|------------|
| Vague instructions | "Process the sample appropriately" | "Centrifuge at 3000 rpm for 10 minutes" |
| Missing decision points | "Review the results" | "If result >10, proceed to step 5; if ≤10, proceed to step 7" |
| Undefined terms | "Use adequate PPE" | "Wear lab coat, gloves, and safety glasses" |
| Inconsistent terminology | "Sample" vs "Specimen" | Use one term consistently |
| Missing QC criteria | "Run QC" | "Run Level 1 and Level 2 controls; accept if within ±2 SD" |
| No cross-references | Standalone procedure | "Refer to SOP-MOL-003 for extraction details" |
| Missing TRPM-LIMS steps | "Enter results" | "Navigate to Results → Add → Enter values in specified fields" |

### Appendix E: Glossary of Terms

| Term | Definition |
|------|------------|
| **ACMG** | American College of Medical Genetics |
| **AST** | Antibiotic Susceptibility Testing |
| **CAP** | College of American Pathologists |
| **CAPA** | Corrective and Preventive Action |
| **CLIA** | Clinical Laboratory Improvement Amendments |
| **DIN** | DNA Integrity Number |
| **GxP** | Good Practice regulations (GLP, GMP, GCP) |
| **HIPAA** | Health Insurance Portability and Accountability Act |
| **IQ/OQ/PQ** | Installation/Operational/Performance Qualification |
| **MIC** | Minimum Inhibitory Concentration |
| **NGS** | Next-Generation Sequencing |
| **QC** | Quality Control |
| **QMS** | Quality Management System |
| **SOP** | Standard Operating Procedure |
| **TAT** | Turnaround Time |
| **VUS** | Variant of Uncertain Significance |

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | _________________ | _________________ | __________ |
| Quality Manager | _________________ | _________________ | __________ |
| Laboratory Director | _________________ | _________________ | __________ |

---

**Document Control Statement:**
This document is controlled. Printed copies are for reference only. The current version is available in TRPM-LIMS QMS module. Verify version before use.

**Confidentiality:**
This document contains proprietary information. Do not distribute outside the organization without authorization.

---

*© 2026 TRPM-LIMS. All rights reserved.*
