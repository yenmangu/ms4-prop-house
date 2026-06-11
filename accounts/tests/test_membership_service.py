from accounts.models import MembershipTier, User
from django.test import TestCase
from moneyed import Money
from accounts.services import MembershipService


class MembershipServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="rob",
            email="rob@example.com",
            password="testpass123",
        )

        self.tier = MembershipTier.objects.create(
            name="Pro",
            price=Money("19.99", "GBP"),
            stripe_price_id="price_test_123",
            discount_percentage=10,
            features=["10% discount", "Priority support"],
        )
        return super().setUp()

    def test_provision_tier_assigns_membership_to_user(self):

        result = MembershipService.provision_tier(
            user=self.user,
            tier_id=self.tier.id,
        )

        self.user.refresh_from_db()
        self.assertTrue(result)
        self.assertEqual(self.user.membership_tier, self.tier)

    def test_provision_tier_returns_false_for_missing_tier(self):

        result = MembershipService.provision_tier(
            user=self.user,
            tier_id=999999,
        )

        self.user.refresh_from_db()
        self.assertFalse(result)
        self.assertIsNone(self.user.membership_tier)
