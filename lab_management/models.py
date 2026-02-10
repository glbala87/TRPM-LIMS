from django.db import models
from django.utils import timezone
from django.utils.html import format_html
from django.conf import settings  # Ensure settings is imported for barcode URL
import barcode
from barcode.writer import ImageWriter
from django.db import models
from django.conf import settings
from django.utils import timezone
from io import BytesIO
from django.core.files.base import ContentFile


# Client Names as choices for client_name
CLIENT_CHOICES = [
    ('Al Farooq Mabela', 'Al Farooq Mabela'),
    ('Adlife', 'Adlife'),
    ('Advance Medical Center', 'Advance Medical Center'),
    ('Afaq Healthcare', 'Afaq Healthcare'),
    ('Afaq Visa Medical', 'Afaq Visa Medical'),
    ('Al Amal', 'Al Amal'),
    ('Al Farooq Barka', 'Al Farooq Barka'),
    ('Al Farooq Sawadi', 'Al Farooq Sawadi'),
    ('Al Manar', 'Al Manar'),
    ('Al Manar Visa Medical', 'Al Manar Visa Medical'),
    ('Al Rafadian', 'Al Rafadian'),
    ('Al Saada', 'Al Saada'),
    ('Al Shammar Polyclinic', 'Al Shammar Polyclinic'),
    ('Ava Labs', 'Ava Labs'),
    ('Azad Healthcare', 'Azad Healthcare'),
    ('Azad Healthcare Visa Medical', 'Azad Healthcare Visa Medical'),
    ('Bahwan', 'Bahwan'),
    ('Barakath Al Noor Clinic', 'Barakath Al Noor Clinic'),
    ('Best Medicare', 'Best Medicare'),
    ('Clinica Victoria', 'Clinica Victoria'),
    ('Clinicare', 'Clinicare'),
    ('Crystal Clinic Visa Medical', 'Crystal Clinic Visa Medical'),
    ('Crystal Polyclinic', 'Crystal Polyclinic'),
    ('El Abda', 'El Abda'),
    ('Fajr Al Madina', 'Fajr Al Madina'),
    ('Fusion', 'Fusion'),
]

# Models
class Patient(models.Model):
    OP_NO = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    tribe = models.CharField(max_length=100, blank=True, null=True)
    age = models.IntegerField()
    marital_status = models.CharField(
        max_length=50,
        choices=[('Single', 'Single'), ('Married', 'Married')],
        default='Single'
    )
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female')])
    passport_no = models.CharField(max_length=50, blank=True, null=True)
    nationality = models.CharField(max_length=100)
    phone_no = models.CharField(max_length=15)
    resident_card = models.CharField(max_length=50, blank=True, null=True)
    client_name = models.CharField(max_length=100, choices=CLIENT_CHOICES, null=True, blank=True)  # Temporarily allow null
    is_special = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    date_added = models.DateField(default=timezone.now)  # Add date field to store when the patient was added
    barcode_image = models.ImageField(upload_to='barcodes/', blank=True, null=True)  # Barcode image field

    def generate_barcode(self):
        """Generate a barcode with patient information"""
        try:
            # Barcode generation using OP_NO
            barcode_data = self.OP_NO
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(barcode_data, writer=ImageWriter())

            # Create an image for the barcode and save it to a file-like object
            barcode_image = BytesIO()
            barcode_instance.write(barcode_image)

            # Convert barcode to image using Pillow
            barcode_image.seek(0)
            barcode_img = Image.open(barcode_image)

            # Create a new image with additional space for text
            img_width = barcode_img.width
            img_height = barcode_img.height + 60  # Additional space for text
            final_img = Image.new('RGB', (img_width, img_height), color=(255, 255, 255))
            final_img.paste(barcode_img, (0, 0))

            # Add text below the barcode
            draw = ImageDraw.Draw(final_img)

            # If PIL font doesn't work, use a basic built-in font
            try:
                font = ImageFont.truetype("arial.ttf", 16)  # Make sure you have a valid font
            except IOError:
                font = ImageFont.load_default()  # Default font if custom font fails

            # Add patient details as text
            text = f"Name: {self.first_name} {self.last_name}\nOP NO: {self.OP_NO}\nAge: {self.age} Y"
            draw.text((10, barcode_img.height + 10), text, fill="black", font=font)

            # Save the final image to a BytesIO object
            final_image_io = BytesIO()
            final_img.save(final_image_io, format="PNG")
            final_image_io.seek(0)

            # Save the barcode image to the model's field
            self.barcode_image.save(f"{self.OP_NO}_barcode.png", ContentFile(final_image_io.read()), save=False)
        except Exception as e:
            print(f"Error generating barcode: {e}")

    def save(self, *args, **kwargs):
        if not self.barcode_image:  # Only generate barcode if it doesn't already exist
            self.generate_barcode()  # Generate barcode with additional information
        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return f"{self.OP_NO} - {self.first_name} {self.last_name}"

    
# Test categories with their corresponding tests and containers
TEST_CATEGORIES = [
    ('HORMONES_AND_VITAMINS', 'Hormones And Vitamins'),
    ('IMMUNOLOGY', 'Immunology'),
    ('SEROLOGY', 'Serology'),
    ('CANCER_MARKERS', 'CANCER MARKERS'),
    ('MICROBIOLOGY_ROUTINE', 'Microbiology Routine'),
    ('MICROBIOLOGY_CULTURE', 'Microbiology Culture'),
    ('BIOCHEMISTRY', 'Biochemistry'),
]

# A dictionary to hold the tests for each category
TEST_CHOICES = {
    'HORMONES_AND_VITAMINS': [
        ('ANTI MULLERIAN HORMONE', 'Serum', 'Red/Yellow'),
        ('B-HCG IN BLOOD', 'Serum', 'Red/Yellow'),
        ('CORTISOL', 'Serum', 'Red/Yellow'),
        ('DHEA - S', 'Serum', 'Red/Yellow'),
        ('ESTRADIOL', 'Serum', 'Red/Yellow'),
        ('FREE T3', 'Serum', 'Red/Yellow'),
        ('FREE T4', 'Serum', 'Red/Yellow'),
        ('FSH', 'Serum', 'Red/Yellow'),
        ('LH', 'Serum', 'Red/Yellow'),
        ('PROGESTERONE (FREE)', 'Serum', 'Red/Yellow'),
        ('PROGESTERONE (TOTAL)', 'Serum', 'Red/Yellow'),
        ('PROLACTIN', 'Serum', 'Red/Yellow'),
        ('SEX HORMONE BINDING GLOBULIN(SHBG)', 'Serum', 'Red/Yellow'),
        ('TESTOSTERONE FREE', 'Serum', 'Red/Yellow'),
        ('TESTOSTERONE TOTAL', 'Serum', 'Red/Yellow'),
        ('THYROID STIMULATINGHORMONE (TSH)', 'Serum', 'Red/Yellow'),
        ('VITAMIN B12', 'Serum', 'Red/Yellow'),
        ('VITAMIN D3', 'Serum', 'Red/Yellow'),
        ('INSULIN', 'Serum', 'Red/Yellow'),
        ('PREGNANCY TEST (BLOOD)', 'Serum', 'Red/Yellow'),
        ('PREGNANCY TEST (SERUM)', 'Serum', 'Red/Yellow'),
        ('PREGNANCY TEST (URINE)', 'Urine', 'Sterile Container'),
        ('THYROID PEROXIDASEAUTOANTIBODIES (ATPO)', 'Serum', 'Red/Yellow'),
        ('VITAMIN B9 (FOLIC ACID)', 'Serum', 'Red/Yellow'),
    ],
    'BIOCHEMISTRY': [
        ('ALBUMIN', 'Serum', 'Red/Yellow'),
        ('ALKALINE PHOSPHATASE', 'Serum', 'Red/Yellow'),
        ('AMYLASE', 'Serum', 'Red/Yellow'),
        ('BILIRUBIN (direct)', 'Serum', 'Red/Yellow'),
        ('BILIRUBIN (indirect)', 'Serum', 'Red/Yellow'),
        ('BILIRUBIN (total)', 'Serum', 'Red/Yellow'),
        ('CALCIUM (total)', 'Serum', 'Red/Yellow'),
        ('CALCIUM (CORRECTED)', 'Serum', 'Red/Yellow'),
        ('Sodium', 'Serum', 'Red/Yellow'),
        ('Potassium', 'Serum', 'Red/Yellow'),
        ('Chloride', 'Serum', 'Red/Yellow'),
        ('CHOLESTEROL', 'Serum', 'Red/Yellow'),
        ('CREATININE', 'Serum', 'Red/Yellow'),
        ('CK, TOTAL', 'Serum', 'Red/Yellow'),
        ('CK MB', 'Serum', 'Red/Yellow'),
        ('GLUCOSE (FASTING)', 'Serum', 'Red/Yellow'),
        ('GLUCOSE (P.P)', 'Serum', 'Red/Yellow'),
        ('GLUCOSE (RANDOM)', 'Serum', 'Red/Yellow'),
        ('HDL', 'Serum', 'Red/Yellow'),
        ('IRON', 'Serum', 'Red/Yellow'),
        ('LDH', 'Serum', 'Red/Yellow'),
        ('LDL', 'Serum', 'Red/Yellow'),
        ('LIPASE', 'Serum', 'Red/Yellow'),
        ('MAGNESIUM', 'Serum', 'Red/Yellow'),
        ('PHOSPHORUS', 'Serum', 'Red/Yellow'),
        ('SGOT(AST)', 'Serum', 'Red/Yellow'),
        ('SGPT(ALT)', 'Serum', 'Red/Yellow'),
        ('TOTAL PROTEIN', 'Serum', 'Red/Yellow'),
        ('TRIGLYCERIDE', 'Serum', 'Red/Yellow'),
        ('UREA', 'Serum', 'Red/Yellow'),
        ('URIC ACID', 'Serum', 'Red/Yellow'),
        ('ZINC', 'Serum', 'Red/Yellow'),
    ],
    'HORMONES_AND_VITAMINS': [
        ('ANTI MULLERIAN HORMONE', 'Serum', 'Red/Yellow'),
        ('B-HCG IN BLOOD', 'Serum', 'Red/Yellow'),
        ('CORTISOL', 'Serum', 'Red/Yellow'),
        ('DHEA - S', 'Serum', 'Red/Yellow'),
        ('ESTRADIOL', 'Serum', 'Red/Yellow'),
        ('FREE T3', 'Serum', 'Red/Yellow'),
        ('FREE T4', 'Serum', 'Red/Yellow'),
        ('FSH', 'Serum', 'Red/Yellow'),
        ('LH', 'Serum', 'Red/Yellow'),
        ('PROGESTERONE (FREE)', 'Serum', 'Red/Yellow'),
        ('PROGESTERONE (TOTAL)', 'Serum', 'Red/Yellow'),
        ('PROLACTIN', 'Serum', 'Red/Yellow'),
        ('SEX HORMONE BINDING GLOBULIN(SHBG)', 'Serum', 'Red/Yellow'),
        ('TESTOSTERONE FREE', 'Serum', 'Red/Yellow'),
        ('TESTOSTERONE TOTAL', 'Serum', 'Red/Yellow'),
        ('THYROID STIMULATINGHORMONE (TSH)', 'Serum', 'Red/Yellow'),
        ('VITAMIN B12', 'Serum', 'Red/Yellow'),
        ('VITAMIN D3', 'Serum', 'Red/Yellow'),
        ('INSULIN', 'Serum', 'Red/Yellow'),
        ('PREGNANCY TEST (BLOOD)', 'Serum', 'Red/Yellow'),
        ('PREGNANCY TEST (SERUM)', 'Serum', 'Red/Yellow'),
        ('PREGNANCY TEST (URINE)', 'Urine', 'Sterile Container'),
        ('THYROID PEROXIDASEAUTOANTIBODIES (ATPO)', 'Serum', 'Red/Yellow'),
        ('VITAMIN B9 (FOLIC ACID)', 'Serum', 'Red/Yellow'),
    ],
    'SEROLOGY': [
        ('CRP H.S', 'Serum', 'Red/Yellow'),
        ('MONOSPOT', 'Serum', 'Red/Yellow'),
        ('RHEUMATOID FACTOR', 'Serum', 'Red/Yellow'),
        ('SYPHILIS', 'Serum', 'Red/Yellow'),
    ],
    'CANCER_MARKERS': [
        ('CA-125', 'Serum', 'Red/Yellow'),
        ('PSA TOTAL', 'Serum', 'Red/Yellow'),
        ('PSA FREE', 'Serum', 'Red/Yellow'),
    ],
    'MICROBIOLOGY_ROUTINE': [
        ('TB GOLD QUANTIFERON', 'Blood', 'EDTA BLOOD (PURPLE)'),
        ('BLOOD CULTURE ANDSENSITIVITY', 'Blood', 'Sterile Container'),
        # Add other Microbiology Routine tests here...
    ],
    'MICROBIOLOGY_CULTURE': [
        ('SPUTUM CULTURE &SENSITIVITY', 'Sputum', 'Sterile Container'),
        ('SEMEN CULTURE &SENSITIVITY', 'Semen', 'Sterile Container'),
        ('STOOL CULTURE ANDSENSITIVITY', 'Stool', 'STOOL CONTAINER'),
        ('VAGINAL SWAB CULTURE &SENSITIVITY', 'Vaginal Swab', 'Sterile Container'),
        # Add other Microbiology Culture tests here...
    ],
}

CONTAINER_CHOICES = [
    ('EDTA BLOOD (PURPLE)', 'EDTA BLOOD (PURPLE)'),
    ('SODIUM CITRATE (Black)', 'SODIUM CITRATE (Black)'),
    ('Red/Yellow', 'Red/Yellow'),
    ('Citrate/Blue', 'Citrate/Blue'),
    ('URINE', 'URINE'),
    ('Sterile Container', 'Sterile Container'),
    ('EDTA', 'EDTA'),
    ('Red/Yellow/STOOL CONTAINER', 'Red/Yellow/STOOL CONTAINER'),
]

class LabOrder(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    test_id = models.CharField(max_length=100, unique=True, blank=True, null=True)  # Test ID field
    test_type = models.CharField(max_length=50, choices=TEST_CATEGORIES, null=True, blank=True)  # Temporarily allow null
    test_name = models.CharField(max_length=100, choices=[(test[0], test[0]) for category in TEST_CHOICES.values() for test in category], blank=True)
    sample_type = models.CharField(max_length=100, choices=[
        ('SERUM', 'SERUM'),
        ('STOOL', 'STOOL'),
        ('BLOOD', 'BLOOD'),
        ('URINE', 'URINE'),
        ('SEMEN', 'SEMEN'),
        ('SPUTUM', 'SPUTUM'),
        ('EDTA BLOOD', 'EDTA BLOOD'),
        ('HIGH VAGINAL SWAB', 'HIGH VAGINAL SWAB'),
        ('NASAL SWAB', 'NASAL SWAB'),
        ('BIOPSY', 'BIOPSY'),
        ('SALIVA', 'SALIVA'),
        ('CEREBROSPINAL FLUID', 'CEREBROSPINAL FLUID'),
    ])
    container = models.CharField(max_length=100, choices=CONTAINER_CHOICES, blank=True)  # New container field
    sample_collected = models.BooleanField(default=False)
    sample_insufficient = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Automatically populate sample_type and container based on the test_name
        if self.test_name:
            for category, tests in TEST_CHOICES.items():
                for test in tests:
                    if test[0] == self.test_name:
                        self.sample_type = test[1]
                        self.container = test[2]
                        break
        super().save(*args, **kwargs)

    def color_code(self):
        return format_html('<span style="color: blue;">Lab Order</span>' if self.sample_collected else '<span style="color: black;">Pending</span>')

    def __str__(self):
        return f"Lab Order for {self.patient.OP_NO} on {self.date}"

    class Meta:
        verbose_name = "Lab Order"  # Singular label for the model
        verbose_name_plural = "Lab Orders"  # Plural label for the model

        
class TestResult(models.Model):
    lab_order = models.ForeignKey(LabOrder, on_delete=models.CASCADE)
    result_data = models.TextField()
    result_updated = models.BooleanField(default=False)

    def color_code(self):
        return format_html('<span style="color: green;">Results Entered</span>' if self.result_updated else '<span style="color: black;">Pending</span>')

    def __str__(self):
        return f"Test Result for {self.lab_order.patient.OP_NO}"

    class Meta:
        verbose_name = "Test Result"  # Singular label for the model
        verbose_name_plural = "Test Results"  # Plural label for the model

