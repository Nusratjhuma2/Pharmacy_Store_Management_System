from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone


class Medicine(models.Model):
    name = models.CharField(max_length=255, unique=True)
    sku = models.CharField(max_length=64, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    generic_name = models.CharField(max_length=255, blank=True)
    weight = models.CharField(max_length=100, blank=True, help_text="e.g., 10 mg/ml")
    indications = models.TextField(blank=True)
    image = models.ImageField(upload_to='medicine_images/', blank=True, null=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    quantity_in_stock = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Sale(models.Model):
    created_by = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)
    created_at = models.DateTimeField(default=timezone.now)
    customer_name = models.CharField(max_length=255, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self) -> str:
        return f"Sale #{self.pk} - {self.created_at:%Y-%m-%d %H:%M}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.medicine} x {self.quantity}"


class CartItem(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='cart_items')
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'medicine')

    def __str__(self) -> str:
        return f"CartItem({self.user_id}, {self.medicine_id}) x {self.quantity}"

# Create your models here.
