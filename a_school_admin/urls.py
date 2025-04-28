from django.urls import path
from . import views


urlpatterns = [
    path("admin-dashboard/", views.school_admin_dashboard, name="admin_dashboard_url"),
    path("example/", views.user_search)
]