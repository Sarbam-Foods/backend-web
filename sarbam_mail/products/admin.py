from django.contrib import admin
from django.utils.html import format_html

from products.models import (
    Category,
    Product,
    Order,
    OrderItem,
    ComboDeal,
    HotDeal,
    SamplePack,
    OrderSample, 
    OrderCombo,
    OrderHot,
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('product', 'qty', 'price', 'status')
    readonly_fields = ('product', 'qty', 'price')
    can_delete = False


class OrderComboInline(admin.TabularInline):
    model = OrderCombo
    extra = 0
    fields = ('product', 'qty', 'price', 'status')
    readonly_fields = ('product', 'qty', 'price')
    can_delete = False

class OrderHotInline(admin.TabularInline):
    model = OrderHot
    extra = 0
    fields = ('product', 'qty', 'price', 'status')
    readonly_fields = ('product', 'qty', 'price')
    can_delete = False

class OrderSampleInline(admin.TabularInline):
    model = OrderSample
    extra = 0
    fields = ('product', 'qty', 'price', 'status')
    readonly_fields = ('product', 'qty', 'price')
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'address', 'status', 'status_colored', 'created_at')
    list_display_links = ('order_id', 'user', 'total_amount', 'address', 'created_at')
    list_editable = ('status',)
    readonly_fields = ('order_id', 'user', 'total_amount', 'created_at')
    ordering = ('-created_at',)
    inlines = (OrderItemInline, OrderComboInline, OrderHotInline, OrderSampleInline)

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


# class CartProductInline(admin.TabularInline):
#     model = CartProduct
#     extra = 0
#     fields = ('product', 'qty', 'subtotal')
#     readonly_fields = ('product', 'qty', 'subtotal')
#     can_delete = False


# class CartComboInline(admin.TabularInline):
#     model = CartCombo
#     extra = 0
#     fields = ('product', 'qty', 'subtotal')
#     readonly_fields = ('product', 'qty', 'subtotal')
#     can_delete = False



# class CartHotInline(admin.TabularInline):
#     model = CartHot
#     extra = 0
#     fields = ('product', 'qty', 'subtotal')
#     readonly_fields = ('product', 'qty', 'subtotal')
#     can_delete = False



# class CartSampleInline(admin.TabularInline):
#     model = CartSample
#     extra = 0
#     fields = ('product', 'qty', 'subtotal')
#     readonly_fields = ('product', 'qty', 'subtotal')
#     can_delete = False



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



@admin.register(ComboDeal)
class ComboDealAdmin(admin.ModelAdmin):
    list_display = ('name', 'original_price', 'discounted_price')
    list_display_links = ('name', 'original_price', 'discounted_price')



@admin.register(HotDeal)
class HotDealAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'original_price', 'discounted_price')
    list_display_links = ('name', 'weight', 'original_price', 'discounted_price')


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('user', 'total_amount', 'address')
#     list_display_links = ('user', 'total_amount', 'address')

#     inlines = (CartProductInline, CartComboInline, CartHotInline, CartSampleInline)


@admin.register(SamplePack)
class SamplePackAdmin(admin.ModelAdmin):
    list_display = ('name', 'weight', 'original_price', 'discounted_price')
    list_display_links = ('name', 'weight', 'original_price', 'discounted_price')
