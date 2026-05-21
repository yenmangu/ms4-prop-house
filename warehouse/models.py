from django.db import models
from django.db.models import (
    F,
    Q,
    Case,
    ExpressionWrapper,
    Value,
    When,
)
from django.conf import Settings
from django.utils import timezone
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from catalogue.models import Product
    from commerce.models import OrderItem


class StockItem(models.Model):
    """
    _Domain:_ Warehouse / Asset Management

    Represents a physical asset in the warehouse, identified by a serial number or barcode.
    Source of truth for pysical state of inventory: how many of each actual items exist.

    _Real world context:_
    Product (`catalogue.Product`) is an abstract concept, (e.g., 'Police Tape').

    `StockItem` is the physical
    representation of an actual tangible unit(e.g., 'Roll #402').
    Tracks the asset's lifecycle- from purchase, through various hire cycles,
    maintenance and eventual retirement.

    _Scaling Potential:_
    If inventory scales to a second warehouse, we just add a 'location' field to the `StockItem`.
    Does not change sales process at all.
    """

    class StockStatus(models.TextChoices):
        AVAILABLE = "AV", "Available"
        ON_HIRE = "OH", "On Hire"
        MAINTENANCE = "MA", "Maintenance"
        RETIRED = "RE", "Retired"

    product = models.ForeignKey(
        "catalogue.Product",
        on_delete=models.CASCADE,
        related_name="stock_items",
    )

    serial_number = models.CharField(
        max_length=100,
        unique=True,
    )

    status = models.CharField(
        max_length=2,
        choices=StockStatus.choices,
        default=StockStatus.AVAILABLE,
    )

    if TYPE_CHECKING:
        product: Product

    def __str__(self):
        return f"{self.product.name} [{self.serial_number}]"


class HireRecordQuerySet(models.QuerySet):
    def with_alert_levels(self):
        now = timezone.now()
        whole_duration = F("due_date") - F("out_date")

        status = HireRecord.HireStatus
        return self.annotate(
            calculated_alert=Case(
                When(
                    returned_date__isnull=False,
                    then=Value(status.RETURNED),
                ),
                When(due_date__lt=now, then=Value(status.OVERDUE)),
                When(
                    # If current time has advanced past 90% of the timeline allocations
                    Q(returned_date__isnull=True)
                    & Q(out_date__isnull=False)
                    & Q(
                        out_date__lte=ExpressionWrapper(
                            now - (whole_duration * 0.9),
                            output_field=models.DateTimeField(),
                        )
                    ),
                    then=Value(
                        status.WARNING
                    ),  # Warning (Impending Overdue)
                ),
                output_field=models.CharField(max_length=2),
                default=Value(status.NOMINAL),
            )
        )

    def for_dashboard_user(self, user):
        """
        Single source of truth for user's hire data.
        Combines filtering, N+1 optimisations and alert calculations.
        """
        return (
            self.filter(order_item__order__user=user)
            .select_related(
                "stock_item__product", "order_item__order"
            )
            .with_alert_levels()
            .order_by("-order_item__order__created_at")
        )


class HireRecord(models.Model):
    """
    _Domain:_ Logistics / Fulfillment

    The 'bridge' entity that links the commercial order (`commerce.Order`) to a physical asset (warehouse.StockItem).

    _Real World Context:_
    This model serves to encapsulate the 'Warehouse' department's data.
    Sales department (`commerce`) cares that 'x' amount of a certain Product were paid for,
    the Warehouse cares *which* 'x' assets leave the building, their condition and when they come back.

    Pointing to `commerce.OrderItem` instead of `commerce.Order`
    enables granular tracking of individual assets within a multi-item order,
    supporting partial returns, and specific asset condition reporting.

    _Data Integrity:_
    Using `models.PROTECT` on both `order_item` and `stock_item` ensures
    no record that represents a physical movement of stock can be deleted.

    If customer order is cancelled or physical item is destroyed, the `HireRecord` must remain
    as a permanent audit trail of asset's history and company's fulfillment activity.
    """

    class HireStatus(models.TextChoices):
        NOMINAL = "NO", "Nominal"
        WARNING = "WA", "Warning"
        OVERDUE = "OV", "Overdue"
        RETURNED = "RE", "Returned"

    order_item = models.ForeignKey(
        "commerce.OrderItem",
        on_delete=models.PROTECT,
        related_name="hires",
    )

    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.PROTECT,
        related_name="hire_history",
    )

    # Timing Fields
    out_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateTimeField()
    returned_date = models.DateTimeField(null=True, blank=True)

    # QC
    condition_on_out = models.TextField(blank=True)
    condition_on_return = models.TextField(blank=True)

    # QuerySet ref
    objects = HireRecordQuerySet.as_manager()

    if TYPE_CHECKING:
        order_item: OrderItem
        # QuerySet Ref
        objects: HireRecordQuerySet

    @property
    def alert_level_label(self) -> str:
        """
        Python fallback property descriptor providing runtime visibility
        if evaluated outside an annotated query chain context.
        """

        status_code = getattr(
            self, "calculated_alert", self.HireStatus.NOMINAL
        )

        if status_code is None:
            print("NO STATUS")
            status_code = self.HireStatus.NOMINAL

        return self.HireStatus(status_code).label

    @property
    def days_remaining(self) -> int:
        """
        Calculate days until item is due back.
        Returns 0 if overdue or already returned.
        """
        if self.returned_date or not self.due_date:
            return 0

        delta = self.due_date - timezone.now()
        return max(0, delta.days)

    @property
    def is_overdue(self) -> bool:
        return (
            not self.returned_date and self.due_date < timezone.now()
        )

    def get_order_id(self) -> Optional[int]:
        if self.order_item and self.order_item.order:
            return self.order_item.order.id

        # Implicit else - return None
        return None

    def __str__(self):
        return f"Hire: {self.stock_item.serial_number} for Order Item {self.order_item.pk}"
