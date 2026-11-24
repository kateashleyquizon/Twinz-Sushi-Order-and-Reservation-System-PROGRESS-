from django.contrib import admin
from .models import (Employee, Customer, Category, MenuItem,Order, OrderItem, Reservation, Transaction)

admin.site.register(Employee)
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Reservation)
admin.site.register(Transaction)