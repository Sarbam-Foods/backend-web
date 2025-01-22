import uuid

from django.db.models import Sum
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from accounts.models import User


# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    category_name = models.CharField(max_length=155)

    def __str__(self):
        return self.category_name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(BaseModel):
    name = models.CharField(max_length=255)
    photo = models.ImageField(
        upload_to='products/',
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg'))],
        null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(validators=[MinValueValidator(0)])
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    weight = models.FloatField(validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f"{self.name}_{self.category}"


class Order(BaseModel):
    ORDER_STATUS = (
        ('Placed', "PLACED"),
        ('Shipped', "SHIPPED"),
        ('Out for Delivery', "OUT FOR DELIVERY"),
        ('Delivered', "DELIVERED"),
        ('Cancelled', "CANCELLED"),
    )

    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(choices=ORDER_STATUS, default="PENDING")

    def __str__(self):
        return f"Order_{self.order_id}"
    

class OrderItem(BaseModel):
    PRODUCT_STATUS = (
        ('Placed', "PLACED"),
        ('Confirmed', "CONFIRMED"),
        ('Cancelled', "CANCELLED"),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.FloatField(validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default='PLACED')

    def __str__(self):
        return f"{self.order}: {self.product.name}"


class Cart(BaseModel):
    cart_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    total_amount = models.FloatField(validators=[MinValueValidator(0)], default=0)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name}_Cart"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


    def update_total_amount(self):
        self.total_amount = self.cart_items.filter(status="Pending").aggregate(
            total = Sum('subtotal')
        )['total'] or 0.0

        self.save()


    def place_order(self):
        pending_items = self.cart_items.filter(status="Pending")

        if not pending_items.exists():
            raise ValueError("No pending items in the cart to place an order.")

        order = Order.objects.create(
            user=self.user,
            total_amount=self.total_amount,
            status = "Placed"
        )

        for cart_product in pending_items:
            OrderItem.objects.create(
                order=order,
                product=cart_product.product,
                qty=cart_product.qty,
                price=cart_product.subtotal
            )
            cart_product.status = "Placed"
            cart_product.save()

        self.checked_out = True
        self.delete()

        return order



class CartProduct(BaseModel):
    PRODUCT_STATUS = (
        ('Pending', "PENDING"),
        ('Placed', "PLACED"),
        ('Cancelled', "CANCELLED")
    )

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_products')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    subtotal = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending")

    def __str__(self):
        return f"{self.cart}: {self.product}"

    def calculate_item_amount(self):
        if not self.status == "Cancelled":
            return self.product.price * self.qty
        else:
            return 0

    def save(self, *args, **kwargs):
        self.subtotal = self.calculate_item_amount()
        super().save(*args, **kwargs)


@receiver(post_save, sender=CartProduct)
def update_cart_total_on_save(sender, instance, **kwargs):
    instance.cart.update_total_amount()


@receiver(post_delete, sender=CartProduct)
def update_cart_total_on_delete(sender, instance, **kwargs):
    instance.cart.update_total_amount()