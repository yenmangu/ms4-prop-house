from accounts.views import (
    InitiateMembershipCheckoutView,
    MembershipOptionsView,
    MembershipSuccessView,
    UserDashboardHireView,
)
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path(
        "membership/",
        MembershipOptionsView.as_view(),
        name=MembershipOptionsView.list_view_name(),
    ),
    path(
        "membership/initiate/<int:pk>/",
        InitiateMembershipCheckoutView.as_view(),
        name="initiate_membership",
    ),
    path(
        "membership/success/",
        MembershipSuccessView.as_view(),
        name="membership_success",
    ),
    path(
        "dashboard/",
        UserDashboardHireView.as_view(),
        name="dashboard",
    ),
]
