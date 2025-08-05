from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Sum, Count, F
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.http import HttpResponse
import csv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from io import BytesIO
import json

from .models import Product, Category, Sale, SaleItem, StockMovement, UserProfile
from .forms import CustomUserCreationForm, ProductForm, CategoryForm, StockAdjustmentForm, SaleFilterForm, SaleEditForm


def is_admin(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'admin'


def is_cashier(user):
    return hasattr(user, 'userprofile') and user.userprofile.role == 'cashier'


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard_view(request):
    user_profile = request.user.userprofile

    if user_profile.role == 'admin':
        # Admin Dashboard
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)

        context = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'low_stock_products': Product.objects.filter(is_active=True,
                                                         stock_quantity__lte=F('min_stock_level')).count(),
            'total_sales_today': Sale.objects.filter(created_at__date=today).aggregate(total=Sum('final_amount'))[
                                     'total'] or 0,
            'total_sales_week':
                Sale.objects.filter(created_at__date__gte=week_ago).aggregate(total=Sum('final_amount'))['total'] or 0,
            'recent_sales': Sale.objects.all()[:5],
            'low_stock_items': Product.objects.filter(is_active=True, stock_quantity__lte=F('min_stock_level'))[
                               :5],
        }
        return render(request, 'admin/dashboard.html', context)
    else:
        # Cashier Dashboard - POS Interface
        categories = Category.objects.filter(is_active=True)
        products = Product.objects.filter(is_active=True, stock_quantity__gt=0)

        # Handle search and filter
        search_query = request.GET.get('search', '')
        category_filter = request.GET.get('category', '')

        if search_query:
            products = products.filter(Q(name__icontains=search_query) | Q(barcode__icontains=search_query))

        if category_filter:
            products = products.filter(category_id=category_filter)

        context = {
            'categories': categories,
            'products': products,
            'search_query': search_query,
            'category_filter': category_filter,
        }
        return render(request, 'cashier/pos.html', context)


# Admin Views
@login_required
def product_list_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    products = Product.objects.all().order_by('-created_at')
    search_query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')

    if search_query:
        products = products.filter(Q(name__icontains=search_query) | Q(barcode__icontains=search_query))

    if category_filter:
        products = products.filter(category_id=category_filter)

    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.filter(is_active=True),
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'admin/product_list.html', context)


@login_required
def product_create_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product created successfully!')
            return redirect('product_list')
    else:
        form = ProductForm()

    return render(request, 'admin/product_form.html', {'form': form, 'title': 'Add Product'})


@login_required
def product_edit_view(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)

    return render(request, 'admin/product_form.html', {'form': form, 'title': 'Edit Product', 'product': product})


@login_required
def category_list_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    categories = Category.objects.all().order_by('-created_at')
    paginator = Paginator(categories, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/category_list.html', {'page_obj': page_obj})


@login_required
def category_create_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()

    return render(request, 'admin/category_form.html', {'form': form, 'title': 'Add Category'})


@login_required
def category_edit_view(request, pk):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'admin/category_form.html', {'form': form, 'title': 'Edit Category', 'category': category})


@login_required
def sale_detail_view(request, sale_id):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    sale = get_object_or_404(Sale, id=sale_id)
    sale_items = sale.saleitem_set.all()

    context = {
        'sale': sale,
        'sale_items': sale_items,
    }

    return render(request, 'admin/sale_detail.html', context)


@login_required
def sales_report_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    form = SaleFilterForm(request.GET)
    sales = Sale.objects.all().order_by('-created_at')

    if form.is_valid():
        if form.cleaned_data['start_date']:
            sales = sales.filter(created_at__date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            sales = sales.filter(created_at__date__lte=form.cleaned_data['end_date'])
        if form.cleaned_data['cashier']:
            sales = sales.filter(cashier=form.cleaned_data['cashier'])
        if form.cleaned_data['payment_method']:
            sales = sales.filter(payment_method=form.cleaned_data['payment_method'])

    # Summary statistics
    total_sales = sales.aggregate(
        total_amount=Sum('final_amount'),
        total_count=Count('id')
    )

    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'total_sales': total_sales,
    }
    return render(request, 'admin/sales_report.html', context)


@login_required
def sale_edit_view(request, sale_id):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    sale = get_object_or_404(Sale, id=sale_id)

    if request.method == 'POST':
        form = SaleEditForm(request.POST, instance=sale)
        if form.is_valid():
            sale = form.save(commit=False)

            # Recalculate final amount
            sale.final_amount = sale.total_amount - sale.discount_amount + sale.tax_amount
            sale.save()

            messages.success(request, 'Sale updated successfully!')
            return redirect('sale_detail', sale_id=sale.id)
    else:
        form = SaleEditForm(instance=sale)

    context = {
        'form': form,
        'sale': sale,
        'sale_items': sale.saleitem_set.all(),
    }

    return render(request, 'admin/sale_edit.html', context)


@login_required
def stock_management_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            stock_movement = form.save(commit=False)
            stock_movement.created_by = request.user
            stock_movement.save()

            # Update product stock
            product = stock_movement.product
            if stock_movement.movement_type == 'in':
                product.stock_quantity += stock_movement.quantity
            elif stock_movement.movement_type == 'out':
                product.stock_quantity -= stock_movement.quantity
            else:  # adjustment
                product.stock_quantity = stock_movement.quantity

            product.save()
            messages.success(request, 'Stock updated successfully!')
            return redirect('stock_management')
    else:
        form = StockAdjustmentForm()

    # Recent stock movements
    movements = StockMovement.objects.all().order_by('-created_at')[:20]
    low_stock_products = Product.objects.filter(
        is_active=True,
        stock_quantity__lte=F('min_stock_level')
    )

    context = {
        'form': form,
        'movements': movements,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'admin/stock_management.html', context)


@login_required
def user_management_view(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    users = User.objects.filter(userprofile__isnull=False).order_by('-date_joined')
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'admin/user_management.html', {'page_obj': page_obj})


# Cashier Views
@login_required
def pos_interface_view(request):
    if not is_cashier(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    return redirect('dashboard')  # Dashboard handles POS interface for cashiers


@login_required
def get_product_details(request, pk):
    if not is_cashier(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)

    try:
        product = Product.objects.get(pk=pk, is_active=True)
        return JsonResponse({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'stock_quantity': product.stock_quantity,
            'image_url': product.image_url,
        })
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)


@login_required
def process_sale(request):
    if not is_cashier(request.user):
        return JsonResponse({'error': 'Access denied'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            items = data.get('items', [])
            customer_name = data.get('customer_name', '')
            customer_phone = data.get('customer_phone', '')
            payment_method = data.get('payment_method', 'cash')
            discount_amount = Decimal(str(data.get('discount_amount', 0)))

            if not items:
                return JsonResponse({'error': 'No items in cart'}, status=400)

            # Calculate totals
            total_amount = Decimal('0')
            sale_items = []

            for item in items:
                product = Product.objects.get(id=item['product_id'], is_active=True)
                quantity = int(item['quantity'])

                if product.stock_quantity < quantity:
                    return JsonResponse({'error': f'Insufficient stock for {product.name}'}, status=400)

                unit_price = product.price
                total_price = quantity * unit_price
                total_amount += total_price

                sale_items.append({
                    'product': product,
                    'quantity': quantity,
                    'unit_price': unit_price,
                    'total_price': total_price,
                })

            # Apply discount and calculate final amount
            tax_amount = Decimal('0')  # You can implement tax calculation here
            final_amount = total_amount - discount_amount + tax_amount

            # Create sale
            sale = Sale.objects.create(
                cashier=request.user,
                total_amount=total_amount,
                discount_amount=discount_amount,
                tax_amount=tax_amount,
                final_amount=final_amount,
                payment_method=payment_method,
                customer_name=customer_name,
                customer_phone=customer_phone,
            )

            # Create sale items and update stock
            for item_data in sale_items:
                SaleItem.objects.create(
                    sale=sale,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    unit_price=item_data['unit_price'],
                    total_price=item_data['total_price'],
                )

                # Update stock
                product = item_data['product']
                product.stock_quantity -= item_data['quantity']
                product.save()

                # Create stock movement
                StockMovement.objects.create(
                    product=product,
                    movement_type='out',
                    quantity=item_data['quantity'],
                    reference_type='sale',
                    reference_id=sale.id,
                    notes=f'Sale - Invoice #{sale.invoice_number}',
                    created_by=request.user,
                )

            return JsonResponse({
                'success': True,
                'invoice_number': sale.invoice_number,
                'final_amount': str(sale.final_amount),
                'sale_id': sale.id,
            })

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def sale_receipt_view(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)

    # Check permissions
    if not (is_admin(request.user) or (is_cashier(request.user) and sale.cashier == request.user)):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    return render(request, 'receipt.html', {'sale': sale})


@login_required
def my_sales_view(request):
    if not is_cashier(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    sales = Sale.objects.filter(cashier=request.user).order_by('-created_at')
    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'cashier/my_sales.html', {'page_obj': page_obj})


@login_required
def export_sales_csv(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice #', 'Date', 'Cashier', 'Customer', 'Payment Method',
                     'Total Amount', 'Discount', 'Tax', 'Final Amount'])

    # Get filtered sales based on the same filters as in sales_report_view
    sales = Sale.objects.all().order_by('-created_at')
    form = SaleFilterForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['start_date']:
            sales = sales.filter(created_at__date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            sales = sales.filter(created_at__date__lte=form.cleaned_data['end_date'])
        if form.cleaned_data['cashier']:
            sales = sales.filter(cashier=form.cleaned_data['cashier'])
        if form.cleaned_data['payment_method']:
            sales = sales.filter(payment_method=form.cleaned_data['payment_method'])

    for sale in sales:
        writer.writerow([
            sale.invoice_number,
            sale.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            sale.cashier.get_full_name() or sale.cashier.username,
            sale.customer_name,
            sale.payment_method,
            sale.total_amount,
            sale.discount_amount,
            sale.tax_amount,
            sale.final_amount,
        ])

    return response


@login_required
def export_sales_pdf(request):
    if not is_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')

    # Create a file-like buffer to receive PDF data
    buffer = BytesIO()

    # Create the PDF object, using the buffer as its "file."
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))

    # Container for the 'Flowable' objects
    elements = []

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']

    # Add title
    elements.append(Paragraph("Sales Report", title_style))
    elements.append(Paragraph("<br/><br/>", styles['Normal']))

    # Get filtered sales based on the same filters as in sales_report_view
    sales = Sale.objects.all().order_by('-created_at')
    form = SaleFilterForm(request.GET)

    if form.is_valid():
        if form.cleaned_data['start_date']:
            sales = sales.filter(created_at__date__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            sales = sales.filter(created_at__date__lte=form.cleaned_data['end_date'])
        if form.cleaned_data['cashier']:
            sales = sales.filter(cashier=form.cleaned_data['cashier'])
        if form.cleaned_data['payment_method']:
            sales = sales.filter(payment_method=form.cleaned_data['payment_method'])

    # Table data
    data = [['Invoice #', 'Date', 'Cashier', 'Customer', 'Payment Method',
             'Total Amount', 'Discount', 'Tax', 'Final Amount']]

    for sale in sales:
        data.append([
            sale.invoice_number,
            sale.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            sale.cashier.get_full_name() or sale.cashier.username,
            sale.customer_name,
            sale.payment_method,
            f"{sale.total_amount:.2f}",
            f"{sale.discount_amount:.2f}",
            f"{sale.tax_amount:.2f}",
            f"{sale.final_amount:.2f}",
        ])

    # Calculate totals
    totals = sales.aggregate(
        total=Sum('total_amount'),
        discount=Sum('discount_amount'),
        tax=Sum('tax_amount'),
        final=Sum('final_amount')
    )

    # Add totals row
    data.append([
        'TOTAL', '', '', '', '',
        f"{totals['total'] or 0:.2f}",
        f"{totals['discount'] or 0:.2f}",
        f"{totals['tax'] or 0:.2f}",
        f"{totals['final'] or 0:.2f}",
    ])

    # Create the table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.black),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 2, colors.black),
    ]))

    elements.append(table)

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and write it to the response
    pdf = buffer.getvalue()
    buffer.close()

    # Create the HTTP response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    response.write(pdf)

    return response
