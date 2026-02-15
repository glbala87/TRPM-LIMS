"""
Pagination classes for the TRPM-LIMS REST API.
"""
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination for list views.
    """
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination for endpoints that may return large datasets.
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 500


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination for endpoints with smaller datasets or mobile views.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class FlexibleLimitOffsetPagination(LimitOffsetPagination):
    """
    Flexible pagination using limit/offset for more granular control.
    """
    default_limit = 25
    max_limit = 200


class SampleListPagination(PageNumberPagination):
    """
    Pagination specifically for sample list views.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class ReportListPagination(PageNumberPagination):
    """
    Pagination for report list views.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
