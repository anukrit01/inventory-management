# inventory/forms.py

from django import forms
from .models import Product, Supplier, SaleOrder, StockMovement

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock_quantity', 'supplier']

class SupplierForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'address']

class SaleOrderForm(forms.ModelForm):
    class Meta:
        model = SaleOrder
        fields = ['product', 'quantity']

class StockMovementForm(forms.ModelForm):
    class Meta:
        model = StockMovement
        fields = ['product', 'quantity', 'movement_type', 'notes']