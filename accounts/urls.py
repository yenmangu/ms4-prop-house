from accounts.views import (
    MembershipOptionsView,
    UserDashboardHireView,
)
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path(
        "membership/",
        MembershipOptionsView.as_view(),
        name=MembershipOptionsView.list_view_name,
    ),
    path(
        "dashboard/",
        UserDashboardHireView.as_view(),
        name="dashboard",
    ),
]
