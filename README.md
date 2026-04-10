# TRPM-LIMS - Laboratory Information Management System

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-6.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-red.svg)](https://www.django-rest-framework.org/)
[![Tests](https://img.shields.io/badge/Tests-62%20passing-brightgreen.svg)]()
[![Deploy Check](https://img.shields.io/badge/Deploy%20Check-0%20issues-brightgreen.svg)]()
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)]()
[![HL7](https://img.shields.io/badge/HL7-v2.5.1-orange.svg)](https://www.hl7.org/)
[![FHIR](https://img.shields.io/badge/FHIR-R4-blueviolet.svg)](https://www.hl7.org/fhir/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, production-ready, multi-tenant Laboratory Information Management System built with Django 6.0. Designed for clinical laboratories, research institutions, and diagnostic facilities with support for molecular diagnostics, microbiology, pathology, pharmacogenomics, single-cell genomics, bioinformatics pipelines, and more.

TRPM-LIMS provides **26 integrated modules**, **150+ data models**, **184 templates**, **60+ REST API endpoints**, and **39 service classes** with full CRUD interfaces, JWT authentication, TOTP MFA, role-based access control, 21 CFR Part 11 electronic signatures, HL7/FHIR interoperability, automated backups, and multi-tenant data isolation.

---

## Table of Contents

- [Features](#features)
- [Key Architectural Features](#key-architectural-features)
- [Architecture](#architecture)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Modules Overview](#modules-overview)
- [REST API](#rest-api)
- [URL Endpoints](#url-endpoints)
- [Configuration](#configuration)
- [Usage Guide](#usage-guide)
- [Production Deployment](#production-deployment)
- [Testing](#testing)
- [Compliance](#compliance)
- [Troubleshooting](#troubleshooting)
- [Make Commands](#make-commands)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

### Core Laboratory Management
- **Patient Management** - Patient registration with auto-generated barcodes and QR codes, client tracking, patient autocomplete search
- **Lab Orders** - Test ordering with sample tracking, test categories, container types, and status workflow
- **Test Results** - Result entry, validation, and clinical reporting
- **Label Generation** - Barcode/label generation service for patients and samples
- **Forms** - PatientForm, LabOrderForm, TestResultForm, PatientSearchForm with validation

### Reagent & Inventory Management
- **General Reagents** - Stock management with lot tracking, expiration alerts, and usage monitoring
- **Molecular Reagents** - Primers, probes, and kits with sequence data, melting temperature (Tm), and GC content
- **Usage Tracking** - Reagent consumption tracking per test/sample
- **Low-Stock Alerts** - Automatic low-stock monitoring and alerts
- **Stability Tracking** - Stability-after-opening calculations for opened reagents
- **Panel Linking** - Link molecular reagents to specific test panels

### Multi-Tenant Architecture
- **Organizations** - Top-level entities (hospital networks, research institutions) with subscription tiers (Free, Basic, Professional, Enterprise)
- **Laboratories** - Multi-lab support with complete data isolation; types include Clinical, Research, Molecular, Pathology, Microbiology, Biobank, Genomics
- **Organization Roles** - Owner, Administrator, Manager, Member, Viewer
- **Laboratory Roles** - Lab Director, Lab Manager, Supervisor, Senior Technician, Technician, Trainee, Viewer
- **Feature Flags** - Per-laboratory feature enablement via JSON configuration
- **Laboratory Switching** - Seamless context switching with session-based tenant context
- **Thread-Local Scoping** - TenantContext and TenantAwareManager for automatic query filtering
- **Resource Limits** - Max laboratories, max users, max samples/month per organization tier

### User Management & RBAC
- **JWT Authentication** - Token-based API auth (15-min access, 1-day refresh, rotation + blacklist)
- **TOTP MFA** - Multi-factor authentication via django-otp; enforced when `ENABLE_HIPAA_MODE=True`
- **Password Security** - 12-char minimum, 90-day aging, last-5 reuse prevention, forced change on expiry
- **Profile Management** - User profiles with edit capability
- **6 Predefined Roles** - Admin, Lab Manager, Supervisor, Technician, Reader, Physician
- **21 Granular Permissions** - Patient, Sample, Result, Equipment, Reagent, Storage, Analytics, User management, Audit access controls
- **RBAC Matrix** - Formal role-to-permission mapping documented in `docs/compliance/rbac_matrix.md`
- **User Administration** - Create, edit, delete users with role assignment (staff-only)
- **Session Tracking** - UserSession model for login history and active session monitoring
- **Account Locking** - Automatic account lockout after failed login attempts
- **Electronic Signatures** - Immutable, integrity-hashed signatures per 21 CFR Part 11 (when `ENABLE_PART11=True`)

### Molecular Diagnostics
- **Sample Workflow** - State machine tracking (Received → Extracted → Amplified → Sequenced → Analyzed → Reported) with workflow engine
- **Test Panels** - PCR, RT-PCR, NGS, Sanger, FISH, Microarray support with configurable test methods
- **Gene Targets** - Gene and variant database with HGVS nomenclature
- **Batch Processing** - 96/384-well plate management with visual editor and batch item tracking
- **NGS Library Tracking** - Library prep, pooling, and sequencing workflow
- **Quality Control** - QC metrics, parameters, controls, and validation rules with auto pass/fail
- **Sample QC & Prep** - Dedicated SampleQC and SamplePrep tracking models
- **Structured Results** - PCR Ct values, variant calls with ACMG classification (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign)
- **Variant Annotation** - ClinVar integration, gnomAD population frequency lookup, clinical significance annotation
- **Reflex Rules Engine** - Configurable reflex testing rules with automated trigger actions
- **Samplesheet Generation** - Automated samplesheet generation for sequencing instruments
- **PDF Reports** - Professional clinical reports with WeasyPrint
- **Workflow Engine** - Service-layer workflow management with valid transition enforcement
- **TAT Monitor** - Turnaround time monitoring service with SLA tracking
- **11 Admin Configurations** - Comprehensive Django admin for all molecular models

### Pharmacogenomics (PGx)
- **Gene Dashboard** - PGx gene database (CYP2D6, CYP2C19, CYP2C9, CYP3A4, DPYD, TPMT, UGT1A1, SLCO1B1)
- **Gene Categories** - Cytochrome P450, Drug Transporter, Phase II Enzyme, Drug Target, HLA Gene
- **Star Alleles** - Allele definitions with activity scores, function levels (Normal, Increased, Decreased, No Function), and population frequencies by ethnicity
- **Phenotype Classification** - PM, IM, NM, RM, UM with activity score ranges
- **Diplotype Calling** - Automated diplotype calling with DiplotypeService, copy number variation support, hybrid allele detection
- **Drug Database** - Drug catalog with 12 drug classes (Analgesic, Antidepressant, Anticoagulant, Antipsychotic, Cardiovascular, Oncology, Immunosuppressant, etc.)
- **Drug-Gene Interactions** - CPIC-based evidence levels (1A Strong → 4 Insufficient), interaction types (PK, PD, ADR, Efficacy, Dosing)
- **Dosing Recommendations** - Phenotype-specific actions (Standard, Reduce, Increase, Avoid, Alternative, Monitor, Caution) with recommendation strength
- **RecommendationService** - Automated clinical summary generation from PGx results
- **Clinical Reports** - PGx-specific PDF report generation with drug recommendation tables

### Microbiology
- **Culture & Sensitivity** - Organism identification and antimicrobial susceptibility testing
- **Antibiotic Panels** - Configurable AST panels with breakpoints (MIC/Zone diameter)
- **Organism Database** - Taxonomic classification with Gram stain support
- **Interpretation Engine** - Automated AST result interpretation service

### Pathology
- **Histopathology Cases** - Case management with grossing-to-final-diagnosis workflow
- **Block & Slide Tracking** - Physical specimen tracking through processing
- **Staining Protocols** - IHC (immunohistochemistry) and special stains management
- **Addenda** - Report amendments with full audit trail
- **TNM Staging** - Cancer staging service for pathology cases
- **Report Service** - Pathology-specific report generation

### Quality Management System (QMS)
- **Document Control** - Version-controlled SOPs, policies, and procedures
- **Folder Organization** - Hierarchical document folder structure
- **Review Workflows** - Multi-step document approval cycles with review workflow service
- **Training Records** - Staff training documentation and tracking
- **Internal Audits** - Quality audit management
- **Audit Trails** - Complete document change history

### Bioinformatics
- **Pipeline Management** - Define and manage analysis pipelines with versioning and configurable parameters
- **Pipeline Executors** - Nextflow, Snakemake, WDL/Cromwell, CWL, Bash, Python
- **Pipeline Types** - Variant Calling, RNA-Seq, ChIP-Seq, Metagenomics, Single-Cell, WGS, WES, Amplicon
- **Service Catalog** - Bioinformatics services with SLA tracking
- **Job Tracking** - Pipeline execution with status monitoring, resource tracking (CPU/memory usage)
- **Result Delivery** - Structured result delivery management with client access

### Analytics & Reporting
- **Configurable Dashboards** - Widget-based dashboard system (KPI widgets, chart widgets)
- **Saved Queries** - Reusable data queries for repeated analysis
- **Report Generation** - PDF and Excel report generation with status lifecycle
- **Scheduled Reports** - Automated report generation and delivery on configurable schedules
- **KPI Metrics** - Historical performance snapshots with indexed queries
- **Alert System** - Configurable alerts with severity levels and status tracking
- **TAT Monitoring** - Turnaround time tracking against SLA targets
- **Services** - MetricsService, ChartDataService, SampleStatisticsService

### Billing & Invoicing
- **Price Lists** - Configurable service pricing with volume discount tiers
- **Client Management** - Client database with types (Hospital, Clinic, Research, Private, Individual) and contact tracking
- **Invoice Generation** - Invoice creation with line items, tax calculation, and status workflow (Draft → Pending → Sent → Partial → Paid → Overdue → Cancelled → Refunded)
- **Payment Tracking** - Payment recording with multiple methods (Cash, Check, Card, Bank Transfer, Online) and reconciliation
- **Quote Management** - Quotation request generation and conversion to invoices
- **Billing Dashboard** - Overview of revenue, outstanding invoices, and payment status

### Project Management
- **Project Lifecycle** - Full status workflow: Draft → Pending Approval → Active → On Hold → Completed → Cancelled → Archived
- **Project Categories** - Configurable project categorization with codes
- **Team Members** - Role-based membership (PI, Co-PI, Researcher, Technician, Coordinator, Analyst, Viewer) with granular permissions (add samples, edit samples, view results, manage members)
- **Sample Association** - Link molecular samples to projects with external sample IDs, subject IDs, and consent tracking
- **Milestones** - Project milestone tracking with target dates, completion dates, and status (Pending, In Progress, Completed, Delayed, Cancelled)
- **Document Management** - Project-specific document storage with types (Protocol, Ethics, Consent, SOP, Report)
- **Ethics & Compliance** - Ethics approval number, approval/expiry dates, ethics documents, consent form management
- **Funding Tracking** - Funding source, grant number, budget tracking
- **Target Tracking** - Target sample count and participant count goals

### Environmental Monitoring (Sensors)
- **Sensor Dashboard** - Real-time monitoring overview with critical/warning alert counts
- **Sensor Types** - Temperature, Humidity, CO2, O2, Pressure, Door Status, Power Status, Custom
- **Device Management** - Configure monitoring devices with warning/critical min/max thresholds, calibration dates, reading intervals
- **Reading History** - Timestamped sensor readings with auto-status calculation based on device thresholds
- **Alert System** - Automatic alerts on threshold breach (Warning/Critical) with notification rules
- **Alert Lifecycle** - Active → Acknowledged → Resolved with user attribution and resolution notes
- **Notification Rules** - AlertNotificationRule model for routing alerts to users, emails, and SMS
- **API Endpoint** - REST endpoint (`/sensors/api/readings/`) for IoT sensor data submission

### Single-Cell Genomics
- **Sample Types** - Configurable single-cell sample types with target cell counts and minimum viability thresholds
- **Sample Tracking** - Full workflow: Received → Dissociated → Cell Sorted → Loaded on Chip → Cells Captured → Lysed → Library Preparation → Sequenced → Analyzed → Failed
- **Platform Support** - 10x Genomics 3'/5' GEX, 10x Multiome, 10x Visium, Smart-seq2, Smart-seq3, Drop-seq, BD Rhapsody, Parse Biosciences
- **Cell Metrics** - Initial count, concentration, viability, target/actual recovery, nuclei isolation
- **Capture Tracking** - Chip ID, position, capture time
- **Quality Metrics** - Mean reads/cell, median genes/cell, median UMI/cell, sequencing saturation
- **Library Management** - GEX, V(D)J T-cell, V(D)J B-cell, ATAC-seq, Feature Barcode, Custom library types
- **Feature Barcodes** - CITE-seq antibodies, cell hashtags, CRISPR guides with barcode sequences, target antigens, vendor/catalog info
- **Barcode Panels** - Grouped feature barcode panels for experiments
- **Cluster Analysis** - Cell cluster tracking with cluster IDs, cell types, marker genes, mean genes/UMI per cluster

### Equipment Management
- **Instrument Tracking** - Full CRUD with serial numbers, locations, status, warranty tracking
- **Instrument Types** - Categorize instruments by type with create/update views
- **Maintenance Records** - Preventive maintenance, calibration, repairs, and certification with full lifecycle (create, view, update, delete)
- **Maintenance Scheduling** - Due date tracking and calibration certificate management
- **Search & Filter** - Find instruments by name, serial number, type, or status

### Sample Storage
- **Storage Units** - Freezers (-80°C, -20°C), refrigerators (2-8°C), nitrogen tanks, room temperature, incubators with temperature range tracking
- **Rack Management** - Row/column rack configuration within units with position-level tracking
- **Storage Positions** - Individual position tracking within racks
- **Audit Logging** - Complete storage event history (moves, disposals, additions)
- **Search & Filter** - Locate samples by unit, type, or status

### Messaging & Notifications
- **Internal Inbox** - Threaded conversation system
- **Thread Detail** - Message thread views with reply capability
- **Notification System** - System notification list with read/unread tracking
- **Notification Service** - Automated notification delivery service
- **Activity Service** - User activity logging and tracking service

### Dynamic Fields
- **Field Categories** - Organize custom fields by category
- **14 Field Types** - Text, TextArea, Integer, Decimal, Boolean, Date, DateTime, Select, MultiSelect, File, URL, Email, Phone, JSON
- **Validation** - Regex pattern validation, required field enforcement
- **Display Options** - show_in_list, show_in_form, searchable flags per field
- **Generic Linking** - ContentType-based generic foreign key for attaching fields to any model
- **Field Templates** - Group field definitions into reusable templates for consistent data capture
- **Custom Field Values** - Store values with type-appropriate validation

### Ontology & Terminology
- **Ontology Sources** - ICD-10, SNOMED-CT, HPO, and custom ontology source management with versioning
- **Disease Ontology** - Hierarchical disease terms with parent/child relationships, clinical significance, affected systems, and synonym support
- **Anatomical Sites** - Body location database organized by body system
- **Clinical Indications** - Testing indications linked to diseases and test panels
- **Organism Taxonomy** - Scientific/common names, NCBI taxonomy IDs, host/pathogen classification
- **Patient Diagnoses** - Link patients to disease terms with diagnosis date, primary/confirmed flags, anatomical site
- **AJAX Search** - Real-time disease term search API endpoint

### Audit & Compliance

#### Audit Trail
- **System-Wide Logging** - AuditLog and AuditTrail models for comprehensive change tracking
- **Before/After Values** - Capture field-level changes with previous and new values
- **IP & User-Agent Capture** - Track source of all changes for forensic analysis
- **Generic Tracking** - ContentType-based linking for auditing any model
- **Audit Dashboard** - Web-based audit log viewing with search and filtering
- **Helper Methods** - log_action, log_create, log_update, log_delete, log_login, log_logout

#### Compliance Management
- **Consent Protocols** - IRB-approved consent protocol management
- **7 Protocol Types** - General, Genetic, Biobanking, Clinical Trial, Data Sharing, Pediatric, Emergency
- **Consent Workflow** - give_consent(), withdraw_consent(), decline_consent() methods with status tracking
- **Witness Tracking** - Record consent witnesses for regulatory compliance
- **Legal Representative** - Support for consenting on behalf of minors/incapacitated patients
- **Consent Validation** - Automated consent validity checking

### Data Exchange & Interoperability

#### HL7/FHIR Integration
- **HL7 v2.5.1 Support** - Full HL7 v2.5.1 message parsing and generation via hl7apy
- **FHIR R4/STU3** - FHIR resource mapping with FHIRService
- **Transport Protocols** - MLLP (Minimum Lower Layer Protocol), HTTP/REST, SFTP, File-based exchange
- **Message Logging** - Complete message log with retry logic and error tracking
- **External Systems** - Configure connections to external LIS, EHR, and HIS systems

#### Import/Export
- **CSV/XLSX Import** - Bulk data import with validation and error tracking per record
- **Export Templates** - Reusable export definitions for consistent data extraction
- **Export Jobs** - Background export operation tracking
- **Template Management** - Download and manage import templates
- **Validation API** - Pre-import data validation endpoints

### Laboratory Instrument Integration
- **ASTM Protocol** - ASTM E1381/E1394 protocol support for instrument communication
- **Connection Types** - TCP socket and Serial (RS-232) connectivity
- **Message Types** - ASTM Header/Patient/Order/Result/Comment and HL7 ORM/ORU/QRY/ACK/ADT messages
- **Checksum Validation** - Automatic message checksum calculation and verification
- **Worklist Export** - Generate and send worklists to instruments
- **Result Processing** - Automated result import from instruments via result_processor service
- **Connection Manager** - Service for managing active instrument connections
- **Result Importer** - Automated parsing and import of instrument result messages

### Sample Transfers
- **Transfer Management** - Full CRUD for sample transfers with auto-generated transfer numbers
- **Dispatch/Receive Workflow** - Separate dispatch and receiving views with status tracking
- **Shipment Conditions** - Ambient, Refrigerated (2-8°C), Frozen (-20°C), Deep Frozen (-80°C), Dry Ice, Liquid Nitrogen
- **Transfer Items** - Individual item tracking within transfers
- **Movement History** - Complete sample movement audit trail
- **Overdue Detection** - Automatic detection of overdue transfers
- **Discrepancy Reporting** - Report and track discrepancies between sent and received items
- **Tracking Service** - Dedicated tracking.py service for transfer monitoring

---

## Key Architectural Features

| Feature | Description |
|---------|-------------|
| **Multi-Tenant Isolation** | Organization → Laboratory hierarchy with TenantAwareManager for automatic query scoping |
| **HL7/FHIR Interoperability** | HL7 v2.5.1 and FHIR R4/STU3 support with MLLP, HTTP, SFTP transports |
| **ASTM Instrument Integration** | ASTM E1381/E1394 protocol for direct analyzer communication |
| **Variant Annotation Pipeline** | ClinVar and gnomAD integration for automated variant classification |
| **Reflex Rules Engine** | Configurable automated reflex testing triggered by result conditions |
| **Pharmacogenomics (CPIC)** | CPIC-aligned drug-gene interaction system with diplotype calling |
| **Role-Based Access Control** | 6 predefined roles with 21 granular permissions |
| **Service Layer Architecture** | 39 service files across 11 apps separating business logic from views |
| **Dynamic Field System** | 14 field types with generic foreign keys for extensible data capture on any model |
| **GenericForeignKey Patterns** | Used in AuditLog, DynamicFields, and other models for flexible entity linking |
| **Abstract Base Models** | TenantAwareModel for automatic laboratory scoping on inherited models |
| **Background Task Processing** | Celery + Redis for scheduled reports, exports, and long-running jobs |
| **WebSocket Support** | Django Channels for real-time sensor data and notifications |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Bootstrap 5)                   │
│  184 Templates │ Font Awesome │ Responsive │ DataTables          │
├─────────────────────────────────────────────────────────────────┤
│                     Django 6.0 Framework                         │
│  Class-Based Views │ LoginRequiredMixin │ Template Inheritance   │
├─────────────────────────────────────────────────────────────────┤
│                    REST API (DRF 3.15+)                          │
│  60+ ViewSets │ drf-spectacular (OpenAPI) │ django-filter        │
├─────────────────────────────────────────────────────────────────┤
│              Multi-Tenant Layer (tenants app)                    │
│  TenantContext │ TenantAwareManager │ Laboratory Scoping         │
├─────────────────────────────────────────────────────────────────┤
│       Service Layer (39 services across 11 apps)                 │
│  Workflow Engine │ ClinVar/gnomAD │ HL7/FHIR │ ASTM │ Reports  │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│  Core    │ Molecular│ Clinical │ Support  │ Infrastructure      │
│  ──────  │ ──────── │ ──────── │ ──────── │ ──────────────      │
│  Patients│ Samples  │ Micro    │ Billing  │ Audit               │
│  Orders  │ Panels   │ Path     │ Projects │ Compliance          │
│  Results │ NGS/QC   │ PGx      │ Sensors  │ Data Exchange       │
│  Reagents│ Variants │ Ontology │ Messaging│ HL7/FHIR            │
│  Storage │ Reflex   │          │ QMS      │ ASTM Instruments    │
│  Equip.  │ Bioinf.  │          │ SingleCell│ Transfers          │
│          │ Annot.   │          │ DynFields│                      │
├──────────┴──────────┴──────────┴──────────┴────────────────────┤
│                    Database (SQLite / PostgreSQL)                 │
│                     150+ Models │ Indexed                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Requirements

- Python 3.12+
- Django 6.0+
- PostgreSQL 16+ (production) or SQLite (local dev only)
- Redis 7+ (Celery broker, caching)
- Docker & Docker Compose (recommended for deployment)

### Key dependencies

| Category | Packages |
|---|---|
| **Core** | Django 6.0, djangorestframework, drf-spectacular |
| **Auth** | djangorestframework-simplejwt (JWT), django-otp (TOTP MFA) |
| **Config** | django-environ (12-factor env vars) |
| **Database** | psycopg2-binary (PostgreSQL) |
| **Static files** | whitenoise |
| **PDF reports** | weasyprint |
| **Background tasks** | celery, redis |
| **Monitoring** | sentry-sdk |
| **Testing** | pytest, pytest-django, pytest-cov, coverage |
| **Load testing** | locust |

See `requirements.txt` for the full list.

---

## Quick Start

### Local development

```bash
# Clone the repository
git clone https://github.com/glbala87/TRPM-LIMS.git
cd TRPM-LIMS

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
make install  # or: pip install -r requirements.txt

# Run migrations (SQLite for local dev)
DEBUG=True python manage.py migrate

# Create superuser
DEBUG=True python manage.py createsuperuser

# Start development server
make run  # or: DEBUG=True python manage.py runserver 0.0.0.0:8000
```

### Production (Docker)

```bash
# Configure environment
cp .env.example .env
nano .env   # Set SECRET_KEY, DATABASE_URL, ALLOWED_HOSTS, etc.

# Generate a SECRET_KEY
make secretkey

# Build and launch the full stack (app + Postgres + Redis + nginx + Celery)
make docker-build
make docker-up

# Apply migrations and create admin
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser

# Verify
docker compose exec app python manage.py check --deploy
```

### Access the application

| URL | Description |
|---|---|
| http://localhost:8000/ | Web interface (lab management home) |
| http://localhost:8000/admin/ | Django admin panel |
| http://localhost:8000/api/ | REST API root |
| http://localhost:8000/api/docs/ | Swagger API documentation |
| http://localhost:8000/api/redoc/ | ReDoc API documentation |

### API authentication (JWT)

```bash
# Obtain a token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your-password"}'
# Returns: {"access": "eyJ...", "refresh": "eyJ..."}

# Use the token
curl http://localhost:8000/api/patients/ \
  -H "Authorization: Bearer <access-token>"

# Refresh when expired (access tokens expire in 15 minutes)
curl -X POST http://localhost:8000/api/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh-token>"}'
```

---

## Installation

### 1. Clone and set up

```bash
git clone https://github.com/glbala87/TRPM-LIMS.git
cd TRPM-LIMS
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. WeasyPrint system dependencies (for PDF reports)

PDF generation is optional — the app runs fine without it, but report generation will fail.

**macOS:**
```bash
brew install pango libffi
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libgdk-pixbuf2.0-0 libffi-dev
```

### 3. Environment configuration

All settings are loaded from environment variables via `django-environ`. For local dev, the defaults work out of the box (SQLite, DEBUG=True). For anything else:

```bash
cp .env.example .env
nano .env
```

Key variables (see `.env.example` for the full list):

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | dev fallback (insecure) | **Required in production** |
| `DEBUG` | `False` | Set `True` for local dev |
| `DATABASE_URL` | SQLite | e.g., `postgres://user:pass@host:5432/trpm_lims` |
| `ALLOWED_HOSTS` | `[]` | Comma-separated hostnames |
| `CELERY_BROKER_URL` | `redis://localhost:6379/0` | Redis for background tasks |
| `ENABLE_PART11` | `False` | 21 CFR Part 11 e-signature enforcement |
| `ENABLE_HIPAA_MODE` | `False` | MFA enforcement + HIPAA controls |
| `PASSWORD_MAX_AGE_DAYS` | `90` | Force password change interval (0 disables) |
| `SENTRY_DSN` | empty | Sentry error monitoring (optional) |

### 4. Run migrations and create admin

```bash
DEBUG=True python manage.py migrate
DEBUG=True python manage.py createsuperuser
```

### 5. Run the dev server

```bash
make run
# or: DEBUG=True python manage.py runserver 0.0.0.0:8000
```

### 6. Optional: Redis & Celery (background tasks)

```bash
redis-server &
celery -A lims worker -l info &
celery -A lims beat -l info &
```

---

## Project Structure

```
TRPM-LIMS/
├── lims/                           # Project settings & configuration
│   ├── settings.py                 # Django settings (33 installed apps)
│   ├── urls.py                     # Root URL router (27 app includes)
│   └── wsgi.py                     # WSGI application
│
├── tenants/                        # Multi-tenant architecture
│   ├── models.py                   # Organization, Laboratory, Memberships, TenantContext, TenantAwareManager
│   ├── views.py                    # Organization/Laboratory CRUD, lab switching
│   ├── urls.py                     # 5 URL patterns
│   └── templates/tenants/          # 4 templates
│
├── users/                          # User management & RBAC
│   ├── models.py                   # Role (6 roles, 21 permissions), UserProfile, UserSession
│   ├── views.py                    # Auth views, profile, user/role admin (13 views)
│   ├── urls.py                     # 12 URL patterns
│   └── templates/users/            # 9 templates
│
├── lab_management/                 # Core lab module
│   ├── models.py                   # Patient, LabOrder, TestResult
│   ├── views.py                    # 6 views (patient list/registration, orders, results, autocomplete)
│   ├── forms.py                    # PatientForm, LabOrderForm, TestResultForm, PatientSearchForm
│   ├── admin.py                    # Custom admin with barcode generation
│   ├── services/                   # label_generator.py
│   └── templates/                  # 6 templates
│
├── reagents/                       # Reagent inventory
│   ├── models.py                   # Reagent, ReagentUsage, MolecularReagent
│   ├── views.py                    # reagent_list view
│   └── admin.py                    # Reagent admin
│
├── molecular_diagnostics/          # Molecular testing (core module)
│   ├── models/                     # 8 model files:
│   │   ├── samples.py              # MolecularSample, SampleQC, SamplePrep
│   │   ├── panels.py               # MolecularTestPanel, GeneTarget
│   │   ├── batches.py              # ProcessingBatch, BatchItem
│   │   ├── workflows.py            # Workflow, WorkflowStep
│   │   ├── qc.py                   # QCResult, QCParameter
│   │   ├── results.py              # MolecularResult, VariantCall, Interpretation
│   │   ├── annotations.py          # VariantAnnotation, ClinicalSignificance
│   │   └── reflex_rules.py         # ReflexRule, ReflexAction
│   ├── views/                      # 12 view files
│   ├── services/                   # 7 services:
│   │   ├── workflow_engine.py      # State machine with valid transitions
│   │   ├── tat_monitor.py          # Turnaround time monitoring
│   │   ├── report_generator.py     # PDF clinical reports (WeasyPrint)
│   │   ├── annotation_service.py   # Variant annotation pipeline
│   │   ├── clinvar_service.py      # ClinVar database integration
│   │   ├── gnomad_service.py       # gnomAD population frequencies
│   │   ├── samplesheet_generator.py# Instrument samplesheet generation
│   │   └── reflex_engine.py        # Reflex testing automation
│   ├── forms/                      # Dynamic forms
│   ├── admin/                      # 11 admin configuration files
│   └── templates/                  # Report templates, dashboards
│
├── pharmacogenomics/               # Pharmacogenomics module
│   ├── models.py                   # PGxGene, StarAllele, Phenotype, Drug, DrugGeneInteraction,
│   │                               #   DrugRecommendation, PGxPanel, PGxResult, PGxDrugResult (9 models)
│   ├── services.py                 # DiplotypeService, RecommendationService
│   ├── views.py                    # 7 views (gene dashboard, gene/drug detail, results, panels)
│   ├── urls.py                     # 7 URL patterns
│   └── templates/pharmacogenomics/ # 8 templates (7 views + PDF report)
│
├── microbiology/                   # Microbiology module
│   ├── models/                     # Culture, Organism, Antibiotic, AST models
│   ├── views.py                    # 6 views with search
│   ├── services/                   # interpretation_engine.py
│   ├── urls.py                     # 6 URL patterns
│   └── templates/microbiology/     # 6 templates
│
├── pathology/                      # Pathology module
│   ├── models/                     # Specimen, Histology, IHC models
│   ├── views.py                    # 4 views (cases, histology)
│   ├── services/                   # staging_service.py, report_service.py
│   ├── urls.py                     # 4 URL patterns
│   └── templates/pathology/        # 4 templates
│
├── ontology/                       # Clinical terminology
│   ├── models.py                   # OntologySource, DiseaseOntology, AnatomicalSite,
│   │                               #   ClinicalIndication, Organism, PatientDiagnosis (6 models)
│   ├── views.py                    # 9 views + AJAX disease_search
│   ├── urls.py                     # 10 URL patterns
│   └── templates/ontology/         # 9 templates
│
├── bioinformatics/                 # Bioinformatics pipelines
│   ├── models.py                   # Pipeline, PipelineParameter, BioinformaticsService,
│   │                               #   AnalysisJob, AnalysisResult, ServiceDelivery (6 models)
│   ├── views.py                    # Pipeline, service, job, result, delivery views
│   ├── urls.py                     # URL patterns
│   └── templates/bioinformatics/   # 9 templates
│
├── single_cell/                    # Single-cell genomics
│   ├── models.py                   # SingleCellSampleType, SingleCellSample, FeatureBarcode,
│   │                               #   FeatureBarcodePanel, SingleCellLibrary, CellCluster (6 models)
│   ├── views.py                    # 9 views
│   ├── urls.py                     # 10 URL patterns
│   └── templates/single_cell/      # 9 templates
│
├── analytics/                      # Analytics & dashboards
│   ├── models.py                   # DashboardWidget, SavedQuery, Report, KPIMetric,
│   │                               #   Alert, ScheduledReport (6 models)
│   ├── admin.py                    # Full admin with list_display, filters, search
│   ├── services/                   # metrics.py, charts.py, statistics.py
│   ├── views.py                    # Dashboard views
│   └── templates/analytics/        # Dashboard templates
│
├── billing/                        # Billing & invoicing
│   ├── models.py                   # PriceList, ServicePrice, Client, Invoice,
│   │                               #   InvoiceItem, Payment, QuotationRequest (7 models)
│   ├── views.py                    # 14+ views (dashboard, CRUD for all entities)
│   ├── urls.py                     # URL patterns
│   └── templates/billing/          # 14 templates
│
├── projects/                       # Research projects
│   ├── models.py                   # ProjectCategory, Project, ProjectMember, ProjectSample,
│   │                               #   ProjectMilestone, ProjectDocument (6 models)
│   ├── views.py                    # 14 views (full lifecycle management)
│   ├── urls.py                     # 13 URL patterns
│   └── templates/projects/         # 12 templates
│
├── sensors/                        # Environmental monitoring
│   ├── models.py                   # SensorType, MonitoringDevice, SensorReading,
│   │                               #   SensorAlert, AlertNotificationRule (5 models)
│   ├── views.py                    # 9 views + submit_reading API endpoint
│   ├── urls.py                     # 11 URL patterns
│   └── templates/sensors/          # 8 templates
│
├── equipment/                      # Instrument management
│   ├── models.py                   # InstrumentType, Instrument, MaintenanceRecord
│   ├── forms.py                    # Forms with date picker widgets
│   ├── views.py                    # 13 views (full CRUD with search/filter)
│   ├── urls.py                     # 14 URL patterns
│   └── templates/equipment/        # 10 templates
│
├── storage/                        # Sample storage
│   ├── models.py                   # StorageUnit, StorageRack, StoragePosition, StorageLog (4 models)
│   ├── forms.py                    # Forms for units and racks
│   ├── views.py                    # 8 views with search/filter
│   ├── urls.py                     # 8 URL patterns
│   └── templates/storage/          # 6 templates
│
├── messaging/                      # Internal messaging
│   ├── models.py                   # Thread, Message, Notification
│   ├── views.py                    # Inbox, thread, notification views
│   ├── services/                   # notification_service.py, activity_service.py
│   ├── urls.py                     # 3 URL patterns
│   └── templates/messaging/        # 3 templates
│
├── qms/                            # Quality Management System
│   ├── models.py                   # Document, DocumentVersion, DocumentReviewCycle, Folder, TrainingRecord
│   ├── views.py                    # 4 views (documents, folders)
│   ├── services/                   # review_workflow.py
│   ├── urls.py                     # 4 URL patterns
│   └── templates/qms/              # 4 templates
│
├── dynamic_fields/                 # Custom field definitions
│   ├── models.py                   # FieldCategory, CustomFieldDefinition, CustomFieldValue, FieldTemplate (4 models)
│   ├── views.py                    # Category, field, template views
│   ├── urls.py                     # URL patterns
│   └── templates/dynamic_fields/   # 7 templates
│
├── audit/                          # Audit logging
│   ├── models.py                   # AuditLog (GenericFK, before/after, IP tracking), AuditTrail
│   ├── views.py                    # Log views, dashboard, activity APIs
│   ├── urls.py                     # URL patterns
│   └── templates/audit/            # 4 templates
│
├── compliance/                     # Compliance & consent management
│   ├── models.py                   # ConsentProtocol (7 types, IRB), PatientConsent (workflow methods)
│   ├── views.py                    # 10+ views with consent APIs
│   ├── urls.py                     # URL patterns
│   └── templates/compliance/       # 8 templates
│
├── data_exchange/                  # Data exchange & interoperability
│   ├── models.py                   # ImportJob, ImportedRecord, ExportTemplate, ExportJob, ExternalSystem, MessageLog (6 models)
│   ├── views.py                    # 8+ views with validation APIs
│   ├── services/                   # fhir_service.py, hl7_service.py, message_router.py
│   ├── importers/                  # Data type-specific importers
│   ├── exporters/                  # Data type-specific exporters
│   ├── urls.py                     # URL patterns
│   └── templates/data_exchange/    # 7 templates
│
├── instruments/                    # Laboratory instrument integration
│   ├── models.py                   # InstrumentConnection (ASTM/HL7), MessageLog, WorklistExport (3 models)
│   ├── views.py                    # 7+ views with communication APIs
│   ├── services/                   # connection_manager.py, result_processor.py,
│   │                               #   worklist_exporter.py, result_importer.py
│   ├── urls.py                     # URL patterns
│   └── templates/instruments/      # 9 templates
│
├── transfers/                      # Sample transfers
│   ├── models.py                   # Transfer (auto-numbered), TransferItem
│   ├── views.py                    # 13+ views (dispatch, receive, track, movement history)
│   ├── services/                   # tracking.py
│   ├── urls.py                     # URL patterns
│   └── templates/transfers/        # 11 templates
│
├── api/                            # REST API (Django REST Framework)
│   ├── urls.py                     # 60+ router-registered viewsets
│   ├── views/                      # APIView implementations per module
│   ├── serializers/                # 21 serializer files
│   ├── filters/                    # 11 filter files
│   ├── permissions/                # Custom permission classes
│   └── pagination/                 # Custom pagination
│
├── docs/                           # Documentation
│   ├── TRPM_LIMS_Complete_SOP_Manual.md
│   ├── TRPM_LIMS_Manuscript.md
│   ├── SOP_Documentation_Methodology.docx
│   ├── TRPM_LIMS_Complete_SOP_Manual.docx
│   ├── TRPM_LIMS_Manuscript.docx
│   └── SOP_TRPM_LIMS.docx
│
├── static/                         # Static files (CSS, JS, images)
├── staticfiles/                    # Collected static files (production)
├── media/                          # Uploaded files (barcodes, reports, documents)
├── templates/                      # Global templates (base.html, navigation)
├── requirements.txt                # Python dependencies
├── db.sqlite3                      # SQLite database (development)
└── manage.py                       # Django management script
```

---

## Modules Overview

| Module | Models | Views | Templates | Services | API | Description |
|--------|--------|-------|-----------|----------|-----|-------------|
| **lab_management** | 3 | 6 | 6 | 1 | Yes | Patients, orders, results, labels |
| **reagents** | 3 | 1 | - | - | Yes | Reagent/molecular reagent inventory |
| **molecular_diagnostics** | 15+ | 12+ | Multiple | 7 | Yes | Samples, panels, QC, variants, reflex |
| **pharmacogenomics** | 9 | 7 | 8 | 2 | - | PGx genes, drugs, diplotypes, CPIC |
| **microbiology** | 5+ | 6 | 6 | 1 | Yes | Culture, AST, interpretation |
| **pathology** | 4+ | 4 | 4 | 2 | Yes | Histopathology, staging, IHC |
| **ontology** | 6 | 10 | 9 | - | - | Disease/anatomy terminology, AJAX |
| **bioinformatics** | 6 | 8+ | 9 | - | - | Pipelines (Nextflow/Snakemake/WDL) |
| **single_cell** | 6 | 9 | 9 | - | - | 10x/Smart-seq/Drop-seq workflows |
| **analytics** | 6 | Dashboard | Dashboard | 3 | - | KPIs, reports, scheduled alerts |
| **billing** | 7 | 14+ | 14 | - | - | Invoicing, payments, quotes |
| **projects** | 6 | 14 | 12 | - | - | Research projects, ethics, milestones |
| **sensors** | 5 | 9 | 8 | - | Yes | Environmental monitoring, IoT API |
| **equipment** | 3 | 13 | 10 | - | Yes | Instruments, maintenance, calibration |
| **storage** | 4 | 8 | 6 | - | Yes | Freezers, racks, positions, audit |
| **users** | 3 | 13 | 9 | - | - | RBAC (6 roles, 21 permissions) |
| **messaging** | 3 | 3 | 3 | 2 | Yes | Inbox, threads, notifications |
| **qms** | 5 | 4 | 4 | 1 | Yes | Documents, reviews, training |
| **dynamic_fields** | 4 | 6 | 7 | - | - | 14 field types, generic FK |
| **tenants** | 5 | 4 | 4 | - | - | Multi-tenant (org/lab/roles) |
| **audit** | 2 | 4 | 4 | - | Yes | Change tracking, IP logging |
| **compliance** | 2 | 10 | 8 | - | - | IRB consent (7 protocol types) |
| **data_exchange** | 6 | 8 | 7 | 3 | Yes | HL7 v2.5.1, FHIR R4, import/export |
| **instruments** | 3 | 7 | 9 | 4 | Yes | ASTM E1381, TCP/Serial, worklists |
| **transfers** | 2 | 13 | 11 | 1 | - | Dispatch/receive, 6 conditions |
| **api** | - | 60+ | - | - | Yes | REST API, Swagger, ReDoc |
| **Totals** | **150+** | **200+** | **184** | **39** | | **26 integrated modules** |

---

## REST API

The REST API is built with Django REST Framework and provides 60+ endpoints with OpenAPI documentation.

### API Documentation

- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

### API Infrastructure

- **21 Serializer files** - Comprehensive data serialization for all modules
- **11 Filter files** - Advanced filtering with django-filter
- **Custom Permissions** - Role-based API access control
- **Custom Pagination** - Configurable page sizes

### Key API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/patients/` | Patient CRUD |
| `/api/lab-orders/` | Lab order management |
| `/api/molecular-samples/` | Molecular sample CRUD and workflow |
| `/api/molecular-results/` | Result management and variant calls |
| `/api/test-panels/` | Test panel configuration |
| `/api/gene-targets/` | Gene target database |
| `/api/instruments/` | Instrument management |
| `/api/storage-units/` | Storage unit CRUD |
| `/api/storage-racks/` | Rack management |
| `/api/reagents/` | Reagent inventory |
| `/api/organisms/` | Microbiology organisms |
| `/api/cultures/` | Culture management |
| `/api/pathology-cases/` | Pathology case CRUD |
| `/api/documents/` | QMS document management |
| `/api/messages/` | Messaging |
| `/api/notifications/` | Notification management |
| `/sensors/api/readings/` | IoT sensor data submission |

### Authentication

API authentication uses Django session authentication and token-based authentication. CORS is configured via django-cors-headers.

---

## URL Endpoints

### Web Interface (27 Routes)

| URL | Module | Description |
|-----|--------|-------------|
| `/` | analytics | Dashboard (home redirect) |
| `/admin/` | django | Admin interface |
| `/api/` | api | REST API root (60+ endpoints) |
| `/lab/` | lab_management | Patient registration, orders, results |
| `/molecular/` | molecular_diagnostics | Molecular testing, TAT dashboard |
| `/pgx/` | pharmacogenomics | PGx genes, drugs, results, panels |
| `/micro/` | microbiology | Cultures, organisms, AST panels |
| `/pathology/` | pathology | Cases, histology |
| `/ontology/` | ontology | Disease terms, anatomy, organisms |
| `/bioinformatics/` | bioinformatics | Pipelines, services, jobs |
| `/single-cell/` | single_cell | Samples, libraries, clusters |
| `/analytics/` | analytics | Dashboards, reports, KPIs |
| `/billing/` | billing | Invoices, payments, quotes, clients |
| `/projects/` | projects | Projects, members, milestones, docs |
| `/sensors/` | sensors | Devices, readings, alerts, dashboard |
| `/equipment/` | equipment | Instruments, types, maintenance |
| `/storage/` | storage | Units, racks, logs |
| `/users/` | users | Login, profile, user/role management |
| `/messaging/` | messaging | Inbox, threads, notifications |
| `/qms/` | qms | Documents, folders |
| `/fields/` | dynamic_fields | Categories, fields, templates |
| `/tenants/` | tenants | Organizations, laboratories |
| `/audit/` | audit | Audit logs, trails, dashboard |
| `/compliance/` | compliance | Consent protocols, patient consent |
| `/exchange/` | data_exchange | Import/export, HL7/FHIR |
| `/instruments/` | instruments | Connections, messages, worklists |
| `/transfers/` | transfers | Dispatch, receive, track |

---

## Configuration

All configuration is via environment variables (`.env` file or system env). See `.env.example` for the full list with comments. Key configuration areas:

### Laboratory branding (used in generated reports)

```bash
LAB_NAME="Your Laboratory Name"
LAB_ADDRESS="123 Lab Street, City, Country"
LAB_PHONE="+1-234-567-8900"
LAB_ACCREDITATION="CAP #12345, CLIA #67890"
```

### Security & authentication

| Setting | Description |
|---|---|
| `SECRET_KEY` | **Required** — generate with `make secretkey` |
| `ALLOWED_HOSTS` | Comma-separated production hostnames |
| `CSRF_TRUSTED_ORIGINS` | e.g., `https://lims.example.org` |
| `CORS_ALLOWED_ORIGINS` | Frontend origins allowed for API calls |
| JWT access token | 15-minute lifetime, refresh tokens 1 day (configurable in settings) |
| Password policy | 12-char minimum, 90-day aging, last-5 reuse prevention |

### Compliance feature flags

| Flag | Default | Effect |
|---|---|---|
| `ENABLE_PART11` | `False` | Requires electronic signatures on result approval/review |
| `ENABLE_HIPAA_MODE` | `False` | Enforces TOTP MFA for all authenticated users |
| `PASSWORD_MAX_AGE_DAYS` | `90` | Force password change interval (0 disables) |

### Database

```bash
# PostgreSQL (production)
DATABASE_URL=postgres://lims_user:lims_pass@localhost:5432/trpm_lims

# SQLite (local dev — used automatically when DATABASE_URL is not set)
```

### External services

```bash
CELERY_BROKER_URL=redis://localhost:6379/0
SENTRY_DSN=https://xxx@sentry.io/yyy   # optional
FHIR_BASE_URL=http://localhost:8000/fhir
NCBI_API_KEY=                            # for ClinVar variant annotation
```

---

## Usage Guide

### Getting Started

1. **Log in** at `/users/login/` or access admin at `/admin/`

2. **Initial Setup** (recommended order):
   - Create Organization and Laboratory (Tenants)
   - Create Roles and Users (Users)
   - Create Instrument Types and Instruments (Equipment)
   - Create Storage Units and Racks (Storage)
   - Configure Reagent Inventory (Reagents)
   - Create Molecular Sample Types and Test Panels
   - Create Gene Targets and Workflow Definitions
   - Configure Consent Protocols (Compliance)
   - Set up External Systems for HL7/FHIR (Data Exchange)

### Molecular Diagnostics Workflow

1. **Create Molecular Sample** → Link to Lab Order, select Test Panel
2. **Track Through Workflow** → RECEIVED → EXTRACTED → AMPLIFIED → SEQUENCED → ANALYZED → REPORTED
3. **Create PCR Plates** → 96/384-well plate management with batch items
4. **Enter Results** → PCR Ct values, variant calls with ACMG classification
5. **Variant Annotation** → Automatic ClinVar/gnomAD lookup
6. **Reflex Testing** → Automatic reflex orders triggered by result conditions
7. **Generate Reports** → Professional PDF clinical reports

### Pharmacogenomics Workflow

1. **Configure Genes** → Add PGx genes with star alleles, activity scores, and population frequencies
2. **Setup Drug Database** → Add drugs with CPIC interaction data, evidence levels, and FDA label status
3. **Create PGx Panels** → Group genes into testing panels
4. **Process Results** → Diplotype calling → Activity score calculation → Phenotype assignment → Drug recommendations
5. **Clinical Reports** → PGx-specific reports with per-drug dosing guidance (Standard/Reduce/Avoid/Alternative)

### HL7/FHIR Integration

1. **Configure External Systems** → Add LIS, EHR, HIS connections with transport settings (MLLP, HTTP, SFTP)
2. **Message Routing** → Automatic message routing between systems
3. **Import/Export** → Bulk CSV/XLSX import with validation, configurable export templates

### Instrument Integration

1. **Configure Connections** → TCP or Serial (RS-232) with ASTM E1381/E1394 protocol
2. **Worklist Export** → Generate and send worklists to analyzers
3. **Result Import** → Automatic parsing and import of instrument results

### Quality Control

1. **Define QC Metrics** → Set acceptable ranges with warning/critical thresholds
2. **Record QC Results** → Link to instrument runs or PCR plates
3. **Monitor** → Auto pass/fail based on metric definitions

### Turnaround Time (TAT) Monitoring

The system tracks sample TAT against SLA targets:
- **On Track**: Within normal processing time
- **Warning**: 75%+ of TAT target
- **Critical**: 90%+ of TAT target
- **Overdue**: Exceeded TAT target

Access the TAT dashboard at `/molecular/tat/`

---

## Production Deployment

### Docker (recommended)

The included `Dockerfile` is a multi-stage build (builder + slim runtime) with:
- Non-root `lims` user
- `tini` init process
- Healthcheck endpoint
- Static files collected at build time via WhiteNoise

The `docker-compose.yml` provides the full stack:

| Service | Image | Purpose |
|---|---|---|
| `app` | `trpm-lims:latest` (built from Dockerfile) | Django + gunicorn |
| `db` | `postgres:16-alpine` | Database |
| `redis` | `redis:7-alpine` | Celery broker + cache |
| `celery` | same as app | Background task worker |
| `nginx` | `nginx:1.27-alpine` | Reverse proxy, media serving |
| `backup` | `postgres:16-alpine` (via override) | Daily pg_dump (02:00 UTC) |

```bash
# 1. Configure
cp .env.example .env
nano .env   # Set SECRET_KEY, ALLOWED_HOSTS, POSTGRES_PASSWORD, etc.

# 2. Build and launch
make docker-build
make docker-up

# 3. Initialize
docker compose exec app python manage.py migrate
docker compose exec app python manage.py createsuperuser

# 4. Verify
docker compose exec app python manage.py check --deploy
# Expected: "System check identified no issues"
```

### Security hardening (automatic when DEBUG=False)

The following are enforced in production mode:
- HSTS (1 year, subdomains, preload)
- Secure session and CSRF cookies
- SSL redirect
- X-Frame-Options: DENY
- Content-Type nosniff
- Referrer-Policy: same-origin

### Gunicorn configuration

`gunicorn.conf.py` is fully env-overridable:

| Env var | Default | Description |
|---|---|---|
| `GUNICORN_WORKERS` | `(2 * CPU) + 1` (max 8) | Worker processes |
| `GUNICORN_THREADS` | `4` | Threads per worker |
| `GUNICORN_TIMEOUT` | `60` | Request timeout (seconds) |
| `GUNICORN_MAX_REQUESTS` | `1000` | Recycle workers after N requests |

### Backups

Automated daily backups are included via `docker-compose.override.yml`:

```bash
# Manual backup
docker compose exec backup /scripts/backup.sh

# Test that backups are restorable
docker compose exec backup /scripts/restore_drill.sh
```

Backups are gzipped pg_dump files stored in a Docker volume with 30-day retention.

### Load testing

```bash
pip install locust
locust --host=http://localhost:8000
# Opens web UI at http://localhost:8089
```

### CI/CD

A GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push/PR:
- Postgres + Redis service containers
- `python manage.py check --deploy`
- `python manage.py migrate`
- `pytest` with coverage report

### Deploy checklist

```
[ ] SECRET_KEY generated and set (make secretkey)
[ ] DATABASE_URL points to production PostgreSQL
[ ] ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS set to real domains
[ ] TLS certificate provisioned (nginx/Caddy/ALB)
[ ] docker compose up -d succeeds
[ ] python manage.py check --deploy returns 0 issues
[ ] python manage.py migrate applied
[ ] Superuser created
[ ] Backup restore drill passed (scripts/restore_drill.sh)
[ ] Sentry DSN configured (optional but recommended)
```

---

## Testing

```bash
make test              # Run all 62 tests
make test-smoke        # Smoke tests only (fast)
make coverage          # Tests with HTML coverage report
make check             # Django system checks (dev mode)
make deploy-check      # Django deploy checks (production mode)
```

Test coverage spans all 26 apps with smoke tests (model creation, API auth) plus an end-to-end integration test covering the full workflow: patient registration, lab order, molecular sample, result entry, review, approval with electronic signature, and audit trail verification.

---

## Compliance

TRPM-LIMS includes scaffolding for 21 CFR Part 11 and HIPAA compliance. See `docs/compliance/` for the full document set:

| Document | Path |
|---|---|
| Validation Master Plan | `docs/compliance/validation_master_plan.md` |
| User Requirements Specification | `docs/compliance/user_requirements_specification.md` |
| Installation Qualification (IQ) | `docs/compliance/installation_qualification.md` |
| Operational Qualification (OQ) | `docs/compliance/operational_qualification.md` |
| Performance Qualification (PQ) | `docs/compliance/performance_qualification.md` |
| Requirements Traceability Matrix | `docs/compliance/traceability_matrix.md` |
| RBAC Matrix | `docs/compliance/rbac_matrix.md` |
| Part 11 Assessment | `docs/compliance/part11_assessment.md` |
| HIPAA Risk Assessment | `docs/compliance/hipaa_risk_assessment.md` |
| Training Log | `docs/compliance/training_log.md` |
| Change Control Log | `docs/compliance/change_control_log.md` |

SOPs are in `docs/sops/`: electronic signature issuance, credential loss, incident response, break-glass access.

---

## Troubleshooting

### Port already in use

```bash
lsof -ti:8000 | xargs kill -9
make run
```

### WeasyPrint warnings

The "WeasyPrint could not import some external libraries" message is cosmetic. PDF report generation won't work without the native libs, but everything else runs fine. To fix:

```bash
# macOS
brew install pango

# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangoft2-1.0-0 libcairo2

# Verify
python -c "from weasyprint import HTML; print('WeasyPrint OK')"
```

### Migration errors

```bash
DEBUG=True python manage.py check
DEBUG=True python manage.py showmigrations
DEBUG=True python manage.py migrate --run-syncdb
```

### Static files not loading

```bash
DEBUG=True python manage.py collectstatic --clear
```

### Deploy check shows issues

```bash
make deploy-check
# Fix any ERRORS (WARNINGS are informational)
```

---

## Make commands

```
make help              Show all targets
make install           Install python dependencies
make migrate           Apply database migrations
make run               Run dev server (DEBUG=True, port 8000)
make test              Run test suite
make test-smoke        Run smoke tests only
make coverage          Tests with coverage report
make check             Django system checks (dev)
make deploy-check      Django deploy checks (production)
make secretkey         Generate a SECRET_KEY
make docker-build      Build Docker image
make docker-up         Start full stack
make docker-down       Stop full stack
make docker-logs       Tail app logs
make docker-shell      Shell into app container
make clean             Remove caches
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `make test`
5. Run deploy check: `make deploy-check`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Contact

- **Name:** Bala Subramani Gattu Linga
- **Email:** blinga@hamad.qa
- **GitHub:** [glbala87](https://github.com/glbala87)
