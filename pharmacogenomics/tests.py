"""Smoke tests for pharmacogenomics app."""
import pytest
from pharmacogenomics.models import PGxGene, StarAllele

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_pgx_gene_and_star_allele():
    gene = PGxGene.objects.create(symbol='CYP2D6', name='Cytochrome P450 2D6')
    allele = StarAllele.objects.create(gene=gene, name='*1')
    assert gene.pk is not None
    assert allele.pk is not None
    assert allele.gene == gene
