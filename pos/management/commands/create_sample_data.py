from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pos.models import UserProfile, Category, Product

class Command(BaseCommand):
    help = 'Create sample data for testing'

    def handle(self, *args, **options):
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User'
            )
            UserProfile.objects.create(user=admin_user, role='admin', phone='1234567890')
            self.stdout.write('Admin user created: admin/admin123')

        # Create cashier user
        if not User.objects.filter(username='cashier').exists():
            cashier_user = User.objects.create_user(
                username='cashier',
                email='cashier@example.com',
                password='cashier123',
                first_name='Cashier',
                last_name='User'
            )
            UserProfile.objects.create(user=cashier_user, role='cashier', phone='9876543210')
            self.stdout.write('Cashier user created: cashier/cashier123')

        # Create sample categories
        categories = [
            {'name': 'Beverages', 'description': 'Soft drinks, juices, water'},
            {'name': 'Snacks', 'description': 'Chips, biscuits, chocolates'},
            {'name': 'Dairy', 'description': 'Milk, cheese, yogurt'},
            {'name': 'Groceries', 'description': 'Rice, flour, spices'},
        ]

        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Category created: {category.name}')

        # Create sample products
        products = [
            {'name': 'Coca Cola 500ml', 'category': 'Beverages', 'price': 25.00, 'stock': 50},
            {'name': 'Lays Chips 50g', 'category': 'Snacks', 'price': 15.00, 'stock': 30},
            {'name': 'Milk 1L', 'category': 'Dairy', 'price': 45.00, 'stock': 20},
            {'name': 'Rice 1kg', 'category': 'Groceries', 'price': 80.00, 'stock': 25},
            {'name': 'Pepsi 500ml', 'category': 'Beverages', 'price': 25.00, 'stock': 40},
            {'name': 'Oreo Biscuits', 'category': 'Snacks', 'price': 30.00, 'stock': 35},
            {'name': 'Cheese 200g', 'category': 'Dairy', 'price': 120.00, 'stock': 15},
            {'name': 'Wheat Flour 1kg', 'category': 'Groceries', 'price': 60.00, 'stock': 20},
        ]

        for prod_data in products:
            category = Category.objects.get(name=prod_data['category'])
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'category': category,
                    'price': prod_data['price'],
                    'stock_quantity': prod_data['stock'],
                    'min_stock_level': 5,
                }
            )
            if created:
                self.stdout.write(f'Product created: {product.name}')

        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
