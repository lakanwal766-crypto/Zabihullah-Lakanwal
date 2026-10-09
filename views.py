from datetime import date, timedelta
from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Medicine, Supplier, Sale, SaleItem

@login_required
def dashboard(request):
    today = timezone.localdate()
    sales_today = Sale.objects.filter(created_at__date=today).aggregate(total=Sum("total"))["total"] or Decimal("0")
    low_stock = Medicine.objects.filter(stock__lte=F("low_stock_threshold")).order_by("stock")[:8]
    expiring = Medicine.objects.filter(expiry_date__isnull=False, expiry_date__lte=today + timedelta(days=90), expiry_date__gte=today).order_by("expiry_date")[:8]
    expired = Medicine.objects.filter(expiry_date__lt=today).order_by("expiry_date")[:8]
    return render(request, "pharmacy/dashboard.html", {
        "medicine_count": Medicine.objects.count(), "sales_today": sales_today,
        "low_stock": low_stock, "expiring": expiring, "expired": expired,
    })

@login_required
def medicines(request):
    q = request.GET.get("q", "").strip()
    items = Medicine.objects.select_related("supplier")
    if q: items = items.filter(name__icontains=q) | items.filter(generic_name__icontains=q) | items.filter(batch_number__icontains=q)
    return render(request, "pharmacy/medicines.html", {"items": items, "q": q})

@login_required
def medicine_add(request):
    suppliers = Supplier.objects.all()
    if request.method == "POST":
        try:
            expiry = request.POST.get("expiry_date") or None
            supplier_id = request.POST.get("supplier") or None
            Medicine.objects.create(
                name=request.POST["name"].strip(), generic_name=request.POST.get("generic_name","").strip(),
                strength=request.POST.get("strength","").strip(), form=request.POST.get("form","").strip(),
                batch_number=request.POST.get("batch_number","").strip(), expiry_date=expiry,
                purchase_price=request.POST.get("purchase_price") or 0, sale_price=request.POST.get("sale_price") or 0,
                stock=int(request.POST.get("stock") or 0), low_stock_threshold=int(request.POST.get("low_stock_threshold") or 10),
                supplier_id=supplier_id)
            messages.success(request, "درمل په بریالیتوب ثبت شو.")
            return redirect("medicines")
        except (ValueError, KeyError):
            messages.error(request, "مهرباني وکړئ ټول اړین معلومات سم ولیکئ.")
    return render(request, "pharmacy/medicine_form.html", {"suppliers": suppliers})

@login_required
def suppliers(request):
    return render(request, "pharmacy/suppliers.html", {"items": Supplier.objects.all()})

@login_required
def supplier_add(request):
    if request.method == "POST":
        name = request.POST.get("name","").strip()
        if name:
            Supplier.objects.create(name=name, phone=request.POST.get("phone","").strip(), address=request.POST.get("address","").strip(), notes=request.POST.get("notes","").strip())
            messages.success(request, "عرضه کوونکی ثبت شو.")
            return redirect("suppliers")
        messages.error(request, "د عرضه کوونکي نوم اړین دی.")
    return render(request, "pharmacy/supplier_form.html")

@login_required
def sales(request):
    items = Sale.objects.prefetch_related("items__medicine").order_by("-created_at")[:100]
    return render(request, "pharmacy/sales.html", {"items": items, "medicines": Medicine.objects.filter(stock__gt=0).order_by("name")})

@login_required
@transaction.atomic
def sale_add(request):
    if request.method != "POST": return redirect("sales")
    try:
        medicine = Medicine.objects.select_for_update().get(pk=int(request.POST["medicine"]))
        quantity = int(request.POST["quantity"])
        if quantity < 1: raise ValueError
        if medicine.stock < quantity:
            messages.error(request, f"د {medicine.name} موجود مقدار کافي نه دی.")
            return redirect("sales")
        sale = Sale.objects.create()
        SaleItem.objects.create(sale=sale, medicine=medicine, quantity=quantity, unit_price=medicine.sale_price)
        sale.total = medicine.sale_price * quantity
        sale.save(update_fields=["total"])
        medicine.stock -= quantity
        medicine.save(update_fields=["stock"])
        messages.success(request, f"خرڅلاو ثبت شو. رسید #{sale.pk} — ټول مبلغ: {sale.total}")
    except (ValueError, KeyError, Medicine.DoesNotExist):
        messages.error(request, "مهرباني وکړئ درمل او مقدار سم وټاکئ.")
    return redirect("sales")

@login_required
def reports(request):
    today = timezone.localdate()
    month_start = today.replace(day=1)
    today_total = Sale.objects.filter(created_at__date=today).aggregate(s=Sum("total"))["s"] or Decimal("0")
    month_total = Sale.objects.filter(created_at__date__gte=month_start).aggregate(s=Sum("total"))["s"] or Decimal("0")
    estimated_profit = SaleItem.objects.filter(sale__created_at__date__gte=month_start).aggregate(
        p=Sum((F("unit_price") - F("medicine__purchase_price")) * F("quantity"))
    )["p"] or Decimal("0")
    return render(request, "pharmacy/reports.html", {"today_total": today_total, "month_total": month_total, "estimated_profit": estimated_profit})
