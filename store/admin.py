from django.contrib import admin
from .models import Product, Order, OrderItem

# Customizing the Admin Panel Interface Headers
admin.site.site_header = "Online Store Admin"
admin.site.site_title = "Online Store Admin Portal"
admin.site.index_title = "Welcome to Online Store Management Portal"

# Advanced registration for better layout visibility
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category')
    list_filter = ('category',)
    search_fields = ('name', 'category')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Removed date_ordered to resolve the build system check error
    list_display = ('id', 'user', 'completed')
    list_filter = ('completed',)
    search_fields = ('user__username', 'id')

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity')
    search_fields = ('order__id', 'product__name')