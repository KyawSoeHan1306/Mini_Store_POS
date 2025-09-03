from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Authentication
    path('', views.dashboard_view, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path("profile/", views.profile, name="profile"),
    path("change-password/", views.change_password, name="change_password"),

    # Admin URLs
    path('products/', views.product_list_view, name='product_list'),
    path('products/add/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),

    path('categories/', views.category_list_view, name='category_list'),
    path('categories/add/', views.category_create_view, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit_view, name='category_edit'),

    path('sales-report/', views.sales_report_view, name='sales_report'),
    path('export-sales-csv/', views.export_sales_csv, name='export_sales_csv'),
    path('export-sales-pdf/', views.export_sales_pdf, name='export_sales_pdf'),
    path('sale/<int:sale_id>/', views.sale_detail_view, name='sale_detail'),
    path('sale/<int:sale_id>/edit/', views.sale_edit_view, name='sale_edit'),
    path('stock-management/', views.stock_management_view, name='stock_management'),
    path('user-management/', views.user_management_view, name='user_management'),

    # Cashier URLs
    path('pos/', views.pos_interface_view, name='pos_interface'),
    path('complete-sale/', views.complete_sale, name='complete_sale'),
    path('api/product/<int:pk>/', views.get_product_details, name='get_product_details'),
    path('api/process-sale/', views.process_sale, name='process_sale'),
    path('receipt/<int:sale_id>/', views.sale_receipt_view, name='sale_receipt'),
    path('my-sales/', views.my_sales_view, name='my_sales'),
]
