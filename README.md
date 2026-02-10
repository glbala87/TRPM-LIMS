# Django LIMS - Laboratory Information Management System

A comprehensive Laboratory Information Management System built with Django, featuring support for both traditional clinical laboratory testing (biochemistry, serology, immunology) and advanced molecular diagnostics (PCR, NGS, Sanger sequencing).

---

## Features

### Core Laboratory Management
- **Patient Management** - Patient registration with barcode generation
- **Lab Orders** - Test ordering with sample tracking
- **Test Results** - Result entry and reporting
- **Reagent Inventory** - Stock management with expiration tracking

### Molecular Diagnostics Module
- **Sample Workflow** - State machine tracking (Received → Extracted → Amplified → Sequenced → Analyzed → Reported)
- **Test Panels** - PCR, RT-PCR, NGS, Sanger, FISH, Microarray support
- **Gene Targets** - Gene and variant database
- **Batch Processing** - 96/384-well plate management with visual editor
- **NGS Library Tracking** - Library prep and pooling workflow
- **Quality Control** - QC metrics, controls, and validation
- **Structured Results** - PCR Ct values, variant calls with ACMG classification
- **PDF Reports** - Professional clinical reports with WeasyPrint

### Equipment Management
- **Instrument Tracking** - Serial numbers, locations, status
- **Maintenance Scheduling** - Preventive maintenance and calibration
- **Certification Records** - Calibration certificates and compliance

### Sample Storage
- **Storage Units** - Freezers, refrigerators, nitrogen tanks
- **Location Tracking** - Rack/position-level sample tracking
- **Audit Logging** - Complete storage history

---

## Requirements

- Python 3.10+
- Django 5.1+
- SQLite (default) or PostgreSQL/MySQL

### Python Dependencies

```
Django>=5.1
Pillow>=10.0
python-barcode>=0.15.1
qrcode>=7.4
weasyprint>=60.0
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Django-LIMS.git
cd Django-LIMS/Django-LIMS-main
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install django pillow python-barcode qrcode weasyprint
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

**Windows:**
```bash
# Install GTK3 runtime from https://github.com/nickvergessen/gtk3-runtime
```

### 4. Configure Database

The default configuration uses SQLite. For production, configure PostgreSQL or MySQL in `lims/settings.py`:

```python
# lims/settings.py

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

Access the application at: http://127.0.0.1:8000/admin/

---

## Project Structure

```
Django-LIMS-main/
├── lims/                       # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── lab_management/             # Core lab module
│   ├── models.py              # Patient, LabOrder, TestResult
│   ├── admin.py
│   └── forms.py
├── reagents/                   # Reagent inventory
│   ├── models.py              # Reagent, MolecularReagent
│   └── admin.py
├── molecular_diagnostics/      # Molecular testing module
│   ├── models/
│   │   ├── samples.py         # MolecularSample, MolecularSampleType
│   │   ├── tests.py           # MolecularTestPanel, GeneTarget
│   │   ├── workflows.py       # WorkflowDefinition, SampleHistory
│   │   ├── batches.py         # PCRPlate, NGSLibrary, NGSPool
│   │   ├── qc.py              # QCMetricDefinition, ControlSample
│   │   └── results.py         # MolecularResult, VariantCall
│   ├── services/
│   │   ├── workflow_engine.py # State machine logic
│   │   ├── tat_monitor.py     # Turnaround time tracking
│   │   └── report_generator.py # PDF generation
│   ├── admin/                 # Admin interfaces
│   └── templates/             # Report templates
├── equipment/                  # Instrument management
│   ├── models.py              # Instrument, MaintenanceRecord
│   └── admin.py
├── storage/                    # Sample storage
│   ├── models.py              # StorageUnit, StoragePosition
│   └── admin.py
├── static/                     # Static files
├── media/                      # Uploaded files
└── templates/                  # Global templates
```

---

## Usage Guide

### Getting Started

1. **Log in to Admin**: Navigate to `/admin/` and log in with your superuser credentials.

2. **Initial Setup** (recommended order):
   - Create Instrument Types and Instruments (Equipment)
   - Create Storage Units and Racks (Storage)
   - Create Molecular Sample Types
   - Create Gene Targets
   - Create Workflow Definitions
   - Create Test Panels

### Patient Registration

1. Go to **Lab Management → Patients**
2. Click **Add Patient**
3. Fill in patient details (OP_NO is the unique identifier)
4. A barcode is automatically generated upon save

### Creating Lab Orders

1. Go to **Lab Management → Lab Orders**
2. Select a patient
3. Choose test type and test name
4. Sample type and container are auto-populated

### Molecular Diagnostics Workflow

#### 1. Create a Molecular Sample

1. Go to **Molecular Diagnostics → Molecular Samples**
2. Click **Add Molecular Sample**
3. Link to an existing Lab Order
4. Select Sample Type and Test Panel
5. Sample ID is auto-generated (format: MOL-YYYYMMDD-XXXX)

#### 2. Track Sample Through Workflow

Samples progress through these statuses:

| Status | Description |
|--------|-------------|
| **RECEIVED** | Initial state when sample arrives |
| **EXTRACTED** | DNA/RNA extraction complete |
| **AMPLIFIED** | PCR amplification complete |
| **SEQUENCED** | Sequencing complete |
| **ANALYZED** | Bioinformatics analysis complete |
| **REPORTED** | Final report generated |

Use admin actions to transition samples:
1. Select samples in the list
2. Choose action (e.g., "Mark selected samples as Extracted")
3. Click "Go"

#### 3. Create PCR Plates

1. Go to **Molecular Diagnostics → PCR Plates**
2. Create a new plate with barcode
3. Add wells and assign samples or controls
4. Link to an Instrument Run

#### 4. Enter Results

1. Go to **Molecular Diagnostics → Molecular Results**
2. Create a new result linked to a sample
3. Add PCR Results (for PCR tests):
   - Target gene
   - Ct value (auto-determines detection if ≤40)
   - Detection status
4. Add Variant Calls (for sequencing tests):
   - Gene, chromosome, position, alleles
   - HGVS nomenclature (c. and p. notation)
   - ACMG classification (Pathogenic, Likely Pathogenic, VUS, Likely Benign, Benign)

#### 5. Generate Reports

1. Approve the result (set status to "Final")
2. Use the "Generate reports" admin action
3. Download the PDF from the result detail page

### Quality Control

#### Define QC Metrics

1. Go to **Molecular Diagnostics → QC Metric Definitions**
2. Create metrics with acceptable ranges (min/max values)
3. Set warning thresholds
4. Mark critical metrics that must pass

#### Record QC Results

1. Go to **Molecular Diagnostics → QC Records**
2. Link to an Instrument Run or PCR Plate
3. Enter measured values
4. Pass/fail is automatically calculated based on metric definition

### Equipment Management

#### Add Instruments

1. Go to **Equipment → Instrument Types** (create types first)
2. Go to **Equipment → Instruments**
3. Enter name, serial number, location, status
4. Set maintenance/calibration schedules

#### Schedule Maintenance

1. Go to **Equipment → Maintenance Records**
2. Create scheduled maintenance entries
3. Update status when completed
4. Upload calibration certificates
5. Set next due date

### Sample Storage

#### Configure Storage

1. **Storage Units**: Create freezers (-80°C, -20°C), refrigerators (2-8°C)
2. **Storage Racks**: Add racks to units with row/column configuration
3. **Storage Positions**: Automatically tracked

#### Track Sample Location

1. When creating/editing a Molecular Sample
2. Set the storage_location field
3. View storage logs for complete audit trail

---

## Turnaround Time (TAT) Monitoring

The system tracks sample turnaround time against SLA targets:

- **On Track**: Sample within normal processing time
- **Warning**: Sample at 75%+ of TAT target
- **Critical**: Sample at 90%+ of TAT target
- **Overdue**: Sample has exceeded TAT target

Access the TAT dashboard at `/molecular/tat/` to view:
- At-risk samples requiring attention
- TAT statistics by test panel
- Daily completion metrics

---

## API Endpoints

| URL | Purpose |
|-----|---------|
| `/admin/` | Django Admin Interface |
| `/molecular/dashboard/` | Molecular Diagnostics Dashboard |
| `/molecular/samples/` | Sample List |
| `/molecular/samples/<id>/` | Sample Detail |
| `/molecular/plates/` | PCR Plate List |
| `/molecular/plates/<id>/layout/` | Plate Layout API (JSON) |
| `/molecular/tat/` | TAT Monitoring Dashboard |
| `/molecular/reports/<id>/generate/` | Generate PDF Report |
| `/molecular/reports/<id>/download/` | Download PDF Report |

---

## Configuration

### Laboratory Settings

Configure your laboratory information in `lims/settings.py`:

```python
# Laboratory settings for report generation
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

Uploaded files (barcodes, reports, certificates) are stored in the `media/` directory:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

---

## Workflow Customization

### Adding Custom Workflow States

Edit `molecular_diagnostics/models/samples.py`:

```python
WORKFLOW_STATUS_CHOICES = [
    ('RECEIVED', 'Received'),
    ('EXTRACTED', 'Extracted'),
    ('QC_CHECK', 'QC Check'),      # Custom state
    ('AMPLIFIED', 'Amplified'),
    # ... etc
]
```

Update the workflow engine in `molecular_diagnostics/services/workflow_engine.py`:

```python
VALID_TRANSITIONS = {
    'RECEIVED': ['EXTRACTED', 'CANCELLED', 'FAILED'],
    'EXTRACTED': ['QC_CHECK', 'CANCELLED', 'FAILED'],
    'QC_CHECK': ['AMPLIFIED', 'FAILED'],
    # ... etc
}
```

### Adding New Test Types

1. Add to `MolecularTestPanel.TEST_TYPE_CHOICES` in `models/tests.py`
2. Create corresponding report template in `templates/molecular_diagnostics/reports/`
3. Update `ReportGenerator.REPORT_TEMPLATES` mapping in `services/report_generator.py`

---

## Troubleshooting

### WeasyPrint Issues

If PDF generation fails:

```bash
# Check WeasyPrint installation
python -c "from weasyprint import HTML; print('WeasyPrint OK')"

# If missing dependencies, install system packages (see Installation section)
```

### Migration Errors

If migrations fail:

```bash
# Check for issues
python manage.py check

# Reset migrations for a specific app if needed
python manage.py migrate molecular_diagnostics zero
python manage.py makemigrations molecular_diagnostics
python manage.py migrate molecular_diagnostics
```

### Static Files Not Loading

```bash
# Collect static files
python manage.py collectstatic --clear

# Verify STATIC_ROOT and STATICFILES_DIRS in settings.py
```

### Database Issues

```bash
# Check database connection
python manage.py dbshell

# Show migrations status
python manage.py showmigrations
```

---

## Production Deployment

### Security Checklist

1. Set `DEBUG = False` in settings.py
2. Generate a new `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Use HTTPS
5. Set secure cookie settings

```python
# Production settings
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

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies for WeasyPrint
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

Create a `docker-compose.yml`:

```yaml
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
```

Run with:
```bash
docker-compose up -d
```

---

## Data Models Reference

### Core Models

| Model | App | Description |
|-------|-----|-------------|
| Patient | lab_management | Patient demographics |
| LabOrder | lab_management | Test orders |
| TestResult | lab_management | Basic test results |
| Reagent | reagents | General reagents |
| MolecularReagent | reagents | Primers, probes, kits |

### Molecular Diagnostics Models

| Model | Description |
|-------|-------------|
| MolecularSampleType | Sample type definitions |
| MolecularSample | Samples with workflow tracking |
| GeneTarget | Gene/genetic targets |
| MolecularTestPanel | Test panel configurations |
| WorkflowDefinition | Workflow definitions |
| WorkflowStep | Steps within workflows |
| SampleHistory | Audit trail |
| InstrumentRun | Instrument runs |
| PCRPlate | PCR plates (96/384-well) |
| PlateWell | Individual wells |
| NGSLibrary | NGS libraries |
| NGSPool | Library pools |
| QCMetricDefinition | QC metric specifications |
| ControlSample | Control materials |
| QCRecord | QC results |
| MolecularResult | Master result records |
| PCRResult | PCR target results |
| SequencingResult | Sequencing metrics |
| VariantCall | Variant annotations |

### Equipment Models

| Model | Description |
|-------|-------------|
| InstrumentType | Instrument categories |
| Instrument | Individual instruments |
| MaintenanceRecord | Maintenance history |

### Storage Models

| Model | Description |
|-------|-------------|
| StorageUnit | Freezers, refrigerators |
| StorageRack | Racks within units |
| StoragePosition | Individual positions |
| StorageLog | Storage audit log |

---

## License

This project is licensed under the MIT License.

---

## Contact

For any questions or feedback, feel free to contact:

- **Name:** Bala Subramani Gattu Linga
- **Email:** blinga@hamad.qa
- **GitHub:** [glbala87](https://github.com/glbala87)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests: `python manage.py test`
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request
