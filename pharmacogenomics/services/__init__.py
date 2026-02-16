# pharmacogenomics/services/__init__.py

from .diplotype_service import DiplotypeService
from .recommendation_service import RecommendationService

__all__ = [
    'DiplotypeService',
    'RecommendationService',
]
