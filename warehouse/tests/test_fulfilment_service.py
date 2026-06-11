from accounts.models import User
from basket.models import Basket, Line
from catalogue.models import Category, Product
from commerce.models import Order, OrderItem
from django.test import TestCase
from moneyed import Money
from warehouse.models import StockItem
from warehouse.services import (
    StockFulfilmentError,
    fulfil_order_items,
    get_stock_availability,
)


class FulFilmentServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="password123",
        )

        self.category = Category.objects.create(
            name="Props",
            slug="props",
        )

        self.product = Product.objects.create(
            name="Smoke Machine",
            slug="smoke-machine",
            description="Test product",
            stock_quantity=5,
            price=Money(100, "GBP"),
        )

        # self.stock_item = StockItem.objects.create(
        #     product=self.product,
        #     physical_count=5,
        #     allocated_count=0,
        # )

        self.stock_item_one = StockItem.objects.create(
            product=self.product,
            serial_number="001",
            status=StockItem.StockStatus.AVAILABLE,
        )

        self.stock_item_two = StockItem.objects.create(
            product=self.product,
            serial_number="002",
            status=StockItem.StockStatus.AVAILABLE,
        )

        self.basket = Basket.objects.create(user=self.user)

        self.line = Line.objects.create(
            basket=self.basket,
            product=self.product,
            quantity=2,
            price_at_addition=self.product.price,
        )

        self.address_data = {
            "delivery_contact_name": "Rob Shelford",
            "phone_number": "07123456789",
            "house_name_or_number": "1",
            "address_line_1": "Test Street",
            "address_line_2": "",
            "town_or_city": "Reading",
            "county": "Berkshire",
            "postcode": "RG1 1AA",
            "country": "GB",
        }

        self.order = Order.create_from_basket(
            basket=self.basket,
            user=self.user,
            name="Rob Shelford",
            email="rob@example.com",
            address_data=self.address_data,
        )

    def test_insufficient_stock_fails_fulfilment(self):
        StockItem.objects.filter(product=self.product).delete()

        StockItem.objects.create(
            product=self.product,
            status=StockItem.StockStatus.AVAILABLE,
        )

        with self.assertRaises(StockFulfilmentError):
            fulfil_order_items(self.order)

        availability = get_stock_availability(self.product)

        self.assertEqual(availability["total"], 1)
        self.assertEqual(availability["available"], 1)
        self.assertEqual(availability["on_hire"], 0)

    def test_successful_fulfilment_reduces_stock(self):

        fulfil_order_items(self.order)

        availability = get_stock_availability(self.product)

        self.assertEqual(availability["total"], 2)
        self.assertEqual(availability["available"], 0)
        self.assertEqual(availability["on_hire"], 2)
