# TRPM-LIMS: A Comprehensive Web-Based Laboratory Information Management System for Translational Research and Precision Medicine

---

## Manuscript

**Title:** Development and Implementation of TRPM-LIMS: An Open-Source, Multi-Tenant Laboratory Information Management System for Molecular Diagnostics, Pharmacogenomics, and Precision Medicine

**Version:** 1.0
**Date:** March 2026

---

## Abstract

Laboratory Information Management Systems (LIMS) are essential infrastructure for modern clinical and research laboratories [1, 2]. However, existing solutions often lack the specialized capabilities required for translational research and precision medicine workflows. We present TRPM-LIMS (Translational Research and Precision Medicine Laboratory Information Management System), an open-source, web-based platform designed to address the complex data management needs of molecular diagnostics laboratories, biobanks, and precision medicine programs.

TRPM-LIMS is built on Django 6.0+ with a modular, multi-tenant architecture comprising over 30 specialized applications. Key capabilities include comprehensive molecular sample tracking, variant annotation with ClinVar and gnomAD integration [9, 10], pharmacogenomics analysis with CPIC-based dosing recommendations [8], quality management system compliance, equipment and reagent inventory management, and HL7/FHIR interoperability for healthcare system integration [6, 7].

The system implements role-based access control with six predefined user roles, supports multi-laboratory operations within organizational hierarchies, and provides RESTful API access to all functionality. Compliance features address ISO 15189 [1], CAP [3], CLIA [4], and 21 CFR Part 11 [5] requirements through comprehensive audit logging, electronic signatures, and document control workflows.

TRPM-LIMS represents a significant advancement in laboratory informatics for precision medicine, offering a scalable, extensible platform that bridges the gap between research and clinical laboratory operations.

**Keywords:** Laboratory Information Management System, LIMS, Precision Medicine, Molecular Diagnostics, Pharmacogenomics, Variant Annotation, Quality Management, Django, Healthcare Interoperability, HL7, FHIR

---

## 1. Introduction

### 1.1 Background and Rationale

The advent of precision medicine has fundamentally transformed clinical laboratory operations. Modern laboratories must now manage increasingly complex workflows encompassing next-generation sequencing (NGS), polymerase chain reaction (PCR) testing, pharmacogenomic analysis, and sophisticated bioinformatics pipelines. Traditional Laboratory Information Management Systems (LIMS), designed primarily for routine clinical chemistry and hematology testing, are often inadequate for these advanced applications [2].

Several critical challenges face contemporary molecular diagnostics laboratories:

1. **Data Complexity**: Molecular testing generates vast quantities of structured and unstructured data, from raw sequencing reads to annotated variant calls, requiring sophisticated data models and storage solutions.

2. **Workflow Variability**: Unlike standardized clinical chemistry workflows, molecular diagnostics encompass diverse methodologies (PCR, NGS, FISH, microarray) with distinct processing requirements, quality control criteria, and reporting needs.

3. **Regulatory Compliance**: Laboratories must maintain compliance with multiple regulatory frameworks including ISO 15189 for medical laboratories [1], CAP accreditation requirements [3], CLIA regulations [4], and 21 CFR Part 11 for electronic records [5].

4. **Interoperability**: Healthcare systems increasingly demand seamless data exchange via HL7 and FHIR standards [6, 7], requiring LIMS platforms to support modern health information exchange protocols.

5. **Pharmacogenomics Integration**: The translation of genetic information into actionable medication guidance requires integration of pharmacogenomic databases, diplotype calling algorithms, and clinical decision support systems [8].

6. **Multi-Site Operations**: Healthcare organizations frequently operate multiple laboratories with varying capabilities, necessitating multi-tenant architectures that maintain data isolation while enabling enterprise-level reporting and oversight.

### 1.2 Existing Solutions and Limitations

Commercial LIMS platforms, while feature-rich, present several limitations for translational research and precision medicine applications:

- **Proprietary Lock-in**: Closed-source systems limit customization and integration capabilities, creating vendor dependencies that constrain laboratory flexibility.

- **Cost Barriers**: Enterprise LIMS licensing fees often exceed the budgets of academic medical centers and smaller clinical laboratories, particularly for specialized molecular diagnostics modules.

- **Workflow Rigidity**: Many commercial systems impose predetermined workflows that poorly accommodate the experimental and evolving nature of translational research protocols.

- **Limited Variant Annotation**: Few platforms provide native integration with variant databases (ClinVar, gnomAD) [9, 10] or support automated annotation pipelines essential for clinical genomics.

- **Pharmacogenomics Gaps**: Comprehensive pharmacogenomic support, including star allele calling and CPIC-based dosing recommendations [8], remains absent from most LIMS platforms.

Open-source alternatives, while addressing cost concerns, typically lack the breadth of functionality, documentation, and regulatory compliance features necessary for clinical deployment.

### 1.3 Objectives

The development of TRPM-LIMS was guided by the following objectives:

1. Create a comprehensive, open-source LIMS platform specifically designed for molecular diagnostics and precision medicine workflows.

2. Implement a multi-tenant architecture supporting organizational hierarchies with multiple laboratories.

3. Provide native variant annotation capabilities through integration with clinical genomics databases [9, 10].

4. Develop a complete pharmacogenomics module with diplotype calling and dosing recommendations based on CPIC guidelines [8].

5. Ensure regulatory compliance through robust audit logging, document control, and quality management features addressing ISO 15189 [1], CAP [3], CLIA [4], and 21 CFR Part 11 [5] requirements.

6. Enable healthcare interoperability through HL7 and FHIR standard support [6, 7].

7. Offer a flexible, extensible platform that accommodates both research and clinical laboratory operations.

---

## 2. System Architecture

### 2.1 Technology Stack

TRPM-LIMS is implemented using the Django web framework (version 6.0+) [12], chosen for its mature ecosystem, robust security features, and extensive documentation. The technology stack comprises:

**Core Framework:**
- Django 6.0+ (Python web framework) [12]
- Django REST Framework 3.15+ (RESTful API development) [13]
- drf-spectacular 0.27+ (OpenAPI schema generation)

**Database Layer:**
- SQLite (development and small deployments)
- PostgreSQL (recommended for production)
- MySQL (alternative production database)

**Task Processing:**
- Celery 5.3+ (distributed task queue)
- Redis 5.0+ (message broker and caching)

**Real-time Communication:**
- Django Channels 4.0+ (WebSocket support)

**Document Generation:**
- WeasyPrint 60.0+ (PDF generation from HTML/CSS)
- Pillow 10.0+ (image processing)

**Barcode and QR Code Generation:**
- python-barcode 0.15.1+
- qrcode 7.4+

**Healthcare Interoperability:**
- hl7apy 1.3.4+ (HL7 message parsing) [6]

**Security:**
- cryptography 41.0+ (field-level encryption)

### 2.2 Modular Application Architecture

TRPM-LIMS employs a modular architecture with over 30 Django applications organized into functional domains. This design promotes code maintainability, enables selective feature deployment, and facilitates customization for specific laboratory requirements. The complete application inventory is presented in Tables 1-6.

#### 2.2.1 Core Framework Applications

**Table 1: Core Framework Applications**

| Application | Purpose |
|-------------|---------|
| `lims` | Project configuration, URL routing, WSGI/ASGI settings |
| `users` | Authentication, authorization, role-based access control |
| `audit` | Comprehensive audit logging for all system activities |
| `api` | RESTful API endpoints with 70+ ViewSets |
| `tenants` | Multi-tenant architecture with organization/laboratory scoping |

#### 2.2.2 Laboratory Operations Applications

**Table 2: Laboratory Operations Applications**

| Application | Purpose |
|-------------|---------|
| `lab_management` | Patient registration, test ordering, result management |
| `reagents` | Inventory management for general and molecular reagents |
| `equipment` | Instrument tracking, maintenance scheduling, calibration |
| `storage` | Hierarchical sample storage with position tracking |
| `instruments` | Laboratory instrument integration (ASTM, HL7, serial) |

#### 2.2.3 Molecular Diagnostics Applications

**Table 3: Molecular Diagnostics Applications**

| Application | Purpose |
|-------------|---------|
| `molecular_diagnostics` | Comprehensive molecular testing workflows |
| `pharmacogenomics` | Drug-gene interactions and dosing recommendations |
| `single_cell` | Single-cell genomics sequencing workflows |
| `bioinformatics` | Pipeline management (Nextflow, Snakemake, WDL, CWL) |

#### 2.2.4 Specialty Testing Applications

**Table 4: Specialty Testing Applications**

| Application | Purpose |
|-------------|---------|
| `microbiology` | Culture and sensitivity testing with WHONET integration |
| `pathology` | Histopathology specimen tracking and TNM staging |

#### 2.2.5 Quality and Compliance Applications

**Table 5: Quality and Compliance Applications**

| Application | Purpose |
|-------------|---------|
| `qms` | Quality Management System with document control |
| `compliance` | Regulatory compliance tracking and documentation |

#### 2.2.6 Supporting Applications

**Table 6: Supporting Applications**

| Application | Purpose |
|-------------|---------|
| `analytics` | Real-time dashboards, KPI tracking, trend analysis |
| `messaging` | Internal messaging, notifications, activity streams |
| `data_exchange` | Import/export functionality with validation |
| `billing` | Financial management, invoicing, payment tracking |
| `projects` | Research project-based organization |
| `ontology` | Disease and terminology ontology integration |
| `sensors` | Environmental monitoring (temperature, humidity) |
| `dynamic_fields` | Custom field definitions per laboratory |
| `transfers` | Sample transfer tracking and workflows |

### 2.3 Multi-Tenant Architecture

TRPM-LIMS implements a sophisticated multi-tenant design enabling organizations to operate multiple laboratories with appropriate data isolation and access controls.

#### 2.3.1 Organizational Hierarchy

The system supports hierarchical organizational structures as illustrated in Figure 1.

**Figure 1: Organizational Hierarchy Model**

```
Organization (Hospital network, research institution)
├── Laboratory 1 (Clinical molecular laboratory)
├── Laboratory 2 (Pathology department)
├── Laboratory 3 (Research genomics core)
└── Laboratory N (Additional facilities)
```

#### 2.3.2 Tenant-Aware Data Model

The system employs a `TenantAwareModel` base class that automatically filters queries by the current laboratory context. This design ensures data isolation while maintaining a single database schema.

```python
class TenantAwareModel(models.Model):
    """Base model for multi-tenant data isolation."""
    laboratory = models.ForeignKey(
        'tenants.Laboratory',
        on_delete=models.CASCADE
    )

    objects = TenantAwareManager()

    class Meta:
        abstract = True
```

Thread-local storage maintains the current tenant context throughout request processing, enabling transparent query filtering without requiring explicit laboratory parameters in application code.

#### 2.3.3 Subscription Tiers

Organizations subscribe to service tiers that determine feature availability and resource limits, as shown in Table 7.

**Table 7: Subscription Tiers and Resource Limits**

| Tier | Laboratories | Users | Samples/Month |
|------|--------------|-------|---------------|
| FREE | 1 | 10 | 1,000 |
| BASIC | 5 | 50 | 10,000 |
| PROFESSIONAL | 20 | 200 | 100,000 |
| ENTERPRISE | Unlimited | Unlimited | SLA-based |

Per-laboratory feature flags enable granular control over module availability, allowing organizations to tailor functionality to specific laboratory needs.

### 2.4 REST API Design

TRPM-LIMS exposes comprehensive RESTful APIs [13] for all system functionality, enabling integration with external systems and supporting single-page application (SPA) frontends.

#### 2.4.1 API Structure

The API comprises over 70 ViewSets organized by functional domain, as illustrated in Figure 2.

**Figure 2: REST API Endpoint Structure**

```
/api/
├── patients/                 # Patient management
├── lab-orders/               # Test ordering
├── test-results/             # Result entry
├── molecular-samples/        # Sample tracking
├── gene-targets/             # Gene database
├── test-panels/              # Test configurations
├── molecular-results/        # Molecular results
├── variant-calls/            # Variant annotations
├── pcr-plates/               # PCR plate management
├── ngs-libraries/            # NGS workflows
├── instruments/              # Equipment inventory
├── maintenance-records/      # Maintenance tracking
├── storage-units/            # Storage management
├── micro/                    # Microbiology endpoints
├── qms/                      # Document management
├── pathology/                # Histopathology
├── pgx/                      # Pharmacogenomics
├── schema/                   # OpenAPI 3.0 schema
├── docs/                     # Swagger UI
└── redoc/                    # ReDoc documentation
```

Complete API documentation is provided in Appendix B.

#### 2.4.2 Authentication and Authorization

The API supports multiple authentication mechanisms:

- **Session Authentication**: Browser-based access with CSRF protection
- **Basic Authentication**: Simple username/password for development
- **Token Authentication**: API tokens for programmatic access (extensible to JWT)

Fine-grained permissions control access to individual endpoints based on user roles and laboratory membership (see Section 5.1).

---

## 3. Core Functional Modules

### 3.1 Patient and Order Management

#### 3.1.1 Patient Registration

The patient management module provides comprehensive demographic data capture:

- **Identification**: Unique patient identifier (OP_NO), passport number, resident card
- **Demographics**: Name, age, gender, nationality, tribe, marital status
- **Contact Information**: Phone number, associated client/clinic
- **Classification**: Special patient flags, company affiliation

Each patient record automatically generates a barcode with patient information overlay for specimen labeling and tracking.

#### 3.1.2 Test Ordering

The laboratory order system supports hierarchical test categorization across seven major domains:

1. **Hormones and Vitamins** (24 tests)
2. **Biochemistry** (30+ tests)
3. **Serology** (4 tests)
4. **Cancer Markers** (3 tests)
5. **Microbiology - Routine**
6. **Microbiology - Culture**
7. **Immunology**

Test selection automatically populates appropriate sample type and container requirements. The system tracks:

- Collection status and sufficiency
- Specimen remarks and special handling
- Auto-generated test identifiers
- Turnaround time targets

### 3.2 Molecular Diagnostics

The molecular diagnostics module represents the core functionality of TRPM-LIMS, providing comprehensive support for molecular testing workflows.

#### 3.2.1 Sample Management

**MolecularSample** entities track specimens through processing with:

- **Auto-generated Identifiers**: Format `MOL-YYYYMMDD-XXXX`
- **Workflow Status Tracking**: Eight-state lifecycle (see Figure 3)
- **Priority Classification**: ROUTINE, URGENT, STAT
- **Derivation Tracking**: ORIGINAL, ALIQUOT, EXTRACT, LIBRARY, DISSECTION, AMPLICON
- **Quality Metrics**: Volume, concentration, integrity assessment
- **Storage Integration**: Linked storage positions with retrieval tracking

**Figure 3: Molecular Sample Workflow States**

```
RECEIVED → EXTRACTED → AMPLIFIED → SEQUENCED → ANALYZED → REPORTED
                                                    ↓
                                    CANCELLED ←──── FAILED
```

Sample parent-child relationships enable complete lineage tracking from original specimen through derived aliquots, extracts, and libraries.

#### 3.2.2 Gene Targets and Test Panels

The system maintains a comprehensive gene database with:

- Gene symbols and full names
- Genomic coordinates (chromosome-start-end format)
- Transcript identifiers (NM_xxxxxx.x format)
- Clinical significance documentation

**MolecularTestPanel** entities define testing configurations as described in Table 8.

**Table 8: MolecularTestPanel Configuration Attributes**

| Attribute | Description |
|-----------|-------------|
| Test Type | PCR, RT-PCR, NGS, Sanger, FISH, Microarray, MLPA, Fragment Analysis |
| Gene Targets | Many-to-many relationship with genes |
| Reagent Kits | Associated reagent requirements |
| Sample Requirements | Volume and concentration minimums |
| Turnaround Time | SLA target in hours |
| Workflow Definition | Processing steps and dependencies |

#### 3.2.3 Result Management

**MolecularResult** entities capture testing outcomes with:

- **Status Workflow**: PENDING → PRELIMINARY → FINAL (or AMENDED, CANCELLED)
- **Interpretations**: POSITIVE, NEGATIVE, INDETERMINATE, NOT_TESTED, INCONCLUSIVE
- **Approval Chain**: Performed by → Reviewed by → Approved by
- **Clinical Content**: Significance, recommendations, limitations, disclaimers
- **Report Generation**: PDF storage with template-based formatting

**PCRResult** subentities (for qPCR/RT-PCR) capture:
- Cycle threshold (Ct) values
- Detection status per target gene
- Multiple results per molecular result

#### 3.2.4 Variant Calling and Annotation

The **VariantCall** model provides comprehensive variant annotation following ACMG/AMP guidelines [11], as detailed in Table 9.

**Table 9: VariantCall Model Fields**

| Field | Description |
|-------|-------------|
| Genomic Coordinates | Chromosome, position, reference/alternate alleles |
| HGVS Nomenclature | cDNA (c.) and protein (p.) notation |
| dbSNP Identifier | rs IDs for known variants |
| ACMG Classification | Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign [11] |
| Population Frequencies | gnomAD allele frequencies [10] |
| Clinical Significance | ClinVar annotations [9] |

The variant annotation system integrates with external databases through caching services (see Section 4.1):

**AnnotationCache Model:**
- Normalized variant keys (chr-pos-ref-alt or rsID)
- ClinVar cached data with fetch timestamps [9]
- gnomAD cached data with fetch timestamps [10]
- Configurable TTL (default: 30 days)
- Cache hit tracking for performance optimization

#### 3.2.5 Batch Processing

**InstrumentRun** entities manage batch operations:

- Unique identifiers: `RUN-YYYYMMDD-XXXXXX`
- Status tracking: PLANNED, IN_PROGRESS, COMPLETED, FAILED, CANCELLED
- Protocol and version documentation
- Start/end timestamps with duration calculation
- Run parameters (JSON for instrument-specific settings)

**PCRPlate** entities support:
- 96-well and 384-well plate formats
- Barcode tracking
- Individual well management
- Links to instrument runs

**NGS Workflow Entities:**
- `NGSLibrary`: Library preparation tracking
- `NGSPool`: Pooling and multiplexing management
- Index/barcode assignment

#### 3.2.6 Quality Control

The QC subsystem ensures result validity:

**QCMetricDefinition**: Defines acceptable ranges with warning and critical thresholds

**ControlSample**: Reference materials with lot tracking and expiration management

**QCRecord**: Links QC materials to runs with:
- Measured values
- Automatic pass/fail determination
- Operator and timestamp tracking

### 3.3 Pharmacogenomics Module

TRPM-LIMS includes a comprehensive pharmacogenomics (PGx) module supporting translation of genetic information into actionable medication guidance based on CPIC guidelines [8].

#### 3.3.1 Gene and Allele Database

**PGxGene Model:**
- Pharmacogene definitions (CYP2D6, CYP2C19, DPYD, TPMT, SLCO1B1, etc.)
- Gene categories: CYP, TRANSPORTER, PHASE2, TARGET, HLA, OTHER
- Copy number relevance flags
- Reference database identifiers (Ensembl, NCBI, PharmVar)

**StarAllele Model:**
- Star allele definitions (*1, *2, *17, etc.)
- Function classification: NORMAL, INCREASED, DECREASED, NO_FUNCTION, UNCERTAIN
- Activity scores (0, 0.5, 1, 2, etc.)
- Defining variants (stored as JSON)
- Population frequencies by ancestry
- Reference IDs (PharmVar, CPIC) [8]

#### 3.3.2 Diplotype and Phenotype Prediction

**Diplotype Model:**
- Combines star alleles into diplotype calls (e.g., *1/*2)
- Phenotype prediction from diplotype
- Metabolizer classifications: ULTRARAPID, RAPID, NORMAL, INTERMEDIATE, POOR
- Clinical recommendations linked to phenotype

#### 3.3.3 Dosing Recommendations

**DosageRecommendation Model:**
- CPIC-based dosing guidance [8]
- Drug-specific recommendations by phenotype
- Evidence level tracking (FDA Level A/B/C)
- Alternative medication suggestions
- Drug interaction information

#### 3.3.4 Patient Results

**PGxResult Model:**
- Patient genotyping results
- Diplotype calls per gene
- Phenotype interpretation
- Linked medications with recommendations
- Clinical significance summary

### 3.4 Microbiology Module

#### 3.4.1 Taxonomic Database

Complete microbial taxonomy hierarchy:
- Kingdom → Phylum → Class → Order → Family → Genus → Species

**Organism Model:**
- Organism types: BACTERIA, FUNGUS, PARASITE, VIRUS, MYCOBACTERIA, YEAST, MOLD
- Morphology: COCCI, BACILLI, COCCOBACILLI, SPIROCHETE, PLEOMORPHIC
- Gram classification: POSITIVE, NEGATIVE, VARIABLE, NA
- Biochemical characteristics
- WHONET and SNOMED-CT coding integration

#### 3.4.2 Antibiotic Susceptibility Testing

**Antibiotic Model**: Drug definitions with pharmacological classification

**ASTPanel Model**: Configurable panels for organism-specific testing

**Breakpoint Model**: EUCAST/CLSI breakpoint definitions for S/I/R interpretation

**ASTResult Model:**
- Susceptibility interpretations (Susceptible, Intermediate, Resistant)
- MIC values
- Quality flags for unusual patterns

### 3.5 Pathology Module

#### 3.5.1 Histology Specimen Tracking

**Histology Model** tracks specimens through 13 processing states as shown in Figure 4.

**Figure 4: Histology Processing Workflow**

```
RECEIVED → GROSSING → PROCESSING → EMBEDDING → CUTTING →
STAINING → COVERSLIPPING → QC → READY → IN_REVIEW →
REPORTED → ARCHIVED
```

Additional tracking includes:
- Fixation types: FORMALIN, ALCOHOL, FROZEN, FRESH, OTHER
- Tissue quality: Tumor cell percentage, necrosis percentage
- Adequacy assessment: ADEQUATE, SUBOPTIMAL, INADEQUATE
- Gross description with measurements and weight
- Surgical and accession number assignment

#### 3.5.2 Block and Slide Management

**HistologyBlock Model**: Tissue block tracking with cassette identification

**HistologySlide Model**: Slide management with staining protocol tracking (H&E, IHC, special stains)

#### 3.5.3 Pathology Reporting

- TNM staging (Tumor, Node, Metastasis)
- Diagnosis codes
- Addendum tracking for report amendments
- Multi-level approval workflow

### 3.6 Equipment Management

#### 3.6.1 Instrument Inventory

**Instrument Model:**
- Serial number and asset number tracking
- Firmware/software version management
- Installation, purchase, warranty dates
- Status: ACTIVE, MAINTENANCE, CALIBRATION, REPAIR, RETIRED, OUT_OF_SERVICE
- Technical specifications (JSON)

**Calculated Properties:**
- `is_maintenance_due`: Scheduled maintenance overdue
- `is_calibration_due`: Calibration interval exceeded
- `is_available`: Currently operational
- `warranty_valid`: Within warranty period

#### 3.6.2 Maintenance Management

**MaintenanceRecord Model:**
- Maintenance types: PREVENTIVE, CORRECTIVE, CALIBRATION, QUALIFICATION, REPAIR, UPGRADE, INSPECTION
- Status workflow: SCHEDULED → IN_PROGRESS → COMPLETED
- Calibration certificate tracking
- Maintenance log history

### 3.7 Storage Management

#### 3.7.1 Hierarchical Storage Model

The storage system implements a hierarchical model as illustrated in Figure 5.

**Figure 5: Hierarchical Storage Architecture**

```
StorageUnit (Freezer, Refrigerator, LN2 Tank)
└── StorageRack (Configurable rows/columns)
    └── StoragePosition (Individual positions)
        └── Sample (Stored specimen)
```

**StorageUnit Model:**
- Unit types: -80°C Freezer, -20°C Freezer, Refrigerator (2-8°C), Liquid N₂ Tank, Room Temperature, Incubator
- Status: ACTIVE, MAINTENANCE, FULL, OUT_OF_SERVICE
- Temperature monitoring: minimum, maximum, target values
- Alarm and monitoring flags

**Calculated Properties:**
- `total_positions`: Total storage capacity
- `occupied_positions`: Currently used positions
- `available_positions`: Remaining capacity

#### 3.7.2 Audit Trail

**StorageLog Model:**
- Complete movement history
- User tracking
- Timestamp recording
- State before/after

### 3.8 Quality Management System

#### 3.8.1 Document Control

**Document Model:**
- Unique identifiers: `DOC-YYYYMMDD-XXXX`
- Editor types: RICHTEXT, MARKDOWN, HTML, PDF, EXTERNAL_LINK
- Version control with complete history
- Author and reader access control
- Review schedule management
- Template support

**DocumentVersion Model:**
- Version numbering
- Content storage
- Change tracking
- Approval status: DRAFT, IN_REVIEW, APPROVED, PUBLISHED, SUPERSEDED

#### 3.8.2 Review Workflows

**DocumentReviewCycle Model:**
- Multi-step approval processes
- Reviewer assignments with deadlines
- Status tracking through review stages

**DocumentCategory Model:**
- Document classification (SOP, Policy, Protocol, Work Instruction)
- Default review intervals per category

### 3.9 Bioinformatics Integration

#### 3.9.1 Pipeline Management

**Pipeline Model:**
- Pipeline types: VARIANT_CALLING, RNA_SEQ, CHIP_SEQ, METAGENOMICS, SINGLE_CELL, WGS, WES, AMPLICON, CUSTOM
- Executor frameworks: NEXTFLOW, SNAKEMAKE, WDL, CWL, BASH, PYTHON
- Repository URL and configuration file storage
- Default compute requirements: CPU cores, memory (GB), time (hours)
- Version tracking

**PipelineParameter Model:**
- Parameter types: STRING, INTEGER, FLOAT, BOOLEAN, FILE, DIRECTORY, SELECT
- Default values and choice lists
- Required field designation

#### 3.9.2 Service Requests

**BioinformaticsService Model:**
- Pipeline execution requests
- Sample/instrument run associations
- Job status: REQUESTED → APPROVED → QUEUED → RUNNING → COMPLETED
- Priority levels: LOW, NORMAL, HIGH, URGENT
- Parameter passing for flexible configurations
- Output and delivery tracking

---

## 4. Data Integration and Interoperability

### 4.1 Variant Annotation Services

TRPM-LIMS implements automated variant annotation through integration with clinical genomics databases [9, 10].

#### 4.1.1 ClinVar Integration

The **ClinVarService** queries the NCBI ClinVar database [9] for:
- Clinical significance classifications
- Review status and evidence levels
- Associated conditions
- Submission history

Results are cached with configurable TTL to minimize API calls while maintaining current information.

#### 4.1.2 gnomAD Integration

Population allele frequency data from the Genome Aggregation Database (gnomAD) [10] provides:
- Global allele frequencies
- Population-specific frequencies
- Filtering allele frequencies
- Homozygote counts

#### 4.1.3 Annotation Workflow

The annotation workflow is illustrated in Figure 6.

**Figure 6: Variant Annotation Workflow**

```
Variant Identified
       ↓
Check Annotation Cache
       ↓
Cache Hit? → Return Cached Data
       ↓ (Cache Miss)
Query ClinVar API [9]
Query gnomAD API [10]
       ↓
Cache Results
       ↓
Return Annotation Data
```

Batch processing capabilities enable efficient annotation of large variant sets from NGS analyses.

### 4.2 HL7 and FHIR Interoperability

#### 4.2.1 HL7 v2.x Support

The **InstrumentConnection** model supports laboratory instrument integration via ASTM E1381/E1394 and HL7 v2.x protocols [6]:

- Connection types: TCP Server, TCP Client, Serial Port
- Network configuration: Host, port, timeout, retry settings
- Serial port configuration: Baud rate, parity, data bits
- Message logging and audit trails

#### 4.2.2 FHIR Integration

TRPM-LIMS is designed for FHIR R4 compatibility [7], supporting:
- Patient resource mapping
- DiagnosticReport generation
- Observation resources for results
- Specimen tracking resources
- PractitionerRole for user mapping

### 4.3 Data Import/Export Framework

#### 4.3.1 Import Capabilities

**ImportJob Model:**
- Supported data types: PATIENTS, SAMPLES, RESULTS, REAGENTS, EQUIPMENT
- File formats: CSV, XLSX
- Status workflow: PENDING → VALIDATING → VALIDATED → IMPORTING → COMPLETED
- Validation before import with error reporting
- Column mapping flexibility
- Options: skip_duplicates, update_existing, dry_run

**ImportedRecord Model:**
- Row-level tracking
- Status: SUCCESS, FAILED, SKIPPED, DUPLICATE
- Error messages for failed records

#### 4.3.2 Export Capabilities

**ExportTemplate Model:**
- Saved templates for repeatable exports
- Supported types: PATIENTS, SAMPLES, RESULTS, LAB_ORDERS, REAGENTS, EQUIPMENT, AUDIT_LOGS
- Configurable column selection
- Filter criteria storage

---

## 5. Security, Compliance, and Audit

### 5.1 Authentication and Authorization

#### 5.1.1 Role-Based Access Control

TRPM-LIMS implements comprehensive RBAC with six predefined roles as described in Table 10.

**Table 10: Role-Based Access Control Definitions**

| Role | Description | Key Permissions |
|------|-------------|-----------------|
| ADMIN | System administrator | Full system access, user management, configuration |
| LAB_MANAGER | Laboratory manager | Operations management, result approval, analytics |
| SUPERVISOR | Technical supervisor | Technician oversight, result review, equipment |
| TECHNICIAN | Laboratory technician | Sample processing, result entry, equipment operation |
| READER | View-only access | Data viewing, report access |
| PHYSICIAN | Clinical user | Patient results, test requisition |

#### 5.1.2 Multi-Level Membership

**Organization Membership Roles:**
- OWNER, ADMIN, MANAGER, MEMBER, VIEWER

**Laboratory Membership Roles:**
- LAB_DIRECTOR, LAB_MANAGER, SUPERVISOR, SENIOR_TECHNICIAN, TECHNICIAN, TRAINEE, VIEWER

This dual-level membership enables users to have different roles across laboratories within an organization.

#### 5.1.3 Permission Matrix

Granular permissions control:
- Patient management (view/edit/create/delete)
- Sample handling (view/edit/create/delete)
- Result entry and approval
- Equipment and reagent management
- Storage management
- Analytics and export
- System configuration
- Audit log access

### 5.2 Audit Logging

#### 5.2.1 Comprehensive Audit Trail

**AuditLog Model** captures 14 action types as detailed in Table 11.

**Table 11: Audit Log Action Types**

| Action | Description |
|--------|-------------|
| CREATE | New record creation |
| UPDATE | Record modification |
| DELETE | Record deletion |
| VIEW | Record access |
| EXPORT | Data export |
| IMPORT | Data import |
| LOGIN | User authentication |
| LOGOUT | Session termination |
| LOGIN_FAILED | Failed authentication attempt |
| APPROVE | Approval action |
| REJECT | Rejection action |
| TRANSITION | Status change |
| PRINT | Document printing |
| EMAIL | Email transmission |

#### 5.2.2 Audit Data Captured

Each audit entry includes:
- User identification
- Timestamp
- Action type
- Affected model and record
- Field-level changes (old vs. new values)
- Request context: IP address, user agent, request path

### 5.3 Regulatory Compliance

#### 5.3.1 Supported Standards

TRPM-LIMS provides compliance features for the regulatory standards listed in Table 12.

**Table 12: Supported Regulatory Standards**

| Standard | Scope |
|----------|-------|
| ISO 15189:2022 [1] | Medical laboratory requirements |
| ISO 17025:2017 | Testing and calibration laboratories |
| CAP [3] | College of American Pathologists accreditation |
| CLIA [4] | Clinical Laboratory Improvement Amendments (42 CFR 493) |
| 21 CFR Part 11 [5] | Electronic records and signatures |
| FDA GxP | Good Practice requirements |
| HIPAA | Health information privacy and security |

#### 5.3.2 Compliance Features

- **Electronic Signatures**: Approval workflows with user authentication [5]
- **Audit Trails**: Immutable logging of all system activities [5]
- **Document Control**: Version management with approval workflows
- **Training Records**: User competency documentation
- **Equipment Qualification**: IQ/OQ/PQ documentation
- **Quality Control**: QC metrics with acceptance criteria
- **CAPA Management**: Corrective and preventive action tracking

### 5.4 Data Security

#### 5.4.1 Security Measures

- **Password Management**: Secure password hashing with Django's auth system [12]
- **Session Security**: Configurable session timeout, secure cookie settings
- **HTTPS Enforcement**: SSL redirect in production
- **CSRF Protection**: Cross-site request forgery prevention
- **Field-Level Encryption**: Cryptography library for sensitive data

#### 5.4.2 Production Security Checklist

```python
# Required production settings
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']
ALLOWED_HOSTS = ['your-domain.com']
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

Additional configuration details are provided in Appendix D.

---

## 6. Analytics and Reporting

### 6.1 Real-Time Dashboards

The analytics module provides operational visibility through:

- **Sample Statistics**: Volume tracking, status distribution, aging analysis
- **TAT Monitoring**: Turnaround time compliance with SLA tracking (see Section 6.2)
- **Quality Metrics**: QC pass rates, failure analysis
- **Equipment Utilization**: Instrument usage and availability
- **User Activity**: Workload distribution, productivity metrics

### 6.2 Turnaround Time Management

#### 6.2.1 TAT Status Classification

The system classifies sample TAT status according to the criteria in Table 13.

**Table 13: TAT Status Classification**

| Status | Condition |
|--------|-----------|
| On Track | < 75% of TAT target |
| Warning | 75-90% of TAT target |
| Critical | 90-100% of TAT target |
| Overdue | > 100% of TAT target |

#### 6.2.2 TAT Features

- Real-time status calculation per sample
- At-risk sample identification dashboard
- Historical TAT trend analysis
- Per-panel TAT statistics
- Bottleneck identification

### 6.3 Report Generation

#### 6.3.1 Report Types

- **Patient Reports**: Final laboratory reports with results
- **QC Reports**: Quality control summaries and trend analysis
- **Operational Reports**: Workload, productivity, and utilization metrics
- **Compliance Reports**: Audit summaries, training status, document reviews

#### 6.3.2 Report Formats

- PDF generation via WeasyPrint
- HTML templates with CSS styling
- Barcode and QR code embedding
- Digital signature blocks

---

## 7. Deployment Architecture

### 7.1 Development Environment

Detailed installation instructions are provided in Appendix A. A quick start guide is shown below:

```bash
# Clone repository
git clone https://github.com/organization/trpm-lims.git
cd trpm-lims

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### 7.2 Production Deployment

#### 7.2.1 Docker Support

TRPM-LIMS includes Docker configuration for containerized deployment:

```dockerfile
# Multi-stage build for production
FROM python:3.12-slim

# System dependencies for WeasyPrint
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 libffi-dev shared-mime-info

# Application setup
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
WORKDIR /app

# Static file collection
RUN python manage.py collectstatic --noinput

# Production server
CMD ["gunicorn", "lims.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### 7.2.2 Docker Compose

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SETTINGS_MODULE=lims.settings
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE_URL=${DATABASE_URL}
    volumes:
      - media:/app/media
      - static:/app/static

  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=trpm_lims
      - POSTGRES_USER=lims_user
      - POSTGRES_PASSWORD=${DB_PASSWORD}

  redis:
    image: redis:7

  celery:
    build: .
    command: celery -A lims worker -l info
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
  media:
  static:
```

### 7.3 Database Recommendations

Database selection guidance is provided in Table 14.

**Table 14: Database Recommendations by Deployment Size**

| Deployment Size | Recommended Database |
|-----------------|---------------------|
| Development | SQLite |
| Small (< 50K samples) | PostgreSQL |
| Medium (50K-500K samples) | PostgreSQL with connection pooling |
| Large (> 500K samples) | PostgreSQL with read replicas |

---

## 8. Extensibility and Customization

### 8.1 Dynamic Fields

The `dynamic_fields` application enables per-laboratory custom field definitions:

- Add custom attributes to core models
- Configure field types (text, number, date, select, multi-select)
- Set validation rules
- Control visibility and required status

### 8.2 Workflow Customization

The workflow engine supports custom processing paths:

- Define workflow steps with dependencies
- Configure status transitions
- Set validation requirements
- Customize approval chains

### 8.3 API Extensions

Third-party integrations can leverage:

- RESTful API with OpenAPI documentation [13] (see Appendix B)
- WebSocket support for real-time updates
- Celery tasks for background processing
- Django signals for event-driven extensions

### 8.4 Theming and Branding

- Configurable laboratory name and branding
- Custom logo placement
- Report template customization
- Email template configuration

---

## 9. Discussion

### 9.1 Addressing Key Challenges

TRPM-LIMS addresses the critical challenges identified in Section 1.1:

**Data Complexity**: The modular architecture with specialized models for molecular samples, variants, and pharmacogenomics provides structured data management appropriate for complex testing workflows.

**Workflow Variability**: Configurable test panels (Table 8), workflow definitions, and dynamic fields accommodate diverse testing methodologies without code modification.

**Regulatory Compliance**: Comprehensive audit logging (Table 11), document control, and approval workflows support ISO 15189 [1], CAP [3], CLIA [4], and 21 CFR Part 11 [5] requirements (see Table 12).

**Interoperability**: HL7 [6] and FHIR [7] support enables integration with healthcare information systems, while the REST API [13] facilitates custom integrations (Figure 2).

**Pharmacogenomics**: The dedicated PGx module with star allele definitions, diplotype calling, and CPIC-based dosing recommendations [8] translates genetic data into clinical guidance.

**Multi-Site Operations**: The multi-tenant architecture (Figure 1, Table 7) enables enterprise deployments with appropriate data isolation and access controls.

### 9.2 Comparison with Existing Solutions

A comparative analysis of TRPM-LIMS against alternative solutions is presented in Table 15.

**Table 15: Feature Comparison with Existing Solutions**

| Feature | TRPM-LIMS | Commercial LIMS | Other Open-Source |
|---------|-----------|-----------------|-------------------|
| Molecular Diagnostics | Comprehensive | Varies | Limited |
| Variant Annotation | Native [9, 10] | Add-on | Rare |
| Pharmacogenomics | Full Module [8] | Limited | Absent |
| Multi-Tenant | Yes | Some | Rare |
| HL7/FHIR [6, 7] | Supported | Usually | Varies |
| QMS | Integrated | Sometimes | Rare |
| Cost | Free | $$$$+ | Free |
| Customization | Full | Limited | Full |

### 9.3 Limitations and Future Work

Current limitations and planned enhancements include:

1. **User Interface**: The current implementation focuses on backend functionality; a modern SPA frontend (React, Vue) would improve user experience.

2. **Machine Learning**: Integration of ML models for QC prediction, variant prioritization, and workflow optimization represents a future direction.

3. **Cloud-Native Deployment**: Kubernetes configurations and cloud-optimized architectures would enhance scalability.

4. **Mobile Access**: Native mobile applications for sample collection and result review would extend system accessibility.

5. **Additional Integrations**: Expanded instrument drivers and EHR integrations would broaden applicability.

---

## 10. Conclusion

TRPM-LIMS represents a comprehensive solution for laboratory information management in translational research and precision medicine settings. The system's modular architecture, spanning over 30 specialized applications (Tables 1-6), addresses the complex data management requirements of modern molecular diagnostics laboratories.

Key contributions include:

1. **Integrated Molecular Diagnostics**: Complete workflows from sample receipt through variant annotation and reporting (Figures 3, 6).

2. **Pharmacogenomics Module**: Comprehensive support for translating genetic data into medication guidance through star allele calling, diplotype prediction, and CPIC-based dosing recommendations [8].

3. **Multi-Tenant Architecture**: Enterprise-ready design supporting organizational hierarchies with multiple laboratories (Figure 1, Table 7).

4. **Regulatory Compliance**: Built-in features addressing ISO 15189 [1], CAP [3], CLIA [4], and 21 CFR Part 11 [5] requirements (Table 12).

5. **Healthcare Interoperability**: HL7 [6] and FHIR [7] support enabling integration with clinical information systems.

6. **Open-Source Availability**: Freely available platform eliminating licensing barriers while enabling community-driven enhancement.

TRPM-LIMS bridges the gap between research and clinical laboratory operations, providing a scalable platform for the evolving needs of precision medicine programs. The system's extensible design ensures adaptability to future requirements while maintaining the stability necessary for regulated laboratory environments.

---

## Acknowledgments

The development of TRPM-LIMS was informed by best practices from clinical laboratory operations, molecular diagnostics workflows, and healthcare informatics standards. The project builds upon the Django ecosystem [12] and numerous open-source libraries that enable sophisticated web application development.

---

## References

1. ISO 15189:2022 - Medical laboratories - Requirements for quality and competence.

2. Clinical and Laboratory Standards Institute (CLSI). Laboratory Information Management System (LIMS); Approved Guideline. AUTO-11.

3. College of American Pathologists (CAP) Laboratory Accreditation Program.

4. Code of Federal Regulations, Title 42, Part 493 - Laboratory Requirements (CLIA).

5. Code of Federal Regulations, Title 21, Part 11 - Electronic Records; Electronic Signatures.

6. HL7 International. HL7 Version 2 Product Suite. https://www.hl7.org/implement/standards/product_section.cfm?section=13

7. HL7 International. HL7 FHIR R4. https://www.hl7.org/fhir/

8. Clinical Pharmacogenetics Implementation Consortium (CPIC). https://cpicpgx.org/

9. ClinVar. National Center for Biotechnology Information. https://www.ncbi.nlm.nih.gov/clinvar/

10. Genome Aggregation Database (gnomAD). https://gnomad.broadinstitute.org/

11. Richards S, et al. Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the American College of Medical Genetics and Genomics and the Association for Molecular Pathology. Genet Med. 2015;17(5):405-424.

12. Django Software Foundation. Django Documentation. https://docs.djangoproject.com/

13. Django REST Framework. https://www.django-rest-framework.org/

---

## Appendices

### Appendix A: Installation Guide

Detailed installation instructions are available in the project README.md file. The installation process includes:

1. **System Requirements**: Python 3.10+, PostgreSQL 13+ (recommended for production)
2. **Virtual Environment Setup**: Creation and activation of isolated Python environment
3. **Dependency Installation**: pip installation of requirements.txt
4. **Database Configuration**: Connection settings and migration execution
5. **Static File Collection**: Aggregation of static assets for web serving
6. **Superuser Creation**: Initial administrative account setup
7. **Service Configuration**: Celery worker and Redis setup for background tasks

### Appendix B: API Reference

Complete API documentation is available at `/api/docs/` (Swagger UI) and `/api/redoc/` (ReDoc) when the application is running.

The API provides:
- **70+ ViewSets** covering all system functionality
- **OpenAPI 3.0 Schema** available at `/api/schema/`
- **Authentication Options**: Session, Basic, Token authentication
- **Filtering**: DjangoFilterBackend, SearchFilter, OrderingFilter
- **Pagination**: Configurable page size (default: 25 items)

### Appendix C: Database Schema

Entity-relationship diagrams and complete schema documentation are maintained in the project's technical documentation. Key schema characteristics include:

- **30+ Django Applications** with interconnected models
- **Tenant-Aware Models** with automatic laboratory scoping
- **Audit Trail Integration** on critical models
- **Soft Delete Support** where appropriate
- **JSON Fields** for flexible configuration storage

### Appendix D: Configuration Reference

All configurable settings are documented in the `lims/settings.py` file with inline comments. Key configuration categories include:

1. **Database Settings**: Connection parameters, pooling options
2. **Security Settings**: Secret key, allowed hosts, CSRF/cookie security
3. **Authentication**: Session timeout, password validators
4. **API Settings**: Pagination, throttling, authentication classes
5. **Celery Settings**: Broker URL, result backend, task serialization
6. **Annotation Services**: ClinVar/gnomAD API configuration, cache TTL
7. **Storage Settings**: Media/static file locations
8. **Email Settings**: SMTP configuration for notifications

---

## Supplementary Information

### Supplementary Table S1: Complete Test Category Listing

The laboratory order system supports the following test categories (referenced in Section 3.1.2):

| Category | Number of Tests | Examples |
|----------|-----------------|----------|
| Hormones and Vitamins | 24 | TSH, T3, T4, Vitamin D, B12 |
| Biochemistry | 30+ | Liver function, Renal function, Lipid profile |
| Serology | 4 | HIV, HBV, HCV, Syphilis |
| Cancer Markers | 3 | PSA, CA-125, AFP |
| Microbiology - Routine | Variable | Urinalysis, Stool examination |
| Microbiology - Culture | Variable | Blood culture, Urine culture |
| Immunology | Variable | ANA, Anti-dsDNA |

### Supplementary Figure S1: Complete System Architecture Diagram

A comprehensive system architecture diagram showing all 30+ applications and their relationships is available in the project repository at `/docs/architecture/system_diagram.png`.

### Supplementary Data S1: API Endpoint Inventory

A complete listing of all 70+ API endpoints with their HTTP methods, parameters, and response schemas is available through the OpenAPI schema at `/api/schema/` (see Appendix B).

---

## Abbreviations

**Table 16: List of Abbreviations**

| Abbreviation | Full Term |
|--------------|-----------|
| ACMG | American College of Medical Genetics and Genomics |
| API | Application Programming Interface |
| AST | Antibiotic Susceptibility Testing |
| CAP | College of American Pathologists |
| CLIA | Clinical Laboratory Improvement Amendments |
| CPIC | Clinical Pharmacogenetics Implementation Consortium |
| CSRF | Cross-Site Request Forgery |
| CWL | Common Workflow Language |
| EHR | Electronic Health Record |
| EUCAST | European Committee on Antimicrobial Susceptibility Testing |
| FHIR | Fast Healthcare Interoperability Resources |
| FISH | Fluorescence In Situ Hybridization |
| gnomAD | Genome Aggregation Database |
| HGVS | Human Genome Variation Society |
| HL7 | Health Level Seven International |
| IHC | Immunohistochemistry |
| IQ/OQ/PQ | Installation/Operational/Performance Qualification |
| JSON | JavaScript Object Notation |
| LIMS | Laboratory Information Management System |
| MIC | Minimum Inhibitory Concentration |
| ML | Machine Learning |
| MLPA | Multiplex Ligation-dependent Probe Amplification |
| NGS | Next-Generation Sequencing |
| PCR | Polymerase Chain Reaction |
| PGx | Pharmacogenomics |
| QC | Quality Control |
| QMS | Quality Management System |
| RBAC | Role-Based Access Control |
| REST | Representational State Transfer |
| RT-PCR | Reverse Transcription Polymerase Chain Reaction |
| SLA | Service Level Agreement |
| SNOMED-CT | Systematized Nomenclature of Medicine - Clinical Terms |
| SOP | Standard Operating Procedure |
| SPA | Single-Page Application |
| TAT | Turnaround Time |
| TNM | Tumor-Node-Metastasis (staging system) |
| TTL | Time To Live |
| VUS | Variant of Uncertain Significance |
| WDL | Workflow Description Language |
| WES | Whole Exome Sequencing |
| WGS | Whole Genome Sequencing |
| WHONET | World Health Organization Network for Antimicrobial Resistance Surveillance |
| WSGI | Web Server Gateway Interface |

---

**Document Information:**
- **Title:** TRPM-LIMS Technical Manuscript
- **Version:** 1.1
- **Created:** March 2026
- **Last Updated:** March 2026
- **Status:** Final
- **Classification:** Public

---

*End of Manuscript*
