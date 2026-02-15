"""
Label generator for TRPM-LIMS.
Supports ZPL (Zebra Printer Language), PDF, and QR code generation.
"""
import io
import base64
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import qrcode
from qrcode.constants import ERROR_CORRECT_M


class LabelGenerator:
    """
    Base label generator with support for multiple output formats.
    """

    def __init__(self, width_mm: float = 50.8, height_mm: float = 25.4, dpi: int = 203):
        """
        Initialize label generator.

        Args:
            width_mm: Label width in millimeters
            height_mm: Label height in millimeters
            dpi: Printer resolution (dots per inch)
        """
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.dpi = dpi

        # Convert mm to dots
        self.width_dots = int(width_mm * dpi / 25.4)
        self.height_dots = int(height_mm * dpi / 25.4)

    def generate_qr_code(self, data: str, size: int = 100) -> bytes:
        """
        Generate a QR code image.

        Args:
            data: Data to encode in QR code
            size: Size of the QR code in pixels

        Returns:
            PNG image bytes
        """
        qr = qrcode.QRCode(
            version=1,
            error_correction=ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size))

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        return buffer.getvalue()

    def generate_qr_code_base64(self, data: str, size: int = 100) -> str:
        """Generate QR code as base64 string."""
        png_bytes = self.generate_qr_code(data, size)
        return base64.b64encode(png_bytes).decode('utf-8')


class ZPLLabelGenerator(LabelGenerator):
    """
    Generate labels in ZPL (Zebra Printer Language) format.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.commands: List[str] = []

    def _start_label(self):
        """Start a new label."""
        self.commands = [
            '^XA',  # Start format
            f'^PW{self.width_dots}',  # Set print width
            f'^LL{self.height_dots}',  # Set label length
        ]

    def _end_label(self):
        """End the label."""
        self.commands.append('^XZ')  # End format

    def add_text(self, x: int, y: int, text: str, font_size: int = 30,
                 font: str = '0', rotation: int = 0):
        """
        Add text to the label.

        Args:
            x: X position in dots
            y: Y position in dots
            text: Text content
            font_size: Font height in dots
            font: ZPL font identifier (0-9, A-Z)
            rotation: Rotation (N=normal, R=90, I=180, B=270)
        """
        rotation_map = {0: 'N', 90: 'R', 180: 'I', 270: 'B'}
        rot = rotation_map.get(rotation, 'N')

        self.commands.append(f'^FO{x},{y}')  # Field origin
        self.commands.append(f'^A{font}{rot},{font_size},{font_size}')  # Font
        self.commands.append(f'^FD{text}^FS')  # Field data and separator

    def add_barcode_128(self, x: int, y: int, data: str, height: int = 50,
                        show_text: bool = True):
        """
        Add a Code 128 barcode.

        Args:
            x: X position in dots
            y: Y position in dots
            data: Barcode data
            height: Barcode height in dots
            show_text: Show human-readable text below barcode
        """
        interpretation = 'Y' if show_text else 'N'
        self.commands.append(f'^FO{x},{y}')
        self.commands.append(f'^BY2')  # Barcode defaults
        self.commands.append(f'^BCN,{height},{interpretation},N,N')
        self.commands.append(f'^FD{data}^FS')

    def add_qr_code(self, x: int, y: int, data: str, magnification: int = 4):
        """
        Add a QR code.

        Args:
            x: X position in dots
            y: Y position in dots
            data: QR code data
            magnification: Size magnification (1-10)
        """
        self.commands.append(f'^FO{x},{y}')
        self.commands.append(f'^BQN,2,{magnification}')
        self.commands.append(f'^FDMM,A{data}^FS')

    def add_line(self, x: int, y: int, width: int, height: int, color: str = 'B'):
        """
        Add a line or box.

        Args:
            x: X position
            y: Y position
            width: Line width in dots
            height: Line height in dots
            color: B=black, W=white
        """
        self.commands.append(f'^FO{x},{y}')
        self.commands.append(f'^GB{width},{height},1,{color}^FS')

    def generate_sample_label(self, sample) -> str:
        """
        Generate a sample label.

        Args:
            sample: MolecularSample model instance

        Returns:
            ZPL command string
        """
        self._start_label()

        # QR code with sample ID
        self.add_qr_code(10, 10, sample.sample_id, magnification=3)

        # Sample ID (large text)
        self.add_text(120, 15, sample.sample_id, font_size=35)

        # Patient info
        patient = sample.patient
        patient_name = f"{patient.last_name}, {patient.first_name}"[:25]
        self.add_text(120, 55, patient_name, font_size=25)

        # Sample type
        sample_type = sample.sample_type.code if sample.sample_type else ''
        self.add_text(120, 85, sample_type, font_size=20)

        # Date
        date_str = sample.received_datetime.strftime('%Y-%m-%d')
        self.add_text(120, 110, date_str, font_size=18)

        # Priority indicator
        if sample.priority != 'ROUTINE':
            self.add_text(350, 15, sample.priority, font_size=25)

        self._end_label()
        return '\n'.join(self.commands)

    def generate_patient_label(self, patient) -> str:
        """
        Generate a patient identification label.

        Args:
            patient: Patient model instance

        Returns:
            ZPL command string
        """
        self._start_label()

        # Barcode with OP_NO
        self.add_barcode_128(10, 10, patient.OP_NO, height=40)

        # Patient name
        full_name = f"{patient.last_name}, {patient.first_name}"[:30]
        self.add_text(10, 70, full_name, font_size=30)

        # OP Number
        self.add_text(10, 105, f"ID: {patient.OP_NO}", font_size=25)

        # DOB/Age and Gender
        info_line = f"Age: {patient.age}  Gender: {patient.gender}"
        self.add_text(10, 135, info_line, font_size=20)

        self._end_label()
        return '\n'.join(self.commands)

    def generate_reagent_label(self, reagent) -> str:
        """
        Generate a reagent label.

        Args:
            reagent: MolecularReagent model instance

        Returns:
            ZPL command string
        """
        self._start_label()

        # QR code with lot number
        self.add_qr_code(10, 10, f"LOT:{reagent.lot_number}", magnification=3)

        # Reagent name
        name = reagent.name[:25]
        self.add_text(120, 15, name, font_size=28)

        # Lot number
        self.add_text(120, 50, f"Lot: {reagent.lot_number}", font_size=22)

        # Expiration date
        if reagent.expiration_date:
            exp_str = reagent.expiration_date.strftime('%Y-%m-%d')
            self.add_text(120, 80, f"Exp: {exp_str}", font_size=22)

        # Storage temperature
        if hasattr(reagent, 'storage_temperature'):
            temp = reagent.get_storage_temperature_display()
            self.add_text(120, 110, temp, font_size=18)

        self._end_label()
        return '\n'.join(self.commands)


class PDFLabelGenerator(LabelGenerator):
    """
    Generate labels as PDF using WeasyPrint or ReportLab.
    """

    def generate_sample_label_html(self, sample) -> str:
        """
        Generate HTML for a sample label.

        Args:
            sample: MolecularSample model instance

        Returns:
            HTML string
        """
        qr_base64 = self.generate_qr_code_base64(sample.sample_id, size=80)
        patient = sample.patient
        patient_name = f"{patient.last_name}, {patient.first_name}"

        html = f"""
        <div style="width: {self.width_mm}mm; height: {self.height_mm}mm;
                    border: 1px solid #000; padding: 2mm; font-family: Arial, sans-serif;
                    box-sizing: border-box; display: flex;">
            <div style="width: 25mm;">
                <img src="data:image/png;base64,{qr_base64}" style="width: 20mm; height: 20mm;">
            </div>
            <div style="flex: 1; padding-left: 2mm;">
                <div style="font-size: 12pt; font-weight: bold;">{sample.sample_id}</div>
                <div style="font-size: 9pt;">{patient_name}</div>
                <div style="font-size: 8pt;">{sample.sample_type.name if sample.sample_type else ''}</div>
                <div style="font-size: 8pt;">{sample.received_datetime.strftime('%Y-%m-%d')}</div>
            </div>
        </div>
        """
        return html

    def generate_batch_labels_html(self, samples) -> str:
        """
        Generate HTML for multiple sample labels.

        Args:
            samples: Iterable of MolecularSample instances

        Returns:
            HTML string with all labels
        """
        labels = []
        for sample in samples:
            labels.append(self.generate_sample_label_html(sample))

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                @page {{
                    size: A4;
                    margin: 10mm;
                }}
                body {{
                    margin: 0;
                    padding: 0;
                }}
                .label-grid {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 2mm;
                }}
                .label {{
                    page-break-inside: avoid;
                }}
            </style>
        </head>
        <body>
            <div class="label-grid">
                {''.join(f'<div class="label">{label}</div>' for label in labels)}
            </div>
        </body>
        </html>
        """
        return html

    def generate_pdf(self, html_content: str) -> bytes:
        """
        Generate PDF from HTML content.

        Args:
            html_content: HTML string

        Returns:
            PDF bytes
        """
        try:
            from weasyprint import HTML
            pdf_buffer = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            return pdf_buffer.getvalue()
        except ImportError:
            raise ImportError("WeasyPrint is required for PDF generation. Install with: pip install weasyprint")

    def to_response(self, samples, filename: str = 'labels.pdf'):
        """
        Generate a Django HttpResponse with PDF labels.

        Args:
            samples: Iterable of samples
            filename: Output filename
        """
        from django.http import HttpResponse

        html = self.generate_batch_labels_html(samples)
        pdf = self.generate_pdf(html)

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class BatchLabelPrinter:
    """
    Batch label printing utility.
    """

    @staticmethod
    def print_sample_labels(samples, output_format: str = 'ZPL') -> str:
        """
        Generate labels for multiple samples.

        Args:
            samples: Iterable of MolecularSample instances
            output_format: 'ZPL' or 'PDF'

        Returns:
            Label data string (ZPL) or bytes (PDF)
        """
        if output_format.upper() == 'ZPL':
            generator = ZPLLabelGenerator()
            labels = []
            for sample in samples:
                labels.append(generator.generate_sample_label(sample))
            return '\n'.join(labels)
        else:
            generator = PDFLabelGenerator()
            return generator.generate_batch_labels_html(samples)

    @staticmethod
    def print_patient_labels(patients, output_format: str = 'ZPL') -> str:
        """
        Generate labels for multiple patients.

        Args:
            patients: Iterable of Patient instances
            output_format: 'ZPL' or 'PDF'
        """
        if output_format.upper() == 'ZPL':
            generator = ZPLLabelGenerator()
            labels = []
            for patient in patients:
                labels.append(generator.generate_patient_label(patient))
            return '\n'.join(labels)
        else:
            raise NotImplementedError("PDF patient labels not yet implemented")
