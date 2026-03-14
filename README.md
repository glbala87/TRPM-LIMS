# TRPM-LIMS - Laboratory Information Management System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-6.0+-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15+-red.svg)](https://www.django-rest-framework.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive, multi-tenant Laboratory Information Management System built with Django 6.0. Designed for clinical laboratories, research institutions, and diagnostic facilities with support for molecular diagnostics, microbiology, pathology, pharmacogenomics, single-cell genomics, bioinformatics pipelines, and more.

TRPM-LIMS provides **23+ integrated modules** with full CRUD interfaces, REST API, role-based access control, and multi-tenant data isolation.

---

## Table of Contents

- [Features](#features)
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
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## Features

### Core Laboratory Management
- **Patient Management** - Patient registration with barcode/QR code generation
- **Lab Orders** - Test ordering with sample tracking and status workflow
- **Test Results** - Result entry, validation, and clinical reporting
- **Reagent Inventory** - Stock management with lot tracking and expiration alerts

### Multi-Tenant Architecture
- **Organizations** - Top-level entities (hospital networks, research institutions)
- **Laboratories** - Multi-lab support with complete data isolation
- **Role-Based Access** - Organization and laboratory-level permissions
- **Feature Flags** - Per-laboratory feature enablement
- **Laboratory Switching** - Seamless context switching between laboratories

### Molecular Diagnostics
- **Sample Workflow** - State machine tracking (Received → Extracted → Amplified → Sequenced → Analyzed → Reported)
- **Test Panels** - PCR, RT-PCR, NGS, Sanger, FISH, Microarray support
- **Gene Targets** - Gene and variant database with HGVS nomenclature
- **Batch Processing** - 96/384-well plate management with visual editor
- **NGS Library Tracking** - Library prep, pooling, and sequencing workflow
- **Quality Control** - QC metrics, controls, and validation rules
- **Structured Results** - PCR Ct values, variant calls with ACMG classification
- **PDF Reports** - Professional clinical reports with WeasyPrint

### Pharmacogenomics (PGx)
- **Gene Dashboard** - PGx gene database (CYP2D6, CYP2C19, DPYD, etc.)
- **Star Alleles** - Allele definitions with activity scores and population frequencies
- **Diplotype Calling** - Automated phenotype assignment from diplotypes
- **Drug-Gene Interactions** - CPIC-based evidence-level drug interaction database
- **Dosing Recommendations** - Phenotype-specific drug dosing guidance
- **Clinical Reports** - PGx-specific PDF report generation

### Microbiology
- **Culture & Sensitivity** - Organism identification and antimicrobial susceptibility
- **Antibiotic Panels** - Configurable AST panels with breakpoints (MIC/Zone)
- **Organism Database** - Taxonomic classification with Gram stain support

### Pathology
- **Histopathology** - Case management with grossing-to-diagnosis workflow
- **Block & Slide Tracking** - Physical specimen tracking
- **Addenda** - Report amendments with full audit trail

### Quality Management System (QMS)
- **Document Control** - Version-controlled SOPs, policies, and procedures
- **Folder Organization** - Hierarchical document organization
- **Review Workflows** - Multi-step document approval cycles
- **Audit Trails** - Complete document change history

### Bioinformatics
- **Pipeline Management** - Define and manage analysis pipelines with versioning
- **Service Catalog** - Bioinformatics services with SLA tracking
- **Job Tracking** - Pipeline execution with status monitoring
- **Result Delivery** - Structured result delivery with client access

### Analytics & Reporting
- **Configurable Dashboards** - Widget-based dashboard system
- **Saved Queries** - Reusable data queries
- **Scheduled Reports** - Automated report generation and delivery
- **KPI Metrics** - Historical performance snapshots
- **Alert System** - Configurable alerts with severity levels
- **TAT Monitoring** - Turnaround time tracking against SLA targets

### Billing & Invoicing
- **Price Lists** - Configurable service pricing
- **Client Management** - Client database with contact tracking
- **Invoice Generation** - Invoice creation with line items and tax
- **Payment Tracking** - Payment recording and reconciliation
- **Quote Management** - Quote generation and conversion to invoices

### Project Management
- **Project Lifecycle** - Draft → Active → Completed workflow
- **Team Members** - Role-based project membership with granular permissions
- **Sample Association** - Link molecular samples to projects with consent tracking
- **Milestones** - Project milestone tracking with status and dates
- **Document Management** - Project-specific document storage
- **Ethics & Compliance** - Ethics approval and consent management

### Environmental Monitoring (Sensors)
- **Sensor Dashboard** - Real-time monitoring overview with alert counts
- **Device Management** - Configure monitoring devices with thresholds
- **Reading History** - Timestamped sensor readings with auto-status calculation
- **Alert System** - Automatic alerts on threshold breach (Warning/Critical)
- **Acknowledge/Resolve** - Alert lifecycle management with audit trail
- **API Endpoint** - REST endpoint for sensor data submission

### Single-Cell Genomics
- **Sample Tracking** - Single-cell sample workflow (Received → Analyzed)
- **Platform Support** - 10x Genomics, Smart-seq2/3, Drop-seq, BD Rhapsody, Parse
- **Cell Metrics** - Viability, concentration, recovery tracking
- **Library Management** - GEX, VDJ, ATAC, Feature Barcode libraries
- **Feature Barcodes** - CITE-seq, cell hashing, CRISPR guide barcodes
- **Cluster Analysis** - Cell cluster tracking with cell type annotation

### Equipment Management
- **Instrument Tracking** - Full CRUD with serial numbers, locations, status
- **Instrument Types** - Categorize instruments by type
- **Maintenance Records** - Preventive maintenance, calibration, and repairs
- **Search & Filter** - Find instruments by name, serial, type, or status

### Sample Storage
- **Storage Units** - Freezers, refrigerators, nitrogen tanks with temperature ranges
- **Rack Management** - Row/column rack configuration within units
- **Audit Logging** - Complete storage event history
- **Search & Filter** - Locate samples by unit, type, or status

### Additional Modules
- **Users & Authentication** - Login, registration, profile management, role-based admin views
- **Messaging** - Internal inbox, threaded conversations, notification system
- **Dynamic Fields** - Custom field definitions with templates for extensible data capture
- **Ontology** - Disease terminology (ICD-10, SNOMED-CT, HPO), anatomical sites, clinical indications, organism taxonomy
- **Audit** - System-wide audit logging with trail views and dashboard
- **Compliance** - Consent protocol and patient consent management
- **Data Exchange** - Import/export with templates and validation
- **Instrument Integration** - Instrument connections, message logs, worklists
- **Transfers** - Sample transfer management with dispatch/receive workflow

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Bootstrap 5)                   │
│  Templates │ Font Awesome │ Responsive Design │ DataTables       │
├─────────────────────────────────────────────────────────────────┤
│                     Django 6.0 Framework                         │
│  Class-Based Views │ LoginRequiredMixin │ Template Inheritance   │
├─────────────────────────────────────────────────────────────────┤
│                    REST API (DRF 3.15+)                          │
│  60+ ViewSets │ drf-spectacular (OpenAPI) │ django-filter        │
├─────────────────────────────────────────────────────────────────┤
│              Multi-Tenant Layer (tenants app)                    │
│  TenantContext │ TenantAwareManager │ Laboratory Scoping         │
├──────────┬──────────┬──────────┬──────────┬────────────────────┤
│  Core    │ Molecular│ Clinical │ Support  │ Infrastructure      │
│  ──────  │ ──────── │ ──────── │ ──────── │ ──────────────      │
│  Patients│ Samples  │ Micro    │ Billing  │ Audit               │
│  Orders  │ Panels   │ Path     │ Projects │ Compliance          │
│  Results │ NGS      │ PGx      │ Sensors  │ Data Exchange       │
│  Reagents│ QC       │ Ontology │ Messaging│ Instruments         │
│  Storage │ Reports  │          │ QMS      │ Transfers           │
│  Equip.  │ Bioinf.  │          │ SingleCell│ Dynamic Fields     │
├──────────┴──────────┴──────────┴──────────┴────────────────────┤
│                    Database (SQLite / PostgreSQL)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Requirements

- Python 3.10+
- Django 6.0+
- SQLite (default) or PostgreSQL/MySQL

### Python Dependencies

```
Django>=6.0
djangorestframework>=3.15.0
drf-spectacular>=0.27.0
django-cors-headers>=4.3.0
django-filter>=23.5
Pillow>=10.0
python-barcode>=0.15.1
qrcode>=7.4
weasyprint>=60.0
openpyxl>=3.1.0
celery>=5.3.0
redis>=5.0.0
hl7apy>=1.3.4
channels>=4.0.0
cryptography>=41.0.0
```

---

## Quick Start

```bash
# Clone the repository
git clone https://github.com/glbala87/TRPM-LIMS.git
cd TRPM-LIMS

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Access the application at:
- **Web Interface**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **REST API**: http://127.0.0.1:8000/api/
- **API Docs**: http://127.0.0.1:8000/api/schema/swagger-ui/

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/glbala87/TRPM-LIMS.git
cd TRPM-LIMS
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Note:** WeasyPrint requires additional system dependencies. See [WeasyPrint Installation](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation) for your OS.

**macOS:**
```bash
brew install pango libffi
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

### 4. Configure Database

The default configuration uses SQLite. For production, configure PostgreSQL in `lims/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'lims_db',
        'USER': 'lims_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files (Production)

```bash
python manage.py collectstatic
```

### 8. Run Development Server

```bash
python manage.py runserver
```

---

## Project Structure

```
TRPM-LIMS/
├── lims/                           # Project settings & configuration
│   ├── settings.py                 # Django settings (33 installed apps)
│   ├── urls.py                     # Root URL router (21 app includes)
│   └── wsgi.py                     # WSGI application
│
├── tenants/                        # Multi-tenant architecture
│   ├── models.py                   # Organization, Laboratory, Memberships, TenantContext
│   ├── views.py                    # Organization/Laboratory CRUD, lab switching
│   ├── urls.py                     # 5 URL patterns
│   └── templates/tenants/          # 4 templates
│
├── lab_management/                 # Core lab module
│   ├── models.py                   # Patient, LabOrder, TestResult
│   ├── admin.py                    # Admin with barcode generation
│   └── services/                   # Label generation services
│
├── molecular_diagnostics/          # Molecular testing (core module)
│   ├── models/                     # Samples, tests, workflows, QC, results
│   ├── services/                   # Workflow engine, TAT monitor, reports
│   └── templates/                  # Report templates, dashboards
│
├── pharmacogenomics/               # Pharmacogenomics module
│   ├── models.py                   # PGxGene, StarAllele, Drug, Recommendations
│   ├── services.py                 # DiplotypeService, RecommendationService
│   ├── views.py                    # 7 views (dashboard, genes, drugs, results)
│   ├── urls.py                     # 7 URL patterns
│   └── templates/pharmacogenomics/ # 7 templates + PDF report
│
├── microbiology/                   # Microbiology module
│   ├── models.py                   # Culture, Organism, Antibiotic, AST
│   ├── views.py                    # 6 views with search
│   ├── urls.py                     # 6 URL patterns
│   └── templates/microbiology/     # 6 templates
│
├── pathology/                      # Pathology module
│   ├── models.py                   # Case, HistologyBlock, Slide, Staining
│   ├── views.py                    # 4 views (cases, histology)
│   ├── urls.py                     # 4 URL patterns
│   └── templates/pathology/        # 4 templates
│
├── ontology/                       # Clinical terminology
│   ├── models.py                   # DiseaseOntology, AnatomicalSite, Organism
│   ├── views.py                    # 9 views + AJAX search
│   ├── urls.py                     # 10 URL patterns
│   └── templates/ontology/         # 9 templates
│
├── bioinformatics/                 # Bioinformatics pipelines
│   ├── models.py                   # Pipeline, Service, Job, Result
│   ├── views.py                    # Pipeline, service, job views
│   ├── urls.py                     # URL patterns
│   └── templates/bioinformatics/   # 9 templates
│
├── single_cell/                    # Single-cell genomics
│   ├── models.py                   # SingleCellSample, Library, FeatureBarcode, Cluster
│   ├── views.py                    # 9 views
│   ├── urls.py                     # 10 URL patterns
│   └── templates/single_cell/      # 9 templates
│
├── analytics/                      # Analytics & dashboards
│   ├── models.py                   # DashboardWidget, Report, KPIMetric, Alert
│   ├── admin.py                    # Full admin registration
│   ├── services/                   # Charts, metrics, statistics services
│   ├── views.py                    # Dashboard views
│   └── templates/analytics/        # Dashboard templates
│
├── billing/                        # Billing & invoicing
│   ├── models.py                   # PriceList, Client, Invoice, Payment, Quote
│   ├── views.py                    # 14+ views (dashboard, CRUD)
│   ├── urls.py                     # URL patterns
│   └── templates/billing/          # 14 templates
│
├── projects/                       # Research projects
│   ├── models.py                   # Project, Member, Sample, Milestone, Document
│   ├── views.py                    # 14 views (full lifecycle)
│   ├── urls.py                     # 13 URL patterns
│   └── templates/projects/         # 12 templates
│
├── sensors/                        # Environmental monitoring
│   ├── models.py                   # SensorType, Device, Reading, Alert
│   ├── views.py                    # 9 views + API endpoint
│   ├── urls.py                     # 11 URL patterns
│   └── templates/sensors/          # 8 templates
│
├── equipment/                      # Instrument management
│   ├── models.py                   # InstrumentType, Instrument, MaintenanceRecord
│   ├── forms.py                    # Forms with date widgets
│   ├── views.py                    # Full CRUD with search/filter
│   ├── urls.py                     # 14 URL patterns
│   └── templates/equipment/        # 10 templates
│
├── storage/                        # Sample storage
│   ├── models.py                   # StorageUnit, Rack, Position, Log
│   ├── forms.py                    # Forms for units and racks
│   ├── views.py                    # 8 views with search/filter
│   ├── urls.py                     # 8 URL patterns
│   └── templates/storage/          # 6 templates
│
├── users/                          # User management & authentication
│   ├── models.py                   # Role, UserProfile
│   ├── views.py                    # Auth, profile, user/role admin views
│   ├── urls.py                     # 12 URL patterns
│   └── templates/users/            # 9 templates
│
├── messaging/                      # Internal messaging
│   ├── models.py                   # Thread, Message, Notification
│   ├── views.py                    # Inbox, thread, notification views
│   ├── urls.py                     # 3 URL patterns
│   └── templates/messaging/        # 3 templates
│
├── qms/                            # Quality Management System
│   ├── models.py                   # Document, Version, ReviewCycle, Folder
│   ├── views.py                    # 4 views (documents, folders)
│   ├── urls.py                     # 4 URL patterns
│   └── templates/qms/             # 4 templates
│
├── dynamic_fields/                 # Custom field definitions
│   ├── models.py                   # Category, FieldDefinition, Template
│   ├── views.py                    # Category, field, template views
│   ├── urls.py                     # URL patterns
│   └── templates/dynamic_fields/   # 7 templates
│
├── reagents/                       # Reagent inventory
│   └── models.py                   # Reagent, MolecularReagent
│
├── api/                            # REST API (DRF)
│   ├── urls.py                     # 60+ router-registered viewsets
│   └── serializers/                # API serializers
│
├── audit/                          # Audit logging
│   ├── models.py                   # AuditLog, AuditTrail
│   ├── views.py                    # Log views, dashboard, API
│   ├── urls.py                     # URL patterns
│   └── templates/audit/            # 4 templates
│
├── compliance/                     # Compliance management
│   ├── models.py                   # ConsentProtocol, PatientConsent
│   ├── views.py                    # 10+ views
│   ├── urls.py                     # URL patterns
│   └── templates/compliance/       # 8 templates
│
├── data_exchange/                  # Data import/export
│   ├── models.py                   # ImportTemplate, ExportConfig
│   ├── views.py                    # 8+ views with validation APIs
│   ├── urls.py                     # URL patterns
│   └── templates/data_exchange/    # 7 templates
│
├── instruments/                    # Instrument integration
│   ├── models.py                   # InstrumentConnection, MessageLog
│   ├── views.py                    # 7+ views with communication APIs
│   ├── urls.py                     # URL patterns
│   └── templates/instruments/      # 9 templates
│
├── transfers/                      # Sample transfers
│   ├── models.py                   # Transfer, TransferItem
│   ├── views.py                    # 13+ views (dispatch, receive, track)
│   ├── urls.py                     # URL patterns
│   └── templates/transfers/        # 11 templates
│
├── docs/                           # Documentation
│   ├── TRPM_LIMS_Complete_SOP_Manual.md
│   ├── TRPM_LIMS_Manuscript.md
│   └── SOP_Documentation_Methodology.docx
│
├── static/                         # Static files (CSS, JS)
├── media/                          # Uploaded files
├── templates/                      # Global templates (base.html)
├── requirements.txt                # Python dependencies
└── manage.py                       # Django management script
```

---

## Modules Overview

| Module | Models | Views | Templates | API | Description |
|--------|--------|-------|-----------|-----|-------------|
| **lab_management** | 3 | Admin | Admin | Yes | Patients, orders, results |
| **molecular_diagnostics** | 10+ | Dashboard | Reports | Yes | Molecular testing workflow |
| **pharmacogenomics** | 8 | 7 | 8 | - | Drug-gene interactions, PGx |
| **microbiology** | 5+ | 6 | 6 | Yes | Culture, AST, organisms |
| **pathology** | 4+ | 4 | 4 | Yes | Histopathology cases |
| **ontology** | 6 | 9 | 9 | - | Disease/anatomy terminology |
| **bioinformatics** | 4+ | 8+ | 9 | - | Pipelines, jobs, results |
| **single_cell** | 6 | 9 | 9 | - | Single-cell sequencing |
| **analytics** | 7 | Dashboard | Dashboard | - | Metrics, reports, alerts |
| **billing** | 5+ | 14+ | 14 | - | Invoicing, payments, quotes |
| **projects** | 6 | 14 | 12 | - | Research project management |
| **sensors** | 4 | 9 | 8 | Yes | Environmental monitoring |
| **equipment** | 3 | 12 | 10 | Yes | Instrument management |
| **storage** | 4 | 8 | 6 | Yes | Sample storage tracking |
| **users** | 2 | 13 | 9 | - | Authentication & profiles |
| **messaging** | 3 | 3 | 3 | Yes | Internal messaging |
| **qms** | 3+ | 4 | 4 | Yes | Document control |
| **dynamic_fields** | 3 | 6 | 7 | - | Custom field definitions |
| **tenants** | 4 | 4 | 4 | - | Multi-tenant architecture |
| **audit** | 2+ | 4 | 4 | Yes | Audit logging |
| **compliance** | 2+ | 10 | 8 | - | Consent management |
| **data_exchange** | 2+ | 8 | 7 | Yes | Import/export |
| **instruments** | 2+ | 7 | 9 | Yes | Instrument integration |
| **transfers** | 2+ | 13 | 11 | - | Sample transfers |

---

## REST API

The REST API is built with Django REST Framework and provides 60+ endpoints.

### API Documentation

- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

### Key API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/patients/` | Patient CRUD |
| `/api/lab-orders/` | Lab order management |
| `/api/molecular-samples/` | Molecular sample CRUD |
| `/api/molecular-results/` | Result management |
| `/api/test-panels/` | Test panel configuration |
| `/api/instruments/` | Instrument management |
| `/api/storage-units/` | Storage unit CRUD |
| `/api/reagents/` | Reagent inventory |
| `/api/organisms/` | Microbiology organisms |
| `/api/cultures/` | Culture management |
| `/api/pathology-cases/` | Pathology case CRUD |
| `/api/documents/` | QMS document management |
| `/api/messages/` | Messaging |

### Authentication

API authentication uses Django session authentication and token-based authentication.

---

## URL Endpoints

### Web Interface

| URL | Module | Description |
|-----|--------|-------------|
| `/` | analytics | Dashboard (home redirect) |
| `/admin/` | django | Admin interface |
| `/lab/` | lab_management | Patient & order management |
| `/molecular/` | molecular_diagnostics | Molecular diagnostics |
| `/pgx/` | pharmacogenomics | Pharmacogenomics |
| `/micro/` | microbiology | Microbiology |
| `/pathology/` | pathology | Pathology |
| `/ontology/` | ontology | Clinical terminology |
| `/bioinformatics/` | bioinformatics | Pipeline management |
| `/single-cell/` | single_cell | Single-cell genomics |
| `/analytics/` | analytics | Dashboards & reports |
| `/billing/` | billing | Invoicing & payments |
| `/projects/` | projects | Research projects |
| `/sensors/` | sensors | Environmental monitoring |
| `/equipment/` | equipment | Instrument management |
| `/storage/` | storage | Sample storage |
| `/users/` | users | User management |
| `/messaging/` | messaging | Internal messaging |
| `/qms/` | qms | Quality management |
| `/fields/` | dynamic_fields | Custom field management |
| `/tenants/` | tenants | Organization management |
| `/audit/` | audit | Audit logs |
| `/compliance/` | compliance | Consent management |
| `/exchange/` | data_exchange | Import/export |
| `/instruments/` | instruments | Instrument integration |
| `/transfers/` | transfers | Sample transfers |
| `/api/` | api | REST API root |

---

## Configuration

### Laboratory Settings

Configure your laboratory in `lims/settings.py`:

```python
LAB_NAME = 'Your Laboratory Name'
LAB_ADDRESS = '123 Lab Street, City, Country'
LAB_PHONE = '+1-234-567-8900'
LAB_ACCREDITATION = 'CAP #12345, CLIA #67890'
```

### Time Zone

```python
TIME_ZONE = 'America/New_York'  # Adjust to your timezone
```

### Media Files

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Celery (Background Tasks)

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

---

## Usage Guide

### Getting Started

1. **Log in** at `/users/login/` or access admin at `/admin/`

2. **Initial Setup** (recommended order):
   - Create Organization and Laboratory (Tenants)
   - Create Instrument Types and Instruments (Equipment)
   - Create Storage Units and Racks (Storage)
   - Create Molecular Sample Types and Test Panels
   - Create Gene Targets and Workflow Definitions

### Molecular Diagnostics Workflow

1. **Create Molecular Sample** → Link to Lab Order, select Test Panel
2. **Track Through Workflow** → RECEIVED → EXTRACTED → AMPLIFIED → SEQUENCED → ANALYZED → REPORTED
3. **Create PCR Plates** → 96/384-well plate management
4. **Enter Results** → PCR Ct values, variant calls with ACMG classification
5. **Generate Reports** → Professional PDF clinical reports

### Pharmacogenomics Workflow

1. **Configure Genes** → Add PGx genes with star alleles and activity scores
2. **Setup Drug Database** → Add drugs with CPIC interaction data
3. **Create PGx Panels** → Group genes into testing panels
4. **Process Results** → Diplotype calling → Phenotype assignment → Drug recommendations
5. **Clinical Reports** → PGx-specific reports with dosing guidance

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

### Security Checklist

```python
DEBUG = False
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = ['your-domain.com']

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
```

### Using Gunicorn

```bash
pip install gunicorn
gunicorn lims.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

### Using Docker

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "lims.wsgi:application", "--bind", "0.0.0.0:8000"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DJANGO_SECRET_KEY=your-secret-key
      - DEBUG=False
    volumes:
      - ./media:/app/media
      - ./staticfiles:/app/staticfiles

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery:
    build: .
    command: celery -A lims worker -l info
    environment:
      - DJANGO_SECRET_KEY=your-secret-key
    depends_on:
      - redis
```

```bash
docker-compose up -d
```

---

## Troubleshooting

### WeasyPrint Issues

```bash
python -c "from weasyprint import HTML; print('WeasyPrint OK')"
```

### Migration Errors

```bash
python manage.py check
python manage.py showmigrations
```

### Static Files Not Loading

```bash
python manage.py collectstatic --clear
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `python manage.py test`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

This project is licensed under the MIT License.

---

## Contact

- **Name:** Bala Subramani Gattu Linga
- **Email:** blinga@hamad.qa
- **GitHub:** [glbala87](https://github.com/glbala87)
