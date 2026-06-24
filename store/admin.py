from django.contrib import admin
from .models import Product, Order, OrderItem

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.site_header = "Online Store Admin"
admin.site.site_title = "Online Store Admin Portal"
admin.site.index_title = "Welcome to Online Store Management Portal"