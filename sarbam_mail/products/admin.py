from django.contrib import admin
from django.utils.html import format_html

from products.models import (
    Category,
    Product,
    Order,
    OrderItem,
    Cart,
    CartProduct
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'qty', 'price', 'status')
    readonly_fields = ('product', 'qty', 'price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'status_colored', 'created_at')
    list_display_links = ('order_id', 'user', 'total_amount', 'created_at')
    list_editable = ('status',)
    readonly_fields = ('order_id', 'user', 'total_amount', 'created_at')
    ordering = ('-created_at',)
    inlines = (OrderItemInline,)

    def status_colored(self, obj):
        """
        Render the status field with a background color based on its value.
        """
        if obj.status == "Placed":
            color = "yellow"
        elif obj.status == "Cancelled":
            color = "red"
        else:
            color = "lime"
        
        return format_html(
            '<span style="background-color: {}; padding: 5px; color: black; border-radius: 4px;">{}</span>',
            color,
            obj.status
        )

    status_colored.short_description = ""


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0
    fields = ('name', 'price', 'qty', 'weight', 'photo')
    readonly_fields = ('name', 'price', 'qty', 'weight', 'photo')


class CartProductInline(admin.TabularInline):
    model = CartProduct
    extra = 0
    fields = ('product', 'qty', 'subtotal')
    readonly_fields = ('product', 'qty', 'subtotal')
    can_delete = False


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


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('cart_id', 'user', 'total_amount', 'checked_out')
#     list_display_links = ('cart_id', 'user', 'total_amount', 'checked_out')
#     ordering = ('checked_out', '-created_at')
#     list_filter = ('checked_out',)
#     inlines = (CartProductInline,)


# @admin.register(CartProduct)
# class CartProductAdmin(admin.ModelAdmin):
#     list_display = ('product', 'cart', 'qty', 'subtotal', 'status')
#     list_display_links = ('product', 'cart', 'qty', 'subtotal', 'status')


# @admin.register(OrderItem)
# class OrderItem(admin.ModelAdmin):
#     list_display = ('order', 'product', 'order__user', 'status')
#     list_display_links = ('order', 'product', 'order__user')
#     list_editable = ('status',)