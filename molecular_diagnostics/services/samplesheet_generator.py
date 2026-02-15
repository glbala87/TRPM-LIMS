"""
Sample sheet generator for Illumina sequencing runs.
Generates sample sheets in IEM (Illumina Experiment Manager) format.
"""
import csv
import io
from datetime import datetime
from typing import List, Dict, Optional
from django.conf import settings


class SampleSheetGenerator:
    """
    Generator for Illumina sample sheets in IEM format.

    Supports:
    - Single-end and paired-end sequencing
    - Single and dual indexing
    - Custom adapter sequences
    - Multiple assay types
    """

    # Default header settings
    DEFAULT_WORKFLOW = 'GenerateFASTQ'
    DEFAULT_APPLICATION = 'FASTQ Only'
    DEFAULT_CHEMISTRY = 'Default'

    def __init__(self, run_name: str, investigator: str = '',
                 experiment_name: str = '', date: datetime = None):
        """
        Initialize sample sheet generator.

        Args:
            run_name: Name of the sequencing run
            investigator: Name of the investigator
            experiment_name: Name of the experiment
            date: Date of the run (defaults to today)
        """
        self.run_name = run_name
        self.investigator = investigator or getattr(settings, 'LAB_NAME', 'TRPM Lab')
        self.experiment_name = experiment_name or run_name
        self.date = date or datetime.now()
        self.samples: List[Dict] = []

        # Configuration
        self.workflow = self.DEFAULT_WORKFLOW
        self.application = self.DEFAULT_APPLICATION
        self.assay = ''
        self.chemistry = self.DEFAULT_CHEMISTRY
        self.reads = [151, 151]  # Default paired-end 150bp
        self.adapter_read1 = ''
        self.adapter_read2 = ''

    def set_reads(self, read1_cycles: int, read2_cycles: int = None):
        """Set read lengths for single-end or paired-end sequencing."""
        if read2_cycles:
            self.reads = [read1_cycles, read2_cycles]
        else:
            self.reads = [read1_cycles]

    def set_adapters(self, adapter_read1: str = '', adapter_read2: str = ''):
        """Set adapter sequences for trimming."""
        self.adapter_read1 = adapter_read1
        self.adapter_read2 = adapter_read2

    def add_sample(self, sample_id: str, sample_name: str,
                   index1: str, index2: str = '',
                   description: str = '', project: str = '',
                   **kwargs):
        """
        Add a sample to the sample sheet.

        Args:
            sample_id: Unique sample identifier
            sample_name: Sample name
            index1: Index 1 (i7) sequence
            index2: Index 2 (i5) sequence (optional for single-indexed)
            description: Sample description
            project: Project name
            **kwargs: Additional sample data
        """
        sample = {
            'Sample_ID': sample_id,
            'Sample_Name': sample_name,
            'Sample_Plate': kwargs.get('sample_plate', ''),
            'Sample_Well': kwargs.get('sample_well', ''),
            'Index_Plate_Well': kwargs.get('index_plate_well', ''),
            'I7_Index_ID': kwargs.get('i7_index_id', ''),
            'index': index1,
            'I5_Index_ID': kwargs.get('i5_index_id', ''),
            'index2': index2,
            'Sample_Project': project,
            'Description': description,
        }
        self.samples.append(sample)

    def add_sample_from_ngs_library(self, library):
        """
        Add a sample from an NGSLibrary model instance.

        Args:
            library: NGSLibrary model instance
        """
        self.add_sample(
            sample_id=library.library_id,
            sample_name=library.sample.sample_id if library.sample else library.library_id,
            index1=library.index_sequence or '',
            index2=library.index2_sequence or '',
            description=library.notes or '',
            project=self.experiment_name,
        )

    def add_samples_from_pool(self, pool):
        """
        Add all samples from an NGSPool model instance.

        Args:
            pool: NGSPool model instance
        """
        for library in pool.libraries.all():
            self.add_sample_from_ngs_library(library)

    def _generate_header(self) -> List[str]:
        """Generate the [Header] section."""
        lines = [
            '[Header]',
            f'IEMFileVersion,5',
            f'Investigator Name,{self.investigator}',
            f'Experiment Name,{self.experiment_name}',
            f'Date,{self.date.strftime("%m/%d/%Y")}',
            f'Workflow,{self.workflow}',
            f'Application,{self.application}',
            f'Instrument Type,NextSeq/MiSeq',
            f'Assay,{self.assay}',
            f'Index Adapters,',
            f'Chemistry,{self.chemistry}',
            '',
        ]
        return lines

    def _generate_reads(self) -> List[str]:
        """Generate the [Reads] section."""
        lines = ['[Reads]']
        for read_length in self.reads:
            lines.append(str(read_length))
        lines.append('')
        return lines

    def _generate_settings(self) -> List[str]:
        """Generate the [Settings] section."""
        lines = ['[Settings]']
        if self.adapter_read1:
            lines.append(f'Adapter,{self.adapter_read1}')
        if self.adapter_read2:
            lines.append(f'AdapterRead2,{self.adapter_read2}')
        lines.append('')
        return lines

    def _generate_data(self) -> List[str]:
        """Generate the [Data] section."""
        lines = ['[Data]']

        # Determine if dual-indexed
        has_index2 = any(s.get('index2') for s in self.samples)

        # Header row
        if has_index2:
            headers = [
                'Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
                'I7_Index_ID', 'index', 'I5_Index_ID', 'index2',
                'Sample_Project', 'Description'
            ]
        else:
            headers = [
                'Sample_ID', 'Sample_Name', 'Sample_Plate', 'Sample_Well',
                'I7_Index_ID', 'index', 'Sample_Project', 'Description'
            ]

        lines.append(','.join(headers))

        # Data rows
        for sample in self.samples:
            if has_index2:
                row = [
                    sample.get('Sample_ID', ''),
                    sample.get('Sample_Name', ''),
                    sample.get('Sample_Plate', ''),
                    sample.get('Sample_Well', ''),
                    sample.get('I7_Index_ID', ''),
                    sample.get('index', ''),
                    sample.get('I5_Index_ID', ''),
                    sample.get('index2', ''),
                    sample.get('Sample_Project', ''),
                    sample.get('Description', ''),
                ]
            else:
                row = [
                    sample.get('Sample_ID', ''),
                    sample.get('Sample_Name', ''),
                    sample.get('Sample_Plate', ''),
                    sample.get('Sample_Well', ''),
                    sample.get('I7_Index_ID', ''),
                    sample.get('index', ''),
                    sample.get('Sample_Project', ''),
                    sample.get('Description', ''),
                ]
            lines.append(','.join(row))

        return lines

    def generate(self) -> str:
        """
        Generate the complete sample sheet as a string.

        Returns:
            Sample sheet content as a string
        """
        lines = []
        lines.extend(self._generate_header())
        lines.extend(self._generate_reads())
        lines.extend(self._generate_settings())
        lines.extend(self._generate_data())

        return '\n'.join(lines)

    def save_to_file(self, filepath: str):
        """Save the sample sheet to a file."""
        content = self.generate()
        with open(filepath, 'w', newline='') as f:
            f.write(content)

    def to_response(self, filename: str = None):
        """
        Generate a Django HttpResponse for download.

        Args:
            filename: Output filename (defaults to run_name.csv)
        """
        from django.http import HttpResponse

        if not filename:
            filename = f'{self.run_name}_SampleSheet.csv'

        content = self.generate()

        response = HttpResponse(content, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response


class BatchSampleSheetGenerator:
    """
    Generate multiple sample sheets for batch processing.
    """

    @staticmethod
    def generate_for_plate(plate, run_name: str = None) -> SampleSheetGenerator:
        """
        Generate a sample sheet from a PCR plate.

        Args:
            plate: PCRPlate model instance
            run_name: Optional run name (defaults to plate barcode)
        """
        run_name = run_name or f"Run_{plate.barcode}"
        generator = SampleSheetGenerator(run_name=run_name)

        for well in plate.wells.filter(sample__isnull=False):
            generator.add_sample(
                sample_id=well.sample.sample_id,
                sample_name=well.sample.sample_id,
                index1='',  # Would need to get from library prep
                description=f'Well {well.position}',
                sample_well=well.position,
            )

        return generator

    @staticmethod
    def generate_for_run(instrument_run, libraries) -> SampleSheetGenerator:
        """
        Generate a sample sheet for an instrument run with libraries.

        Args:
            instrument_run: InstrumentRun model instance
            libraries: QuerySet of NGSLibrary instances
        """
        generator = SampleSheetGenerator(
            run_name=instrument_run.run_id,
            experiment_name=instrument_run.protocol_name or instrument_run.run_id,
        )

        for library in libraries:
            generator.add_sample_from_ngs_library(library)

        return generator
