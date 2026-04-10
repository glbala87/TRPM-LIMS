"""Smoke tests for projects app."""
import pytest
from projects.models import ProjectCategory, Project

pytestmark = [pytest.mark.django_db, pytest.mark.smoke]


def test_project_category_create():
    c = ProjectCategory.objects.create(name='Oncology', code='ONCO')
    assert c.pk is not None


def test_project_create():
    p = Project.objects.create(project_id='PROJ-001', name='BRCA Screening')
    assert p.pk is not None
