from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal

class Supplier(models.Model):
    name = models.CharField("د عرضه کوونکي نوم", max_length=160)
    phone = models.CharField("د اړیکې شمېره", max_length=40, blank=True)
    address = models.CharField("پته", max_length=250, blank=True)
    notes = models.TextField("یادښت", blank=True)
    def __str__(self): return self.name
    class Meta: ordering = ["name"]

class Medicine(models.Model):
    name = models.CharField("د درمل نوم", max_length=180)
    generic_name = models.CharField("جنریک نوم", max_length=180, blank=True)
    strength = models.CharField("قوت", max_length=80, blank=True, help_text="لکه 500 mg")
    form = models.CharField("ډول", max_length=80, blank=True, help_text="Tablet, Capsule, Syrup...")
    batch_number = models.CharField("Batch نمبر", max_length=100, blank=True)
    expiry_date = models.DateField("د ختمېدو نېټه", null=True, blank=True)
    purchase_price = models.DecimalField("د پېرلو قیمت", max_digits=12, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(0)])
    sale_price = models.DecimalField("د خرڅلاو قیمت", max_digits=12, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField("موجود مقدار", default=0)
    low_stock_threshold = models.PositiveIntegerField("د کم سټاک حد", default=10)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="عرضه کوونکی")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.name} ({self.strength})"
    class Meta: ordering = ["name"]

class Sale(models.Model):
    created_at = models.DateTimeField("د خرڅلاو وخت", auto_now_add=True)
    total = models.DecimalField("ټول مبلغ", max_digits=12, decimal_places=2, default=Decimal("0"))
    note = models.CharField("یادښت", max_length=250, blank=True)
    def __str__(self): return f"رسید #{self.pk} — {self.total}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    medicine = models.ForeignKey(Medicine, on_delete=models.PROTECT, verbose_name="درمل")
    quantity = models.PositiveIntegerField("مقدار", validators=[MinValueValidator(1)])
    unit_price = models.DecimalField("د یوې دانې قیمت", max_digits=12, decimal_places=2)
    @property
    def line_total(self): return self.quantity * self.unit_price
