from accounts.models import User
from basket.models import Basket
from commerce.services import CheckoutService
from django.test import TestCase


class CheckoutServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
        )

    def test_empty_basket_cannot_enter_checkout(self):
        basket = Basket.objects.create(user=self.user)

        intent, error = (
            CheckoutService.create_payment_intent_for_basket(
                basket=basket, user=self.user, post_data={}
            )
        )

        self.assertIsNone(intent)
        self.assertEqual(error, "Your basket is empty.")
