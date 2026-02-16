# molecular_diagnostics/tasks/annotation_tasks.py
"""
Celery tasks for background variant annotation processing.
"""

import logging
from celery import shared_task
from django.db import transaction

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
)
def annotate_variant_task(self, variant_call_id: int, force_refresh: bool = False):
    """
    Annotate a single variant call in the background.

    Args:
        variant_call_id: ID of the VariantCall to annotate
        force_refresh: Skip cache and fetch fresh data

    Returns:
        Dictionary with annotation status
    """
    from molecular_diagnostics.models import VariantCall
    from molecular_diagnostics.services.annotation_service import AnnotationService

    try:
        variant_call = VariantCall.objects.select_related('gene').get(pk=variant_call_id)
    except VariantCall.DoesNotExist:
        logger.error(f"VariantCall {variant_call_id} not found")
        return {'status': 'error', 'message': 'Variant call not found'}

    service = AnnotationService()

    try:
        annotation = service.annotate_variant(variant_call, force_refresh=force_refresh)
        return {
            'status': 'success',
            'annotation_id': annotation.id,
            'annotation_status': annotation.annotation_status,
            'clinical_significance': annotation.clinical_significance,
        }
    except Exception as e:
        logger.error(f"Annotation task failed for variant {variant_call_id}: {e}")
        raise


@shared_task(
    bind=True,
    max_retries=2,
    default_retry_delay=120,
)
def annotate_result_task(self, molecular_result_id: int, force_refresh: bool = False):
    """
    Annotate all variants in a molecular result.

    Args:
        molecular_result_id: ID of the MolecularResult
        force_refresh: Skip cache and fetch fresh data

    Returns:
        Dictionary with annotation stats
    """
    from molecular_diagnostics.models import MolecularResult
    from molecular_diagnostics.services.annotation_service import AnnotationService

    try:
        result = MolecularResult.objects.get(pk=molecular_result_id)
    except MolecularResult.DoesNotExist:
        logger.error(f"MolecularResult {molecular_result_id} not found")
        return {'status': 'error', 'message': 'Molecular result not found'}

    service = AnnotationService()

    try:
        annotations = service.annotate_result(result, force_refresh=force_refresh)

        stats = {
            'status': 'success',
            'total_variants': len(annotations),
            'completed': sum(1 for a in annotations if a.annotation_status == 'COMPLETED'),
            'partial': sum(1 for a in annotations if a.annotation_status == 'PARTIAL'),
            'not_found': sum(1 for a in annotations if a.annotation_status == 'NOT_FOUND'),
            'failed': sum(1 for a in annotations if a.annotation_status == 'FAILED'),
        }

        logger.info(f"Annotated {stats['total_variants']} variants for result {molecular_result_id}")
        return stats

    except Exception as e:
        logger.error(f"Result annotation task failed for {molecular_result_id}: {e}")
        raise self.retry(exc=e)


@shared_task(
    bind=True,
    max_retries=1,
    time_limit=3600,  # 1 hour max
    soft_time_limit=3300,  # 55 min soft limit
)
def bulk_annotate_task(
    self,
    variant_call_ids: list,
    force_refresh: bool = False,
    notify_user_id: int = None
):
    """
    Bulk annotate multiple variants in the background.

    Args:
        variant_call_ids: List of VariantCall IDs to annotate
        force_refresh: Skip cache and fetch fresh data
        notify_user_id: User ID to notify on completion

    Returns:
        Dictionary with annotation stats
    """
    from molecular_diagnostics.models import VariantCall
    from molecular_diagnostics.services.annotation_service import AnnotationService

    variant_calls = VariantCall.objects.filter(
        pk__in=variant_call_ids
    ).select_related('gene')

    if not variant_calls.exists():
        logger.warning(f"No variant calls found for IDs: {variant_call_ids}")
        return {'status': 'error', 'message': 'No variant calls found'}

    service = AnnotationService()

    def progress_callback(current, total, variant):
        # Update task state for progress tracking
        self.update_state(
            state='PROGRESS',
            meta={
                'current': current,
                'total': total,
                'percent': int((current / total) * 100),
            }
        )

    try:
        stats = service.bulk_annotate(
            list(variant_calls),
            force_refresh=force_refresh,
            progress_callback=progress_callback
        )

        result = {
            'status': 'success',
            'total': stats['total'],
            'success_count': stats['success_count'],
            'partial_count': stats['partial_count'],
            'not_found_count': stats['not_found_count'],
            'failed_count': stats['failed_count'],
        }

        # Notify user if requested
        if notify_user_id:
            _notify_user_completion(notify_user_id, result)

        logger.info(f"Bulk annotation complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Bulk annotation task failed: {e}")
        raise


@shared_task(
    bind=True,
    time_limit=7200,  # 2 hours max
)
def refresh_stale_annotations_task(self, days_old: int = 30):
    """
    Refresh annotations that are older than specified days.

    Typically run as a scheduled task (e.g., weekly).

    Args:
        days_old: Refresh annotations older than this many days

    Returns:
        Dictionary with refresh stats
    """
    from molecular_diagnostics.services.annotation_service import AnnotationService

    logger.info(f"Starting stale annotation refresh (older than {days_old} days)")

    service = AnnotationService()

    try:
        stats = service.refresh_stale_annotations(days_old=days_old)

        result = {
            'status': 'success',
            'total_refreshed': stats['total'],
            'success_count': stats['success_count'],
            'failed_count': stats['failed_count'],
        }

        logger.info(f"Stale annotation refresh complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Stale annotation refresh failed: {e}")
        raise


@shared_task
def cleanup_annotation_cache_task(days_old: int = 90, min_hits: int = 0):
    """
    Clean up old annotation cache entries.

    Typically run as a scheduled task (e.g., monthly).

    Args:
        days_old: Delete entries older than this
        min_hits: Only delete entries with fewer hits

    Returns:
        Dictionary with cleanup stats
    """
    from molecular_diagnostics.services.annotation_service import AnnotationService

    logger.info(f"Starting annotation cache cleanup (older than {days_old} days)")

    service = AnnotationService()

    try:
        deleted_count = service.cleanup_cache(days_old=days_old, min_hits=min_hits)

        result = {
            'status': 'success',
            'deleted_count': deleted_count,
        }

        logger.info(f"Cache cleanup complete: {result}")
        return result

    except Exception as e:
        logger.error(f"Cache cleanup failed: {e}")
        raise


def _notify_user_completion(user_id: int, result: dict):
    """
    Send notification to user when bulk annotation completes.
    """
    try:
        # Try to use messaging app if available
        from messaging.models import Notification

        Notification.objects.create(
            user_id=user_id,
            title="Variant Annotation Complete",
            message=(
                f"Bulk annotation finished: {result['success_count']} successful, "
                f"{result['failed_count']} failed out of {result['total']} total."
            ),
            notification_type='INFO',
        )
    except ImportError:
        # Messaging app not available, log instead
        logger.info(f"Would notify user {user_id}: annotation complete - {result}")
    except Exception as e:
        logger.warning(f"Failed to notify user {user_id}: {e}")


# Celery beat schedule for periodic tasks
# Add to your celery.py or settings:
#
# CELERY_BEAT_SCHEDULE = {
#     'refresh-stale-annotations': {
#         'task': 'molecular_diagnostics.tasks.annotation_tasks.refresh_stale_annotations_task',
#         'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sundays at 2 AM
#         'args': (30,),
#     },
#     'cleanup-annotation-cache': {
#         'task': 'molecular_diagnostics.tasks.annotation_tasks.cleanup_annotation_cache_task',
#         'schedule': crontab(day_of_month=1, hour=3, minute=0),  # 1st of month at 3 AM
#         'args': (90, 0),
#     },
# }
