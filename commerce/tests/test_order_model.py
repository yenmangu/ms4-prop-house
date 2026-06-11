from django.test import TestCase

from accounts.models import User
from basket.models import Basket, Line
from catalogue.models import Product
from commerce.models import Order


# Create your tests here.
class OrderModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )

        self.product = Product.objects.create(
            name="Test Prop",
            slug="test-prop",
            description="A test prop.",
            price=10,
            stock_quantity=5,
        )

        self.basket = Basket.objects.create(
            user=self.user,
        )

        Line.objects.create(
            basket=self.basket,
            product=self.product,
            quantity=2,
            price_at_addition=self.product.price,
        )

    def test_create_from_basket_stores_delivery_snapshot(self):
        self.address_data = {
            "delivery_contact_name": "Reece Selvadorai",
            "phone_number": "07123456789",
            "house_name_or_number": "Unit 5",
            "address_line_1": "Production Yard",
            "address_line_2": "Studio Estate",
            "town_or_city": "Chelmsford",
            "county": "Essex",
            "postcode": "CM1 1AA",
            "country": "GB",
        }

        order = Order.create_from_basket(
            basket=self.basket,
            user=self.user,
            name="Rob Shelford",
            email="rob@example.com",
            address_data=self.address_data,
        )

        self.assertEqual(order.full_name, "Rob Shelford")
        self.assertEqual(order.email, "rob@example.com")
        self.assertEqual(
            order.delivery_contact_name, "Reece Selvadorai"
        )
        self.assertEqual(order.delivery_phone_number, "07123456789")
        self.assertEqual(
            order.delivery_house_name_or_number, "Unit 5"
        )
        self.assertEqual(
            order.delivery_address_line_1, "Production Yard"
        )
        self.assertEqual(
            order.delivery_address_line_2, "Studio Estate"
        )
        self.assertEqual(order.delivery_town_or_city, "Chelmsford")
        self.assertEqual(order.delivery_county, "Essex")
        self.assertEqual(order.delivery_postcode, "CM1 1AA")
        self.assertEqual(str(order.delivery_country), "GB")
