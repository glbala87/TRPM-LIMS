# TRPM-LIMS Standard Operating Procedures (SOP)

**Document Number:** SOP-TRPM-001
**Version:** 1.0
**Effective Date:** 2026-02-16
**Review Date:** 2027-02-16

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [System Overview](#2-system-overview)
3. [User Roles and Responsibilities](#3-user-roles-and-responsibilities)
4. [System Access and Security](#4-system-access-and-security)
5. [Initial Setup Procedures](#5-initial-setup-procedures)
6. [Patient Management](#6-patient-management)
7. [Lab Order Management](#7-lab-order-management)
8. [Molecular Diagnostics Workflow](#8-molecular-diagnostics-workflow)
9. [Microbiology Module](#9-microbiology-module)
10. [Pathology Module](#10-pathology-module)
11. [Quality Control Procedures](#11-quality-control-procedures)
12. [Equipment Management](#12-equipment-management)
13. [Sample Storage Management](#13-sample-storage-management)
14. [Reagent Inventory Management](#14-reagent-inventory-management)
15. [Quality Management System (QMS)](#15-quality-management-system-qms)
16. [Compliance and Consent Management](#16-compliance-and-consent-management)
17. [Audit Trail and Logging](#17-audit-trail-and-logging)
18. [Reporting and Analytics](#18-reporting-and-analytics)
19. [Data Backup and Recovery](#19-data-backup-and-recovery)
20. [Change Control](#20-change-control)
21. [Appendices](#21-appendices)

---

## 1. Purpose and Scope

### 1.1 Purpose

This Standard Operating Procedure (SOP) document provides comprehensive guidelines for the operation, management, and maintenance of the TRPM-LIMS (Laboratory Information Management System). It ensures consistent, compliant, and efficient laboratory operations across all modules and user roles.

### 1.2 Scope

This SOP applies to:
- All laboratory personnel using TRPM-LIMS
- IT administrators responsible for system maintenance
- Quality assurance personnel
- Laboratory directors and managers
- All modules within TRPM-LIMS including:
  - Core Laboratory Management
  - Molecular Diagnostics
  - Microbiology
  - Pathology
  - Equipment Management
  - Sample Storage
  - Quality Management System
  - Analytics and Reporting

### 1.3 References

- ISO 15189:2022 - Medical Laboratories Requirements
- CAP (College of American Pathologists) Accreditation Standards
- CLIA (Clinical Laboratory Improvement Amendments) Regulations
- HIPAA Privacy and Security Rules
- 21 CFR Part 11 - Electronic Records; Electronic Signatures

---

## 2. System Overview

### 2.1 System Description

TRPM-LIMS is a comprehensive, multi-tenant Laboratory Information Management System built on Django framework. It supports clinical laboratory testing, molecular diagnostics, microbiology, pathology, and quality management.

### 2.2 Core Modules

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
| **Sensors** | Environmental monitoring |

### 2.3 Multi-Tenant Architecture

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

### 2.4 System Requirements

- **Server:** Python 3.10+, Django 6.0+
- **Database:** PostgreSQL (production) or SQLite (development)
- **Dependencies:** Pillow, python-barcode, qrcode, weasyprint

---

## 3. User Roles and Responsibilities

### 3.1 Organization-Level Roles

| Role | Permissions | Responsibilities |
|------|-------------|------------------|
| **Owner** | Full administrative access | Organization configuration, billing, user management |
| **Administrator** | Administrative access | User management, laboratory setup, settings |
| **Manager** | Supervisory access | Workflow oversight, reporting, approvals |
| **Member** | Standard access | Day-to-day operations |
| **Viewer** | Read-only access | View data, generate reports |

### 3.2 Laboratory-Level Roles

| Role | Permissions | Responsibilities |
|------|-------------|------------------|
| **Laboratory Director** | Full lab authority | Final approvals, QC oversight, compliance |
| **Laboratory Manager** | Lab administration | Staff supervision, workflow management |
| **Supervisor** | Section oversight | Section management, result review |
| **Senior Technician** | Advanced testing | Complex testing, troubleshooting, training |
| **Technician** | Standard testing | Sample processing, testing, data entry |
| **Trainee** | Limited access | Supervised operations only |
| **Viewer** | Read-only | View results and reports |

### 3.3 Role Assignment Procedure

1. **Request:** Department head submits user access request form
2. **Review:** Laboratory Manager reviews and approves role assignment
3. **Creation:** Administrator creates user account with appropriate role
4. **Training:** User completes required training modules
5. **Activation:** Account activated after training verification
6. **Documentation:** Access documented in user management records

---

## 4. System Access and Security

### 4.1 Account Creation

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

### 4.2 Password Requirements

- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character
- Password expires every 90 days
- Cannot reuse last 12 passwords

### 4.3 Login Procedure

1. Navigate to system URL
2. Enter username and password
3. Complete multi-factor authentication (if enabled)
4. System logs login with IP address and timestamp
5. User directed to default laboratory dashboard

### 4.4 Session Management

- Sessions expire after 30 minutes of inactivity
- Concurrent session limit: 2 per user
- Automatic logout on browser close

### 4.5 Account Lockout

- 5 failed login attempts triggers 15-minute lockout
- 10 failed attempts triggers 24-hour lockout
- Administrator intervention required after 15 failed attempts
- All failed attempts logged in audit trail

---

## 5. Initial Setup Procedures

### 5.1 Organization Setup

**Procedure:**
1. Navigate to Admin → Tenants → Organizations
2. Click "Add Organization"
3. Complete required fields:
   - Name and Code
   - Contact information
   - Subscription tier
   - Maximum laboratories/users/samples
4. Save organization

### 5.2 Laboratory Setup

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

### 5.3 Initial Configuration Checklist

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

## 6. Patient Management

### 6.1 Patient Registration

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

### 6.2 Patient Search

**Methods:**
- Search by OP_NO (exact match)
- Search by name (partial match)
- Search by date of birth
- Barcode scan (if equipped)

### 6.3 Patient Update

**Procedure:**
1. Search and locate patient record
2. Click to edit
3. Update required fields
4. Add note explaining change
5. Save changes
6. System logs all modifications in audit trail

### 6.4 Patient Merge (Duplicate Resolution)

**Authorization:** Laboratory Manager or higher

**Procedure:**
1. Identify duplicate patient records
2. Determine primary record (most complete)
3. Document rationale for merge
4. Execute merge (transfers all orders/samples to primary)
5. Audit trail maintains both record histories

---

## 7. Lab Order Management

### 7.1 Creating a Lab Order

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

### 7.2 Order Priorities

| Priority | Definition | TAT Target |
|----------|------------|------------|
| **STAT** | Life-threatening situation | < 1 hour |
| **Urgent** | Results needed same day | < 4 hours |
| **Routine** | Standard processing | Per test TAT |

### 7.3 Order Modification

**Authorization:** Technician or higher

**Restrictions:**
- Cannot modify orders with final results
- All changes logged in audit trail
- Reason for modification required

### 7.4 Order Cancellation

**Authorization:** Supervisor or higher

**Procedure:**
1. Open order record
2. Select "Cancel Order"
3. Enter cancellation reason
4. Confirm cancellation
5. System updates order status
6. Notifications sent to relevant parties

---

## 8. Molecular Diagnostics Workflow

### 8.1 Sample Registration

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

### 8.2 Workflow States

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

### 8.3 Status Transition Procedure

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

### 8.4 Sample Derivation

#### 8.4.1 Creating Aliquots

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

#### 8.4.2 Creating Extracts

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

### 8.5 PCR Plate Management

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

### 8.6 NGS Library Preparation

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

### 8.7 Result Entry

#### 8.7.1 PCR Results

**Procedure:**
1. Navigate to Molecular Diagnostics → Molecular Results
2. Create new result linked to sample
3. Add PCR Result entries:
   - Target gene
   - Ct value
   - Detection status (auto-determined: Ct ≤ 40 = Detected)
   - Melting temperature (if applicable)
4. Review and save

#### 8.7.2 Variant Calls

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

### 8.8 ACMG Classification Guide

| Classification | Description |
|----------------|-------------|
| **Pathogenic** | Causes disease |
| **Likely Pathogenic** | >90% certainty of pathogenicity |
| **VUS** | Variant of Uncertain Significance |
| **Likely Benign** | >90% certainty of benign nature |
| **Benign** | Does not cause disease |

### 8.9 Result Review and Approval

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

### 8.10 Report Generation

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

## 9. Microbiology Module

### 9.1 Culture Sample Registration

**Procedure:**
1. Navigate to Microbiology → Microbiology Samples
2. Create new sample linked to lab order
3. Enter sample details:
   - Specimen type (Blood, Urine, Wound, etc.)
   - Collection site
   - Culture type
4. Save sample

### 9.2 Culture Processing

**Procedure:**
1. Plate sample on appropriate media
2. Record plating details in system
3. Incubate per protocol
4. Record daily observations:
   - Growth: None, Light, Moderate, Heavy
   - Colony morphology
   - Gram stain results
5. Update sample status

### 9.3 Organism Identification

**Procedure:**
1. Select isolate for identification
2. Perform identification testing (manual or automated)
3. Record organism identification:
   - Organism name (genus/species)
   - Identification method
   - Confidence level
4. Link to taxonomic database

### 9.4 Antibiotic Susceptibility Testing (AST)

**Procedure:**
1. Navigate to Microbiology → AST Results
2. Select organism identification
3. Select AST panel appropriate for organism
4. Enter results for each antibiotic:
   - MIC value or zone size
   - Interpretation (S/I/R)
5. System applies breakpoints automatically
6. Review and save

### 9.5 Breakpoint Configuration

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

## 10. Pathology Module

### 10.1 Case Registration

**Procedure:**
1. Navigate to Pathology → Cases
2. Create new case linked to patient
3. Enter case information:
   - Specimen type
   - Clinical history
   - Pre-operative diagnosis
   - Surgeon/referring physician
4. Save case

### 10.2 Specimen Accessioning

**Procedure:**
1. Receive specimen in laboratory
2. Verify patient identification
3. Assign case number
4. Document specimen condition
5. Photograph specimen (if required)
6. Enter gross description

### 10.3 Grossing Procedure

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

### 10.4 Slide Preparation

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

### 10.5 Diagnosis Entry

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

## 11. Quality Control Procedures

### 11.1 QC Metric Definition

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

### 11.2 QC Recording

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

### 11.3 QC Failure Handling

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

### 11.4 Control Materials

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

### 11.5 Proficiency Testing

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

## 12. Equipment Management

### 12.1 Instrument Registration

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

### 12.2 Instrument Status Codes

| Status | Definition | Action Required |
|--------|------------|-----------------|
| **Active** | Operational for testing | None |
| **In Maintenance** | Undergoing maintenance | Complete maintenance |
| **Calibration Due** | Calibration scheduled | Perform calibration |
| **Out of Service** | Not operational | Repair or replace |
| **Retired** | Permanently removed | Archive records |

### 12.3 Maintenance Scheduling

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

### 12.4 Performing Maintenance

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

### 12.5 Calibration Records

**Procedure:**
1. Navigate to Equipment → Calibration Records
2. Create calibration record
3. Enter calibration details:
   - Calibrator used (with lot number)
   - Expected values
   - Measured values
   - Pass/fail criteria
4. Document results
5. Upload calibration certificate
6. Update next calibration due date
7. Save record

### 12.6 Out of Service Procedure

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

## 13. Sample Storage Management

### 13.1 Storage Unit Configuration

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

### 13.2 Sample Storage Assignment

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

### 13.3 Sample Retrieval

**Procedure:**
1. Search for sample by ID
2. Note current storage location
3. Retrieve sample from storage
4. Document retrieval in system:
   - Clear storage location, or
   - Update to new location
5. System logs retrieval event
6. Return sample to appropriate storage when finished

### 13.4 Storage Audit

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

### 13.5 Temperature Monitoring

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

## 14. Reagent Inventory Management

### 14.1 Reagent Categories

| Category | Description |
|----------|-------------|
| **General** | Common lab chemicals, buffers |
| **Molecular** | Primers, probes, polymerases |
| **Kits** | Complete test kits |
| **Controls** | QC materials |
| **Calibrators** | Calibration materials |

### 14.2 Reagent Receipt

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

### 14.3 Reagent Usage

**Procedure:**
1. Retrieve reagent from storage
2. Verify not expired
3. Document usage:
   - Navigate to reagent record
   - Update quantity on hand
4. Link usage to sample/run if applicable
5. Return to storage

### 14.4 Expiration Management

**Daily Review:**
1. Run expiration report
2. Review reagents expiring within 30 days
3. Plan usage or reorder
4. Remove expired reagents:
   - Mark as expired in system
   - Physically remove from inventory
   - Document disposal

### 14.5 Reorder Process

**Procedure:**
1. Monitor inventory levels
2. When below reorder point:
   - Generate purchase request
   - Submit for approval
   - Place order with vendor
3. Document order in system
4. Update records upon receipt

---

## 15. Quality Management System (QMS)

### 15.1 Document Categories

| Category | Description | Review Frequency |
|----------|-------------|------------------|
| **SOP** | Standard Operating Procedures | Annual |
| **Policy** | Laboratory policies | Annual |
| **Form** | Blank forms and templates | As needed |
| **Work Instruction** | Step-by-step procedures | Annual |
| **Reference** | Reference materials | As needed |

### 15.2 Document Creation

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

### 15.3 Document Review Workflow

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

### 15.4 Document Access

**Procedure:**
1. Navigate to QMS → Documents
2. Search by title, number, or category
3. View current effective version
4. Access version history if needed
5. Print controlled copies (with watermark)

### 15.5 Annual Document Review

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

## 16. Compliance and Consent Management

### 16.1 Consent Protocol Setup

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

### 16.2 Obtaining Patient Consent

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

### 16.3 Consent Status Values

| Status | Description |
|--------|-------------|
| **Pending** | Consent not yet obtained |
| **Consented** | Patient gave consent |
| **Declined** | Patient declined consent |
| **Withdrawn** | Patient withdrew consent |
| **Expired** | Protocol has expired |

### 16.4 Consent Withdrawal

**Procedure:**
1. Open patient consent record
2. Document withdrawal request
3. Enter withdrawal details:
   - Date of withdrawal
   - Reason (if provided)
   - Staff member processing
4. Set status to "Withdrawn"
5. Notify relevant personnel
6. Document impact on ongoing testing

### 16.5 Consent Verification

**Before testing genetic/research samples:**
1. Verify patient has valid consent for protocol
2. Confirm consent is not expired
3. Confirm consent not withdrawn
4. Document verification
5. Proceed only if valid consent confirmed

---

## 17. Audit Trail and Logging

### 17.1 Audit Log Contents

All system activities are logged with:
- Timestamp
- User information
- Action type (Create, Update, Delete, View, etc.)
- Object affected
- Before/after values for changes
- IP address
- User agent

### 17.2 Auditable Actions

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

### 17.3 Viewing Audit Logs

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

### 17.4 Audit Trail Retention

- Audit logs retained for minimum 10 years
- Logs archived annually
- Archives stored securely off-site
- Restoration tested annually

### 17.5 Security Incident Investigation

**Procedure:**
1. Identify timeframe of concern
2. Generate audit log report for period
3. Filter by relevant users/actions
4. Analyze access patterns
5. Document findings
6. Escalate as needed

---

## 18. Reporting and Analytics

### 18.1 Turnaround Time (TAT) Monitoring

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

### 18.2 Standard Reports

| Report | Description | Frequency |
|--------|-------------|-----------|
| **Sample Volume** | Daily/weekly/monthly sample counts | Daily |
| **TAT Compliance** | % samples meeting TAT targets | Weekly |
| **QC Summary** | QC pass/fail rates | Weekly |
| **Workload Distribution** | Samples by technician | Weekly |
| **Equipment Utilization** | Instrument usage rates | Monthly |
| **Reagent Consumption** | Reagent usage trends | Monthly |

### 18.3 Generating Reports

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

### 18.4 Custom Dashboards

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

## 19. Data Backup and Recovery

### 19.1 Backup Schedule

| Type | Frequency | Retention |
|------|-----------|-----------|
| **Full Backup** | Weekly (Sunday 2 AM) | 12 weeks |
| **Incremental Backup** | Daily (2 AM) | 4 weeks |
| **Transaction Logs** | Every 15 minutes | 1 week |

### 19.2 Backup Verification

**Weekly Procedure:**
1. Verify backup completion status
2. Check backup file integrity
3. Document verification results
4. Report any failures immediately

### 19.3 Disaster Recovery Testing

**Quarterly Procedure:**
1. Restore backup to test environment
2. Verify data integrity
3. Test critical functions
4. Document test results
5. Address any issues identified

### 19.4 Recovery Procedure

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

## 20. Change Control

### 20.1 Change Categories

| Category | Description | Approval |
|----------|-------------|----------|
| **Emergency** | Critical fix needed immediately | IT Manager + Lab Director |
| **Standard** | Normal enhancement or fix | Change Advisory Board |
| **Minor** | Minimal impact changes | IT Manager |

### 20.2 Change Request Process

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

### 20.3 Emergency Change Process

**Procedure:**
1. Document emergency situation
2. Obtain verbal approval from:
   - IT Manager
   - Laboratory Director
3. Implement fix
4. Document all actions
5. Submit retroactive change request
6. Review in next CAB meeting

### 20.4 Software Updates

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

## 21. Appendices

### Appendix A: Abbreviations

| Abbreviation | Definition |
|--------------|------------|
| AST | Antibiotic Susceptibility Testing |
| CAP | College of American Pathologists |
| CLIA | Clinical Laboratory Improvement Amendments |
| IHC | Immunohistochemistry |
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

### Appendix B: Contact Information

**System Administration:**
- IT Help Desk: [Contact Info]
- LIMS Administrator: [Contact Info]

**Laboratory Management:**
- Laboratory Director: [Contact Info]
- Laboratory Manager: [Contact Info]
- Quality Manager: [Contact Info]

**Vendor Support:**
- TRPM-LIMS Support: [Contact Info]

### Appendix C: Quick Reference - URL Endpoints

| Function | URL |
|----------|-----|
| Admin Interface | `/admin/` |
| Molecular Dashboard | `/molecular/dashboard/` |
| Sample List | `/molecular/samples/` |
| PCR Plates | `/molecular/plates/` |
| TAT Monitoring | `/molecular/tat/` |
| Report Generation | `/molecular/reports/<id>/generate/` |
| Report Download | `/molecular/reports/<id>/download/` |

### Appendix D: Workflow Status Codes

**Molecular Diagnostics:**
```
RECEIVED → EXTRACTED → AMPLIFIED → SEQUENCED → ANALYZED → REPORTED
                ↓           ↓          ↓          ↓
              FAILED     FAILED     FAILED     FAILED
```

### Appendix E: Training Checklist

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

### Appendix F: Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-16 | TRPM-LIMS Team | Initial release |

---

**Document Approval:**

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Author | _________________ | _________________ | __________ |
| Reviewer | _________________ | _________________ | __________ |
| Laboratory Director | _________________ | _________________ | __________ |
| Quality Manager | _________________ | _________________ | __________ |

---

*This document is controlled. Printed copies are for reference only. Always refer to the electronic version for the current revision.*
