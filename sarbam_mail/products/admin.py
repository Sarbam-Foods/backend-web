from django.contrib import admin
from products.models import (
    Category,
    Product,
    Order,
    OrderItem
)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'qty', 'price')
    readonly_fields = ('product', 'qty', 'price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'created_at')
    list_display_links = ('order_id', 'user', 'total_amount', 'created_at')
    readonly_fields = ('order_id', 'user', 'total_amount', 'created_at')
    inlines = (OrderItemInline,)

class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'price', 'qty', 'weight', 'photo')
    readonly_fields = ('name', 'price', 'qty', 'weight', 'photo')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
   search_fields = ('Category',)
   inlines = (ProductInline,)



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'qty', 'weight', 'category')
    list_display_links = ('name', 'price', 'qty', 'weight', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

