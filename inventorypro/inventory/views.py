# inventory/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Product, Supplier, SaleOrder, StockMovement
from .forms import ProductForm, SupplierForm, SaleOrderForm, StockMovementForm
from django.db.models import Sum
from django.contrib.auth.decorators import login_required


@login_required
def dashboard(request):
    context = {
        'total_products': Product.objects.count(),
        'total_suppliers': Supplier.objects.count(),
        'total_sales': SaleOrder.objects.filter(status='COMPLETED').count(),
        'low_stock_products': Product.objects.filter(stock_quantity__lte=10)
    }
    return render(request, 'inventory/dashboard.html', context)

@login_required
def cancel_sale(request, pk):
    sale_order = get_object_or_404(SaleOrder, pk=pk)
    if sale_order.status == 'PENDING':
        sale_order.status = 'CANCELLED'
        sale_order.save()
        
        # Restore stock
        product = sale_order.product
        product.stock_quantity += sale_order.quantity
        product.save()
        
        # Record stock movement
        StockMovement.objects.create(
            product=product,
            quantity=sale_order.quantity,
            movement_type='IN',
            notes=f'Cancelled sale order #{sale_order.id}'
        )
        
        messages.success(request, 'Sale order cancelled successfully!')
    else:
        messages.error(request, 'Cannot cancel this sale order!')
    return redirect('sale_list')

@login_required
def complete_sale(request, pk):
    sale_order = get_object_or_404(SaleOrder, pk=pk)
    if sale_order.status == 'PENDING':
        sale_order.status = 'COMPLETED'
        sale_order.save()
        messages.success(request, 'Sale order completed successfully!')
    else:
        messages.error(request, 'Cannot complete this sale order!')
    return redirect('sale_list')

@login_required
def stock_level_check(request):
    products = Product.objects.all().annotate(
        total_in=Sum('stockmovement__quantity',
                    filter=models.Q(stockmovement__movement_type='IN')),
        total_out=Sum('stockmovement__quantity',
                     filter=models.Q(stockmovement__movement_type='OUT'))
    )
    return render(request, 'inventory/stock_check.html', {'products': products})

@login_required
def add_stock_movement(request):
    if request.method == 'POST':
        form = StockMovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            product = movement.product
            
            if movement.movement_type == 'IN':
                product.stock_quantity += movement.quantity
            else:
                if product.stock_quantity >= movement.quantity:
                    product.stock_quantity -= movement.quantity
                else:
                    messages.error(request, 'Insufficient stock!')
                    return redirect('add_stock_movement')
            
            product.save()
            movement.save()
            messages.success(request, 'Stock movement recorded successfully!')
            return redirect('product_list')
    else:
        form = StockMovementForm()
    return render(request, 'inventory/stock_movement_form.html', {'form': form})

def product_list(request):
    products = Product.objects.all()
    return render(request, 'inventory/product_list.html', {'products': products})

def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product added successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'inventory/product_form.html', {'form': form})

def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, 'inventory/supplier_list.html', {'suppliers': suppliers})

def add_supplier(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier added successfully!')
            return redirect('supplier_list')
    else:
        form = SupplierForm()
    return render(request, 'inventory/supplier_form.html', {'form': form})

def create_sale_order(request):
    if request.method == 'POST':
        form = SaleOrderForm(request.POST)
        if form.is_valid():
            sale_order = form.save(commit=False)
            product = sale_order.product
            
            if product.stock_quantity >= sale_order.quantity:
                sale_order.total_price = product.price * sale_order.quantity
                sale_order.save()
                
                # Update stock
                product.stock_quantity -= sale_order.quantity
                product.save()
                
                # Create stock movement
                StockMovement.objects.create(
                    product=product,
                    quantity=sale_order.quantity,
                    movement_type='OUT',
                    notes=f'Sale order #{sale_order.id}'
                )
                
                messages.success(request, 'Sale order created successfully!')
                return redirect('sale_list')
            else:
                messages.error(request, 'Insufficient stock!')
    else:
        form = SaleOrderForm()
    return render(request, 'inventory/sale_form.html', {'form': form})