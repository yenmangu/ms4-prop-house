from django.http import HttpRequest
from .models import Basket


def perform_merge_basket(sender, request: HttpRequest, user, **kwargs):
    """
    When a User logs in, check if they have a guest basket in session.
    If they do, link to their user account.

    Args:
        sender (_type_): _description_
        request (_type_): _description_
        user (_type_): _description_
    """
    guest_basket_id = request.session.get("basket_id")
    if guest_basket_id:
        try:
            guest_basket = Basket.objects.get(id=guest_basket_id, user__isnull=True)

            existing_user_basket = (
                Basket.objects.filter(
                    user=user,
                    status=Basket.Status.OPEN,
                )
                .exclude(id=guest_basket_id)
                .first()
            )

            if existing_user_basket:
                # Merge and associate basket with user
                guest_basket.merge_into(existing_user_basket)
                request.session["basket_id"] = str(existing_user_basket.id)
            else:
                guest_basket.user = user
                guest_basket.save()

        except Basket.DoesNotExist:
            pass
