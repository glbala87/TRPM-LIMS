# transfers/services/tracking.py

"""
Tracking service for sample movements between locations.

Provides functionality to track sample transfers, monitor shipment status,
and generate movement reports.
"""

from django.utils import timezone
from django.db.models import Count, Q, F
from datetime import timedelta
from typing import Dict, List, Optional, Any


class TransferTrackingService:
    """
    Service for tracking and monitoring sample transfers.

    Provides methods for:
    - Creating and managing transfers
    - Tracking shipment status
    - Monitoring overdue transfers
    - Generating movement reports
    """

    def __init__(self):
        self.now = timezone.now()

    def create_transfer(
        self,
        source_location: str,
        destination_location: str,
        items: List[Dict[str, Any]],
        user=None,
        courier: str = "",
        tracking_number: str = "",
        shipment_conditions: str = "AMBIENT",
        expected_arrival_date=None,
        notes: str = "",
        special_instructions: str = ""
    ):
        """
        Create a new sample transfer with items.

        Args:
            source_location: Origin facility/location
            destination_location: Destination facility/location
            items: List of dicts with sample_id, quantity, notes, etc.
            user: User initiating the transfer
            courier: Courier/shipping company
            tracking_number: Shipping tracking number
            shipment_conditions: Temperature conditions
            expected_arrival_date: Expected arrival datetime
            notes: Additional notes
            special_instructions: Special handling instructions

        Returns:
            Transfer instance
        """
        from ..models import Transfer, TransferItem

        transfer = Transfer.objects.create(
            source_location=source_location,
            destination_location=destination_location,
            courier=courier,
            tracking_number=tracking_number,
            shipment_conditions=shipment_conditions,
            expected_arrival_date=expected_arrival_date,
            notes=notes,
            special_instructions=special_instructions,
            initiated_by=user,
            status='PENDING'
        )

        # Create transfer items
        for item_data in items:
            TransferItem.objects.create(
                transfer=transfer,
                sample_id=item_data.get('sample_id', ''),
                lab_order_id=item_data.get('lab_order_id'),
                quantity=item_data.get('quantity', 1),
                container_type=item_data.get('container_type', ''),
                storage_position=item_data.get('storage_position', ''),
                condition_on_departure=item_data.get('condition', ''),
                notes=item_data.get('notes', '')
            )

        return transfer

    def dispatch_transfer(self, transfer, user=None):
        """
        Mark a transfer as dispatched/in transit.

        Args:
            transfer: Transfer instance
            user: User dispatching the transfer

        Returns:
            Updated Transfer instance
        """
        transfer.mark_in_transit(user)
        self._log_movement(
            transfer,
            'DISPATCHED',
            f"Transfer dispatched from {transfer.source_location}",
            user
        )
        return transfer

    def receive_transfer(
        self,
        transfer,
        user=None,
        item_conditions: Optional[Dict[str, str]] = None
    ):
        """
        Mark a transfer as received.

        Args:
            transfer: Transfer instance
            user: User receiving the transfer
            item_conditions: Dict mapping sample_id to condition on arrival

        Returns:
            Updated Transfer instance
        """
        transfer.mark_received(user)

        # Update individual items
        for item in transfer.items.all():
            condition = None
            if item_conditions and item.sample_id in item_conditions:
                condition = item_conditions[item.sample_id]
            item.mark_received(user, condition)

        self._log_movement(
            transfer,
            'RECEIVED',
            f"Transfer received at {transfer.destination_location}",
            user
        )
        return transfer

    def get_transfer_status(self, transfer_number: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed status of a transfer.

        Args:
            transfer_number: Transfer identifier

        Returns:
            Dict with transfer details and status
        """
        from ..models import Transfer

        try:
            transfer = Transfer.objects.get(transfer_number=transfer_number)
        except Transfer.DoesNotExist:
            return None

        return {
            'transfer_number': transfer.transfer_number,
            'status': transfer.status,
            'status_display': transfer.get_status_display(),
            'source_location': transfer.source_location,
            'destination_location': transfer.destination_location,
            'transfer_date': transfer.transfer_date,
            'expected_arrival_date': transfer.expected_arrival_date,
            'actual_arrival_date': transfer.actual_arrival_date,
            'courier': transfer.courier,
            'tracking_number': transfer.tracking_number,
            'shipment_conditions': transfer.get_shipment_conditions_display(),
            'total_items': transfer.total_items,
            'total_quantity': transfer.total_quantity,
            'is_overdue': transfer.is_overdue,
            'items': [
                {
                    'sample_id': item.sample_id,
                    'quantity': item.quantity,
                    'is_received': item.is_received,
                    'has_discrepancy': item.has_discrepancy
                }
                for item in transfer.items.all()
            ]
        }

    def get_sample_movement_history(self, sample_id: str) -> List[Dict[str, Any]]:
        """
        Get the complete movement history of a sample.

        Args:
            sample_id: Sample identifier

        Returns:
            List of movement records for the sample
        """
        from ..models import TransferItem

        items = TransferItem.objects.filter(
            sample_id=sample_id
        ).select_related(
            'transfer'
        ).order_by('-transfer__transfer_date')

        history = []
        for item in items:
            history.append({
                'transfer_number': item.transfer.transfer_number,
                'transfer_date': item.transfer.transfer_date,
                'source': item.transfer.source_location,
                'destination': item.transfer.destination_location,
                'status': item.transfer.status,
                'quantity': item.quantity,
                'condition_sent': item.condition_on_departure,
                'condition_received': item.condition_on_arrival,
                'received_at': item.received_at,
                'has_discrepancy': item.has_discrepancy,
                'discrepancy_notes': item.discrepancy_notes
            })

        return history

    def get_active_transfers(self) -> List:
        """
        Get all active (pending or in transit) transfers.

        Returns:
            QuerySet of active transfers
        """
        from ..models import Transfer

        return Transfer.objects.filter(
            status__in=['PENDING', 'IN_TRANSIT']
        ).select_related(
            'initiated_by'
        ).prefetch_related(
            'items'
        ).order_by('-transfer_date')

    def get_overdue_transfers(self) -> List:
        """
        Get all overdue transfers.

        Returns:
            List of overdue transfer records
        """
        from ..models import Transfer

        overdue = Transfer.objects.filter(
            status='IN_TRANSIT',
            expected_arrival_date__lt=self.now
        ).select_related(
            'initiated_by'
        )

        return [
            {
                'transfer': t,
                'days_overdue': (self.now - t.expected_arrival_date).days,
                'hours_overdue': int((self.now - t.expected_arrival_date).total_seconds() / 3600)
            }
            for t in overdue
        ]

    def get_transfers_by_location(
        self,
        location: str,
        direction: str = 'both'
    ) -> List:
        """
        Get transfers for a specific location.

        Args:
            location: Location name
            direction: 'incoming', 'outgoing', or 'both'

        Returns:
            QuerySet of transfers
        """
        from ..models import Transfer

        filters = Q()

        if direction in ['outgoing', 'both']:
            filters |= Q(source_location__icontains=location)
        if direction in ['incoming', 'both']:
            filters |= Q(destination_location__icontains=location)

        return Transfer.objects.filter(filters).order_by('-transfer_date')

    def get_transfer_statistics(
        self,
        start_date=None,
        end_date=None
    ) -> Dict[str, Any]:
        """
        Get transfer statistics for a date range.

        Args:
            start_date: Start of date range (defaults to 30 days ago)
            end_date: End of date range (defaults to now)

        Returns:
            Dict with statistics
        """
        from ..models import Transfer

        if end_date is None:
            end_date = self.now
        if start_date is None:
            start_date = end_date - timedelta(days=30)

        transfers = Transfer.objects.filter(
            transfer_date__gte=start_date,
            transfer_date__lte=end_date
        )

        total = transfers.count()
        by_status = transfers.values('status').annotate(count=Count('id'))

        # Calculate average transit time for received transfers
        received = transfers.filter(
            status='RECEIVED',
            actual_arrival_date__isnull=False
        )

        avg_transit_time = None
        if received.exists():
            transit_times = []
            for t in received:
                delta = t.actual_arrival_date - t.transfer_date
                transit_times.append(delta.total_seconds() / 3600)  # Convert to hours
            avg_transit_time = sum(transit_times) / len(transit_times)

        # On-time delivery rate
        on_time_count = received.filter(
            actual_arrival_date__lte=F('expected_arrival_date')
        ).count()
        on_time_rate = (on_time_count / received.count() * 100) if received.count() > 0 else None

        return {
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'total_transfers': total,
            'by_status': {item['status']: item['count'] for item in by_status},
            'avg_transit_time_hours': round(avg_transit_time, 1) if avg_transit_time else None,
            'on_time_delivery_rate': round(on_time_rate, 1) if on_time_rate else None,
            'total_items_transferred': sum(t.total_quantity for t in transfers)
        }

    def report_discrepancy(
        self,
        transfer_number: str,
        sample_id: str,
        description: str,
        user=None
    ) -> bool:
        """
        Report a discrepancy for a transfer item.

        Args:
            transfer_number: Transfer identifier
            sample_id: Sample identifier
            description: Description of the discrepancy
            user: User reporting the discrepancy

        Returns:
            True if discrepancy was reported successfully
        """
        from ..models import Transfer, TransferItem

        try:
            transfer = Transfer.objects.get(transfer_number=transfer_number)
            item = transfer.items.get(sample_id=sample_id)
            item.report_discrepancy(description)

            self._log_movement(
                transfer,
                'DISCREPANCY',
                f"Discrepancy reported for {sample_id}: {description}",
                user
            )
            return True
        except (Transfer.DoesNotExist, TransferItem.DoesNotExist):
            return False

    def _log_movement(self, transfer, action, description, user=None):
        """
        Internal method to log transfer movements.

        This can be extended to integrate with the audit app or
        create dedicated movement logs.
        """
        # For now, this is a placeholder that can be extended
        # to create audit log entries or send notifications
        pass

    def search_transfers(
        self,
        query: str = None,
        status: str = None,
        courier: str = None,
        start_date=None,
        end_date=None
    ) -> List:
        """
        Search transfers with various filters.

        Args:
            query: Search term for transfer number, locations, tracking number
            status: Filter by status
            courier: Filter by courier
            start_date: Filter by start date
            end_date: Filter by end date

        Returns:
            QuerySet of matching transfers
        """
        from ..models import Transfer

        filters = Q()

        if query:
            filters &= (
                Q(transfer_number__icontains=query) |
                Q(source_location__icontains=query) |
                Q(destination_location__icontains=query) |
                Q(tracking_number__icontains=query)
            )

        if status:
            filters &= Q(status=status)

        if courier:
            filters &= Q(courier__icontains=courier)

        if start_date:
            filters &= Q(transfer_date__gte=start_date)

        if end_date:
            filters &= Q(transfer_date__lte=end_date)

        return Transfer.objects.filter(filters).order_by('-transfer_date')
