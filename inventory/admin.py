from django.contrib import admin
from .models import Medicine, Sale, SaleItem


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ("name", "sku", "category", "generic_name", "weight", "manufacturer", "batch_number", "expiry_date", "quantity_in_stock", "unit_price")
    search_fields = ("name", "sku", "category", "generic_name", "weight", "manufacturer", "batch_number")
    list_filter = ("expiry_date", "category")


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "created_at", "customer_name", "total_amount")
    inlines = [SaleItemInline]

# Register your models here.
