from typing import TYPE_CHECKING

from accounts.forms import CustomerAddressForm
from accounts.models import Address
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.http import QueryDict
    from models import User
    from typing import Tuple


class AddressService:
    """
    Manage addresses from address_data from commerce.services.
    Handles CustomerAddressForm management and validation.
    Handles saving default address to User model.
    """

    @staticmethod
    def validate_address_form(
        post_data: QueryDict,
    ) -> Tuple[CustomerAddressForm | None, str | None]:
        """
        Validate post_data against CustomerAddressForm.

        Returns:
            (form, None) if valid.
            (None, errors_json) if invalid.
        """

        address_form = CustomerAddressForm(post_data)
        if not address_form.is_valid():
            return None, address_form.errors.as_json()

        return address_form, None

    @staticmethod
    def save_default_address(
        user: User,
        address_form: CustomerAddressForm,
        post_data: QueryDict,
    ) -> Address | None:
        """
        Save default address to User model
        """

        if not user.is_authenticated:
            return None

        should_save_default = (
            post_data.get("save_as_default_address") == "on"
        )

        if not should_save_default:
            return None

        Address.objects.filter(user=user, is_default=True).update(
            is_default=False
        )

        address: Address = address_form.save(commit=False)
        address.user = user
        address.label = "Default"
        address.is_default = True
        address.save()

        return address
