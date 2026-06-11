from django.http import QueryDict
from django.test import TestCase

from accounts.models import Address, User
from accounts.forms import CustomerAddressForm
from accounts.services import AddressService


class AddressServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rob_address_test",
            email="rob@example.com",
            password="testpass123",
        )

        self.post_data = QueryDict(mutable=True)
        self.test_name = "Robert J Shelford"
        self.test_postcode = "CM0 7JF"
        self.test_house_name = "Test Fsrm"
        self.test_town_city = "Clacton"
        self.post_data.update(
            {
                "delivery_contact_name": self.test_name,
                "phone_number": "07991590448",
                "house_name_or_number": self.test_house_name,
                "address_line_1": "Test Road",
                "address_line_2": "",
                "town_or_city": self.test_town_city,
                "postcode": self.test_postcode,
                "county": "Essex",
                "country": "GB",
                "save_as_default_address": "on",
            }
        )

    def test_validate_form_with_error(self):
        self.post_data.update(
            {
                "postcode": "",
            }
        )
        address_form, error = AddressService.validate_address_form(
            self.post_data
        )

        self.assertIsNone(address_form, "Address has errors")
        self.assertIsNotNone(error)

    def test_save_default_creates_address(self):
        address_form = CustomerAddressForm(self.post_data)
        if not address_form.is_valid():

            print(f"Errors: {address_form.errors.as_json()}")

        self.assertTrue(address_form.is_valid())

        address = AddressService.save_default_address(
            user=self.user,
            address_form=address_form,
            post_data=self.post_data,
        )

        self.assertIsNotNone(address)
        self.assertEqual(Address.objects.count(), 1)

        saved_address = Address.objects.get(
            user=self.user,
        )

        self.assertTrue(saved_address.is_default)
        self.assertEqual(saved_address.postcode, self.test_postcode)
        self.assertEqual(
            saved_address.house_name_or_number, self.test_house_name
        )
        self.assertEqual(
            saved_address.delivery_contact_name, self.test_name
        )
