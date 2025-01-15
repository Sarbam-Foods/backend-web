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
    price = models.FloatField(validators=[MinValueValidator(0)])
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    weight = models.FloatField(validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f"{self.name}_{self.category}"


class Order(BaseModel):
    order_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.FloatField(validators=[MinValueValidator(0)])
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return f"Order_{self.order_id}"
    

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField(validators=[MinValueValidator(1)])
    price = models.FloatField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.order}: {self.product.name}"


class Cart(BaseModel):
    cart_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    total_amount = models.FloatField(validators=[MinValueValidator(0)], default=0)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name}_Cart"

    def update_total_amount(self):
        self.total_amount = self.cart_items.aggregate(
            total=Sum('subtotal')
        )['total'] or 0.0
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def place_order(self):
        if self.checked_out or not self.cart_items.exists():
            raise ValueError("Cart is already checked out or empty.")

        order = Order.objects.create(
            user=self.user,
            total_amount=self.total_amount,
        )

        for cart_product in self.cart_items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_product.product,
                qty=cart_product.qty,
                price=cart_product.subtotal
            )

        self.checked_out = True
        self.save()

        return order



class CartProduct(BaseModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_products')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    subtotal = models.FloatField(default=0, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.cart}: {self.product}"

    def calculate_item_amount(self):
        return self.product.price * self.qty

    def save(self, *args, **kwargs):
        self.subtotal = self.calculate_item_amount()
        super().save(*args, **kwargs)


@receiver(post_save, sender=CartProduct)
def update_cart_total_on_save(sender, instance, **kwargs):
    instance.cart.update_total_amount()


@receiver(post_delete, sender=CartProduct)
def update_cart_total_on_delete(sender, instance, **kwargs):
    instance.cart.update_total_amount()