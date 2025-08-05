from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import transaction
from decimal import Decimal
import random
from datetime import datetime, timedelta
from pos.models import UserProfile, Category, Product, Sale, SaleItem, StockMovement


class Command(BaseCommand):
    help = 'Create sample data for Mini Store POS'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        try:
            with transaction.atomic():
                # Create groups first
                self.create_groups()

                # Create users and profiles
                self.create_users()

                # Create categories
                self.create_categories()

                # Create products
                self.create_products()

                # Create sales
                self.create_sales()

                # Create stock movements
                self.create_stock_movements()

            self.stdout.write(
                self.style.SUCCESS('Sample data created successfully!')
            )
            self.stdout.write('')
            self.stdout.write('Login credentials:')
            self.stdout.write('Admin: username=admin, password=password123')
            self.stdout.write('Cashier: username=cashier1, password=password123')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating sample data: {str(e)}')
            )

    def create_groups(self):
        """Create user groups"""
        groups = ['Admin', 'Cashier']
        for group_name in groups:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f'Created group: {group_name}')

    def create_users(self):
        """Create sample users with profiles"""
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@ministore.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
                'groups': ['Admin'],
                'role': 'admin',
                'phone': '555-0001'
            },
            {
                'username': 'cashier1',
                'email': 'cashier1@ministore.com',
                'first_name': 'Alice',
                'last_name': 'Smith',
                'groups': ['Cashier'],
                'role': 'cashier',
                'phone': '555-0002'
            },
            {
                'username': 'cashier2',
                'email': 'cashier2@ministore.com',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'groups': ['Cashier'],
                'role': 'cashier',
                'phone': '555-0003'
            }
        ]

        for user_data in users_data:
            # Check if user already exists
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'is_staff': user_data.get('is_staff', False),
                    'is_superuser': user_data.get('is_superuser', False),
                }
            )

            if created:
                user.set_password('password123')  # Set default password
                user.save()
                self.stdout.write(f'Created user: {user.username}')
            else:
                self.stdout.write(f'User already exists: {user.username}')

            # Add user to groups
            for group_name in user_data['groups']:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)

            # Create or update UserProfile
            profile, profile_created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': user_data['role'],
                    'phone': user_data['phone']
                }
            )

            if profile_created:
                self.stdout.write(f'Created profile for: {user.username}')
            else:
                # Update existing profile
                profile.role = user_data['role']
                profile.phone = user_data['phone']
                profile.save()
                self.stdout.write(f'Updated profile for: {user.username}')

    def create_categories(self):
        """Create product categories"""
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and accessories'},
            {'name': 'Clothing', 'description': 'Apparel and fashion items'},
            {'name': 'Food & Beverages', 'description': 'Food items and drinks'},
            {'name': 'Books & Stationery', 'description': 'Books, notebooks, and office supplies'},
            {'name': 'Home & Garden', 'description': 'Household items and garden supplies'},
            {'name': 'Sports & Fitness', 'description': 'Sports equipment and fitness gear'},
            {'name': 'Health & Beauty', 'description': 'Health products and cosmetics'},
            {'name': 'Toys & Games', 'description': 'Toys and entertainment items'},
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created category: {cat_data["name"]}')

    def create_products(self):
        """Create sample products"""
        categories = list(Category.objects.all())

        if not categories:
            self.stdout.write('No categories found. Creating products without categories.')
            return

        products_data = [
            # Electronics
            {'name': 'Smartphone', 'category': 'Electronics', 'price': 25000.00, 'stock': 50},
            {'name': 'Laptop', 'category': 'Electronics', 'price': 45000.00, 'stock': 20},
            {'name': 'Bluetooth Headphones', 'category': 'Electronics', 'price': 2500.00, 'stock': 75},
            {'name': 'USB Cable', 'category': 'Electronics', 'price': 500.00, 'stock': 100},
            {'name': 'Power Bank', 'category': 'Electronics', 'price': 1500.00, 'stock': 60},

            # Clothing
            {'name': 'Cotton T-Shirt', 'category': 'Clothing', 'price': 800.00, 'stock': 80},
            {'name': 'Blue Jeans', 'category': 'Clothing', 'price': 1500.00, 'stock': 40},
            {'name': 'Running Shoes', 'category': 'Clothing', 'price': 3000.00, 'stock': 30},
            {'name': 'Baseball Cap', 'category': 'Clothing', 'price': 600.00, 'stock': 50},

            # Food & Beverages
            {'name': 'Premium Coffee Beans 1kg', 'category': 'Food & Beverages', 'price': 1200.00, 'stock': 25},
            {'name': 'Green Tea Box', 'category': 'Food & Beverages', 'price': 300.00, 'stock': 40},
            {'name': 'Dark Chocolate Bar', 'category': 'Food & Beverages', 'price': 150.00, 'stock': 120},
            {'name': 'Energy Drink', 'category': 'Food & Beverages', 'price': 80.00, 'stock': 200},

            # Books & Stationery
            {'name': 'Programming Handbook', 'category': 'Books & Stationery', 'price': 1800.00, 'stock': 15},
            {'name': 'Notebook Set', 'category': 'Books & Stationery', 'price': 400.00, 'stock': 60},
            {'name': 'Ballpoint Pens (Pack of 10)', 'category': 'Books & Stationery', 'price': 200.00, 'stock': 80},

            # Home & Garden
            {'name': 'Ceramic Plant Pot', 'category': 'Home & Garden', 'price': 400.00, 'stock': 35},
            {'name': 'Kitchen Knife Set', 'category': 'Home & Garden', 'price': 1200.00, 'stock': 20},
            {'name': 'LED Table Lamp', 'category': 'Home & Garden', 'price': 800.00, 'stock': 25},

            # Sports & Fitness
            {'name': 'Tennis Ball Set', 'category': 'Sports & Fitness', 'price': 300.00, 'stock': 45},
            {'name': 'Yoga Mat', 'category': 'Sports & Fitness', 'price': 1500.00, 'stock': 30},
            {'name': 'Water Bottle', 'category': 'Sports & Fitness', 'price': 400.00, 'stock': 70},

            # Health & Beauty
            {'name': 'Face Cream', 'category': 'Health & Beauty', 'price': 800.00, 'stock': 40},
            {'name': 'Shampoo 500ml', 'category': 'Health & Beauty', 'price': 600.00, 'stock': 55},

            # Toys & Games
            {'name': 'Board Game', 'category': 'Toys & Games', 'price': 1200.00, 'stock': 20},
            {'name': 'Puzzle 1000 pieces', 'category': 'Toys & Games', 'price': 800.00, 'stock': 15},
        ]

        for product_data in products_data:
            try:
                category = next((cat for cat in categories if cat.name == product_data['category']), None)
                if not category:
                    category = random.choice(categories)

                # Generate unique barcode
                barcode = f"{random.randint(1000000000000, 9999999999999)}"

                product, created = Product.objects.get_or_create(
                    name=product_data['name'],
                    defaults={
                        'category': category,
                        'barcode': barcode,
                        'price': Decimal(str(product_data['price'])),
                        'stock_quantity': product_data['stock'],
                        'min_stock_level': random.randint(5, 15),
                        'description': f"High quality {product_data['name'].lower()}",
                        'is_active': True
                    }
                )

                if created:
                    self.stdout.write(f'Created product: {product_data["name"]} - ₹{product_data["price"]}')

            except Exception as e:
                self.stdout.write(f'Error creating product {product_data["name"]}: {str(e)}')

    def create_sales(self):
        """Create sample sales"""
        users = User.objects.filter(userprofile__role='cashier')
        if not users.exists():
            users = User.objects.all()

        products = Product.objects.filter(stock_quantity__gt=0)

        if not products.exists():
            self.stdout.write('No products with stock found. Skipping sales.')
            return

        payment_methods = ['cash', 'card', 'digital']
        customer_names = [
            'John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Wilson',
            'David Brown', 'Lisa Davis', 'Tom Anderson', 'Emma Taylor',
            '', '', ''  # Some empty names for walk-in customers
        ]

        for i in range(25):  # Create 25 sample sales
            try:
                cashier = random.choice(users)
                sale_date = datetime.now() - timedelta(days=random.randint(0, 30))
                customer_name = random.choice(customer_names)

                # Create the sale
                sale = Sale.objects.create(
                    cashier=cashier,
                    total_amount=Decimal('0'),  # Will be calculated
                    discount_amount=Decimal('0'),
                    tax_amount=Decimal('0'),
                    final_amount=Decimal('0'),  # Will be calculated
                    payment_method=random.choice(payment_methods),
                    customer_name=customer_name,
                    customer_phone=f'555-{random.randint(1000, 9999)}' if customer_name else '',
                    created_at=sale_date
                )

                # Add random products to sale
                sale_total = Decimal('0')
                available_products = list(products.filter(stock_quantity__gt=0))
                selected_products = random.sample(
                    available_products,
                    min(random.randint(1, 5), len(available_products))
                )

                for product in selected_products:
                    max_qty = min(product.stock_quantity, 10)
                    if max_qty <= 0:
                        continue

                    quantity = random.randint(1, max_qty)
                    unit_price = product.price
                    total_price = unit_price * quantity

                    # Create sale item
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price
                    )

                    sale_total += total_price

                    # Update product stock
                    product.stock_quantity -= quantity
                    product.save()

                # Calculate discount (random 0-10%)
                discount_percent = random.uniform(0, 0.1)
                discount_amount = sale_total * Decimal(str(discount_percent))

                # Calculate tax (5% GST)
                tax_amount = (sale_total - discount_amount) * Decimal('0.05')

                # Calculate final amount
                final_amount = sale_total - discount_amount + tax_amount

                # Update sale totals
                sale.total_amount = sale_total
                sale.discount_amount = discount_amount
                sale.tax_amount = tax_amount
                sale.final_amount = final_amount
                sale.save()

                self.stdout.write(f'Created sale: {sale.invoice_number} - ₹{final_amount:.2f}')

            except Exception as e:
                self.stdout.write(f'Error creating sale {i + 1}: {str(e)}')

        self.stdout.write(f'Created {Sale.objects.count()} sales total')

    def create_stock_movements(self):
        """Create sample stock movements"""
        products = Product.objects.all()
        users = User.objects.all()

        if not products.exists() or not users.exists():
            self.stdout.write('No products or users found. Skipping stock movements.')
            return

        movement_types = ['in', 'out', 'adjustment']

        for i in range(15):  # Create 15 sample stock movements
            try:
                product = random.choice(products)
                user = random.choice(users)
                movement_type = random.choice(movement_types)

                if movement_type == 'in':
                    quantity = random.randint(10, 50)
                    notes = f'Stock replenishment - Purchase Order #{random.randint(1000, 9999)}'
                    # Update product stock
                    product.stock_quantity += quantity
                    product.save()
                elif movement_type == 'out':
                    max_out = min(product.stock_quantity, 20)
                    if max_out <= 0:
                        continue
                    quantity = -random.randint(1, max_out)
                    notes = f'Stock issued - Manual adjustment'
                    # Update product stock
                    product.stock_quantity += quantity  # quantity is negative
                    product.save()
                else:  # adjustment
                    quantity = random.randint(-10, 10)
                    notes = f'Stock adjustment - Inventory count correction'
                    if product.stock_quantity + quantity >= 0:
                        product.stock_quantity += quantity
                        product.save()
                    else:
                        continue

                movement = StockMovement.objects.create(
                    product=product,
                    movement_type=movement_type,
                    quantity=abs(quantity),  # Store absolute value
                    reference_type='manual',
                    notes=notes,
                    created_by=user,
                    created_at=datetime.now() - timedelta(days=random.randint(0, 30))
                )

                self.stdout.write(f'Created stock movement: {product.name} - {movement_type} - {abs(quantity)}')

            except Exception as e:
                self.stdout.write(f'Error creating stock movement {i + 1}: {str(e)}')

        self.stdout.write(f'Created {StockMovement.objects.count()} stock movements total')