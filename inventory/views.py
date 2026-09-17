from decimal import Decimal
from django.db.models import Q
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from datetime import date

from .models import Medicine, Sale, SaleItem, CartItem


def staff_required(user):
    return user.is_authenticated and user.is_staff


def login_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        if not request.user.is_staff:
            messages.error(request, "Only admin/staff users can access this system.")
            return redirect('login')
        return redirect('medicine_list')

    form = AuthenticationForm(request, data=request.POST or None)
    # Add Bootstrap classes to form fields
    form.fields['username'].widget.attrs.update({"class": "form-control"})
    form.fields['password'].widget.attrs.update({"class": "form-control"})
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if not user.is_staff:
            messages.error(request, "Only admin/staff users can login.")
        else:
            login(request, user)
            return redirect('medicine_list')
    return render(request, 'auth/login.html', {'form': form})


def register_view(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        return redirect('medicine_list')

    class StaffUserCreationForm(UserCreationForm):
        def save(self, commit=True):
            user = super().save(commit=False)
            user.is_staff = True
            if commit:
                user.save()
            return user

    if request.method == 'POST':
        form = StaffUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful. You are now logged in.')
                return redirect('medicine_list')
            except Exception as e:
                messages.error(request, f'Registration error: {str(e)}')
    else:
        form = StaffUserCreationForm()
        
    # Add Bootstrap classes to form fields
    for field_name in ['username', 'password1', 'password2']:
        if field_name in form.fields:
            form.fields[field_name].widget.attrs.update({"class": "form-control"})
            
    return render(request, 'auth/register.html', {'form': form})


@login_required
@user_passes_test(staff_required)
def medicine_list(request: HttpRequest) -> HttpResponse:
    q = request.GET.get('q', '').strip()
    medicines = Medicine.objects.all()
    if q:
        medicines = medicines.filter(
            Q(name__icontains=q)
            | Q(generic_name__icontains=q)
            | Q(manufacturer__icontains=q)
            | Q(weight__icontains=q)
            | Q(batch_number__icontains=q)
            | Q(sku__icontains=q)
            | Q(category__icontains=q)
        )
    paginator = Paginator(medicines, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'inventory/medicine_list.html', {'medicines': page_obj, 'q': q, 'page_obj': page_obj})


@login_required
@user_passes_test(staff_required)
def medicine_add(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        manufacturer = request.POST.get('manufacturer', '').strip()
        generic_name = request.POST.get('generic_name', '').strip()
        weight = request.POST.get('weight', '').strip()
        indications = request.POST.get('indications', '').strip()
        batch_number = request.POST.get('batch_number', '').strip()
        expiry_str = request.POST.get('expiry_date') or None
        expiry_date = None
        if expiry_str:
            try:
                expiry_date = date.fromisoformat(expiry_str)
            except ValueError:
                messages.error(request, 'Invalid expiry date format. Use YYYY-MM-DD.')
        quantity_in_stock = int(request.POST.get('quantity_in_stock') or 0)
        unit_price = Decimal(request.POST.get('unit_price') or '0')

        if not name:
            messages.error(request, 'Name is required.')
        else:
            Medicine.objects.create(
                name=name,
                manufacturer=manufacturer,
                generic_name=generic_name,
                weight=weight,
                indications=indications,
                batch_number=batch_number,
                expiry_date=expiry_date,
                quantity_in_stock=quantity_in_stock,
                unit_price=unit_price,
            )
            messages.success(request, 'Medicine added successfully.')
            return redirect('medicine_list')
    return render(request, 'inventory/medicine_add.html')


@login_required
@user_passes_test(staff_required)
def cart_add(request: HttpRequest, pk: int) -> HttpResponse:
    # Persist cart item in DB for current user
    medicine = get_object_or_404(Medicine, pk=pk)
    item, _ = CartItem.objects.get_or_create(user=request.user, medicine=medicine)
    item.quantity = item.quantity + 1
    item.save()
    # stay on the same page
    referer = request.META.get('HTTP_REFERER') or reverse('medicine_list')
    return redirect(referer)


@login_required
@user_passes_test(staff_required)
def cart_clear(request: HttpRequest) -> HttpResponse:
    # Clear persistent cart for this user
    CartItem.objects.filter(user=request.user).delete()
    referer = request.META.get('HTTP_REFERER') or reverse('cart')
    return redirect(referer)


@login_required
@user_passes_test(staff_required)
def cart_remove(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        med_id = request.POST.get('id')
        if med_id:
            CartItem.objects.filter(user=request.user, medicine_id=int(med_id)).delete()
    referer = request.META.get('HTTP_REFERER') or reverse('cart')
    return redirect(referer)


@login_required
@user_passes_test(staff_required)
def medicine_delete(request: HttpRequest, pk: int) -> HttpResponse:
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        try:
            medicine.delete()
            messages.success(request, 'Medicine deleted.')
        except ProtectedError:
            messages.error(request, 'Cannot delete this medicine because it is referenced by previous sales.')
        return redirect('medicine_list')
    return render(request, 'inventory/medicine_confirm_delete.html', {'medicine': medicine})


@login_required
@user_passes_test(staff_required)
def medicine_edit(request: HttpRequest, pk: int) -> HttpResponse:
    medicine = get_object_or_404(Medicine, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        manufacturer = request.POST.get('manufacturer', '').strip()
        generic_name = request.POST.get('generic_name', '').strip()
        weight = request.POST.get('weight', '').strip()
        indications = request.POST.get('indications', '').strip()
        batch_number = request.POST.get('batch_number', '').strip()
        expiry_str = request.POST.get('expiry_date') or None
        expiry_date = None
        if expiry_str:
            try:
                expiry_date = date.fromisoformat(expiry_str)
            except ValueError:
                messages.error(request, 'Invalid expiry date format. Use YYYY-MM-DD.')
        quantity_in_stock = int(request.POST.get('quantity_in_stock') or 0)
        unit_price = Decimal(request.POST.get('unit_price') or '0')

        if not name:
            messages.error(request, 'Name is required.')
        else:
            medicine.name = name
            medicine.manufacturer = manufacturer
            medicine.generic_name = generic_name
            medicine.weight = weight
            medicine.indications = indications
            medicine.batch_number = batch_number
            medicine.expiry_date = expiry_date
            medicine.quantity_in_stock = quantity_in_stock
            medicine.unit_price = unit_price
            if 'image' in request.FILES:
                medicine.image = request.FILES['image']
            medicine.save()
            messages.success(request, 'Medicine updated successfully.')
            return redirect('medicine_list')
    return render(request, 'inventory/medicine_edit.html', {"medicine": medicine})


@login_required
@user_passes_test(staff_required)
def sell_view(request: HttpRequest) -> HttpResponse:
    medicines = Medicine.objects.all()
    # Load persistent cart for this user
    cart_qs = CartItem.objects.filter(user=request.user).select_related('medicine')
    session_cart = {str(ci.medicine_id): ci.quantity for ci in cart_qs}
    cart_items = [(ci.medicine, ci.quantity) for ci in cart_qs]
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name', '').strip()
        # Parse items via management count item-TOTAL_FORMS
        items = []
        total_forms = int(request.POST.get('item-TOTAL_FORMS') or 0)
        total = Decimal('0')
        errors = []
        for index in range(total_forms):
            med_id = request.POST.get(f'item-{index}-medicine')
            qty = request.POST.get(f'item-{index}-qty')
            if not med_id and not qty:
                continue
            try:
                medicine = Medicine.objects.get(pk=int(med_id))
                quantity = int(qty)
                if quantity <= 0:
                    raise ValueError('Quantity must be positive')
                if medicine.quantity_in_stock < quantity:
                    errors.append(f'Not enough stock for {medicine.name}.')
                price = medicine.unit_price
                line_total = price * quantity
                items.append((medicine, quantity, price, line_total))
                total += line_total
            except Exception:
                errors.append(f'Invalid item at row {index + 1}.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'inventory/sell.html', {"medicines": medicines})
        if not items:
            messages.error(request, 'Add at least one item to sell.')
            return render(request, 'inventory/sell.html', {"medicines": medicines})

        with transaction.atomic():
            sale = Sale.objects.create(created_by=request.user, customer_name=customer_name, total_amount=total)
            for medicine, quantity, price, line_total in items:
                SaleItem.objects.create(
                    sale=sale,
                    medicine=medicine,
                    quantity=quantity,
                    unit_price=price,
                    line_total=line_total,
                )
                medicine.quantity_in_stock -= quantity
                medicine.save(update_fields=["quantity_in_stock"])
            # Clear persistent cart after sale
            CartItem.objects.filter(user=request.user).delete()
        return redirect('receipt', pk=sale.pk)

    return render(request, 'inventory/sell.html', {"medicines": medicines, "session_cart": session_cart, "cart_items": cart_items})


@login_required
@user_passes_test(staff_required)
def receipt_view(request: HttpRequest, pk: int) -> HttpResponse:
    sale = get_object_or_404(Sale.objects.select_related('created_by').prefetch_related('items__medicine'), pk=pk)
    return render(request, 'inventory/receipt.html', {"sale": sale})

@login_required
@user_passes_test(staff_required)
def sales_history(request: HttpRequest) -> HttpResponse:
    sales = (Sale.objects
             .select_related('created_by')
             .prefetch_related('items__medicine')
             .order_by('-created_at'))
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')
    customer = request.GET.get('customer', '').strip()
    if from_date:
        sales = sales.filter(created_at__date__gte=from_date)
    if to_date:
        sales = sales.filter(created_at__date__lte=to_date)
    if customer:
        sales = sales.filter(customer_name__icontains=customer)
    return render(request, 'inventory/sales_history.html', {"sales": sales})

# Create your views here.
