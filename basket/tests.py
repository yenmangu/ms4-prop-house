# Start Setup
# This section is needed for the tests to show up in VSCode testing panel.
# It is not needed for `python manage.py test basket.tests`
# Uncomment below to enable.

# import os
# import django

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "prop_house.settings")

# django.setup()

# End Setup

import json
from django.test import TestCase, Client
from django.urls import reverse
from .models import Basket
from catalogue.models import Product


class BasketSessionTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.product = Product.objects.create(
            name="Test Prop",
            price=10.00,
            stock_quantity=5,
        )

        self.update_url = reverse("basket:update")

    def test_basket_session_persistence(self):
        """
        Tests if basket_id persist in session between ADD and REMOVE calls.
        """
        # 1st Request: ADD item
        payload = {
            "product_id": self.product.id,
            "quantity": 1,
            "action": "add",
        }
        response = self.client.post(
            self.update_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)

        # Check if session has ID immediately after ADD

        session = self.client.session
        session_key = session.session_key

        basket = Basket.objects.filter(
            session_key=session_key,
        ).first()

        self.assertIsNotNone(
            basket, "basket should be in session after ADD"
        )

        # # 2nd Request: REMOVE the item
        # # Client maintains cookies, so should send sessionid back

        response = self.client.post(
            self.update_url,
            data=json.dumps(payload),
            content_type="application/json",
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)

        # # Inspect session after REMOVE
        session_after = self.client.session

        self.assertEqual(
            session_key,
            session_after.session_key,
            "Session Key changed between requests!",
        )
