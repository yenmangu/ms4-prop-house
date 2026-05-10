from accounts.views import UserDashboardHireView
from django.urls import path

app_name = "accounts"

urlpatterns = [
    path(
        "dashboard/",
        UserDashboardHireView.as_view(),
        name="dashboard",
    ),
]
