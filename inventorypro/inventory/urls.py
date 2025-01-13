from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/add/', views.add_supplier, name='add_supplier'),
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.create_sale_order, name='create_sale'),
    path('sales/<int:pk>/cancel/', views.cancel_sale, name='cancel_sale'),
    path('sales/<int:pk>/complete/', views.complete_sale, name='complete_sale'),
    path('stock/movement/', views.add_stock_movement, name='add_stock_movement'),
    path('stock/check/', views.stock_level_check, name='stock_level_check'),
]