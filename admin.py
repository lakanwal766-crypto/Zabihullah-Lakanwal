from django.contrib import admin
from .models import Medicine, Supplier, Sale, SaleItem

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "strength", "form", "batch_number", "expiry_date", "stock", "sale_price")
    search_fields = ("name", "generic_name", "batch_number")
    list_filter = ("form", "expiry_date")
@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "phone")
    search_fields = ("name", "phone")
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "total")
    inlines = [SaleItemInline]
admin.site.register(Sale, SaleAdmin)
