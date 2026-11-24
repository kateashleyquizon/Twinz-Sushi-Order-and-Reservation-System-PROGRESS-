from django.db import models


# 1. Employee Model
class Employee(models.Model):
    employee_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.employee_name

# 2. Customer Model
class Customer(models.Model):
    customer_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.customer_name

# 3. Category Model
class Category(models.Model):
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

# 4. Menu Item Model
class MenuItem(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    item_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.item_name


# Reservation Model
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    DELIVERY_CHOICES = [
        ('Pickup', 'Pickup'),
        ('Door-to-Door', 'Door-to-Door Delivery'),
    ]

    PAYMENT_CHOICES = [
    ('COD', 'Cash on Delivery'),
    ('GCash', 'GCash'),
    ('GoTyme', 'GoTyme'),
    ('Maribank', 'Maribank'),
    ]

    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE
    )

    delivery_option = models.CharField(
        max_length=20, choices=DELIVERY_CHOICES,
        default='Pickup'
    )
    reservation_date = models.DateField()
    reservation_time = models.TimeField()

    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES,
        default='COD'
    )
    downpayment_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )

    reservation_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"Reservation #{self.id}"

# 6. Order Model
class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Ready', 'Ready'),
        ('Completed', 'Completed'),
    ]

    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    order_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return f"Order #{self.id}"


# 7. Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.menu_item} - {self.quantity}"


# 8. Transaction Model
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('Order', 'Order Payment'),
        ('Reservation', 'Reservation Downpayment'),
    ]

    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )
    transaction_date = models.DateTimeField(auto_now_add=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"Transaction #{self.id}"