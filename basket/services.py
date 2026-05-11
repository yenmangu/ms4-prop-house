from django.http import HttpRequest
from .models import Basket


def get_basket_for_request(request: HttpRequest):
    """
    Retrieves the active basket for a given request across all domains (Catalogue, Basket, etc.).

    This function bridges the gap between 'Lazy' middleware and 'Active' views by
    performing a hierarchical search:
    1. Authenticated User (Highest priority)
    2. Explicit session ID (Stored from previous interactions)
    3. Session Key (Orphan recovery for anonymous users)
    4. Ghost Instance (Unsaved fallback to prevent 0-count display issues)
    """

    # Check auth user
    if request.user.is_authenticated:
        basket = Basket.objects.filter(
            user=request.user,
            status=Basket.Status.OPEN,
        ).last()

        if not basket:
            basket = Basket.objects.create(
                user=request.user,
                status=Basket.Status.OPEN,
            )
        return basket

    # Check Session ID
    basket_id = request.session.get("basket_id")
    if basket_id:
        basket = Basket.objects.filter(
            id=basket_id,
            status=Basket.Status.OPEN,
        ).first()
        if basket:
            return basket
        else:
            # Self-healing stale session ID logic
            del request.session["basket_id"]
            request.session.modified = True

    # Check Session Key (Orphan lookup)
    if request.session.session_key:
        orphan = Basket.objects.filter(
            session_key=request.session.session_key,
            status=Basket.Status.OPEN,
            user__isnull=True,
        ).first()
        if orphan:
            # Sync session ID
            request.session["basket_id"] = str(orphan.id)
            return orphan

    # Failsafe: Ghost Basket
    return Basket(session_key=request.session.session_key)


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
