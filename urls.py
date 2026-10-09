from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from pharmacy import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(template_name="pharmacy/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("medicines/", views.medicines, name="medicines"),
    path("medicines/add/", views.medicine_add, name="medicine_add"),
    path("suppliers/", views.suppliers, name="suppliers"),
    path("suppliers/add/", views.supplier_add, name="supplier_add"),
    path("sales/", views.sales, name="sales"),
    path("sales/add/", views.sale_add, name="sale_add"),
    path("reports/", views.reports, name="reports"),
]
