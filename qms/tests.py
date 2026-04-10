"""Smoke tests for qms app."""
import pytest
from qms.models import DocumentCategory, DocumentTag

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_document_category_create():
    c = DocumentCategory.objects.create(code='SOP', name='Standard Operating Procedures')
    assert c.pk is not None


def test_document_tag_create():
    t = DocumentTag.objects.create(name='draft')
    assert t.pk is not None
