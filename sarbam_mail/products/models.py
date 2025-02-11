import uuid

from django.db.models import Sum
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from accounts.models import User, PromoCode


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
    id = models.CharField(unique=True, primary_key=True, editable=False, max_length=20)
    
    name = models.CharField(max_length=255)
    photo = models.ImageField(
        upload_to='products/',
        validators=[FileExtensionValidator(allowed_extensions=('png', 'jpg', 'jpeg' ))],
        null=True, blank=True
    )
    description = models.TextField(null=True, blank=True)
    price = models.FloatField(validators=[MinValueValidator(0)])
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    weight = models.FloatField(validators=[MinValueValidator(0)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return f"{self.name}_{self.category}"
    
    def save(self, *args, **kwargs):
        if not self.id:
            latest_product = Product.objects.order_by('-id').first()
            if latest_product:
                latest_id = int(latest_product.id.split('_')[1])
                count = latest_id + 1
                self.id = f"PRODUCT_{count:05d}"
            else:
                self.id = "PRODUCT_00001"
         
        super().save(*args, **kwargs)



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
    status = models.CharField(max_length=30, choices=ORDER_STATUS, default="PENDING")
    address = models.CharField(max_length=255, null=True, blank=True)
    coupon_id = models.ForeignKey(PromoCode, null=True, blank=True,  on_delete=models.SET_NULL, related_name='promo_coupon')
    is_coupon_applied = models.BooleanField(default=False)


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
    status = models.CharField(max_length=30,choices=PRODUCT_STATUS, default='PLACED')

    def __str__(self):
        return f"{self.order}: {self.product.name}"


class Cart(BaseModel):
    cart_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart')
    total_amount = models.FloatField(validators=[MinValueValidator(0)], default=0)
    address = models.CharField(max_length=255, null=True, blank=True)
    checked_out = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.name}_Cart"


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_total_amount()


    def update_total_amount(self):
        total = 0
        
        total += self.cart_items.filter(status="Pending").aggregate(total=Sum('subtotal'))['total'] or 0.0
        total += self.cart_combo_items.filter(status="Pending").aggregate(total=Sum('subtotal'))['total'] or 0.0
        total += self.cart_hot_items.filter(status="Pending").aggregate(total=Sum('subtotal'))['total'] or 0.0
        total += self.cart_sample_items.filter(status="Pending").aggregate(total=Sum('subtotal'))['total'] or 0.0

        self.total_amount = total


    def place_order(self):
        """Places an order, moving all cart items—including combo deals, hot deals, and sample packs—to the order and clearing the cart."""

        # Get all pending items from different categories
        pending_items = list(self.cart_items.filter(status="Pending")) + \
                        list(self.cart_combo_items.filter(status="Pending")) + \
                        list(self.cart_hot_items.filter(status="Pending")) + \
                        list(self.cart_sample_items.filter(status="Pending"))

        if not pending_items:
            raise ValueError("No pending items in the cart to place an order.")

        # Create a new order
        order = Order.objects.create(
            user=self.user,
            total_amount=self.total_amount,
            address=self.address,
            status="Placed"
        )

        # Move cart items to order items
        for cart_item in pending_items:
            if isinstance(cart_item, CartProduct):
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    qty=cart_item.qty,
                    price=cart_item.subtotal
                )
            elif isinstance(cart_item, CartCombo):
                OrderCombo.objects.create(
                    order=order,
                    product=cart_item.product,
                    qty=cart_item.qty,
                    price=cart_item.subtotal
                )
            elif isinstance(cart_item, CartHot):
                OrderHot.objects.create(
                    order=order,
                    product=cart_item.product,
                    qty=cart_item.qty,
                    price=cart_item.subtotal
                )
            elif isinstance(cart_item, CartSample):
                OrderSample.objects.create(
                    order=order,
                    product=cart_item.product,
                    qty=cart_item.qty,
                    price=cart_item.subtotal
                )

            # Mark cart item as placed
            cart_item.status = "Placed"
            cart_item.save()

        # Mark cart as checked out and delete it
        self.checked_out = True
        self.save()
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
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending", max_length=25)

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



class ComboDeal(models.Model):
    id = models.CharField(unique=True, primary_key=True, editable=False, max_length=20)

    name = models.CharField(max_length=125)
    photo = models.ImageField(upload_to='combo_deals/', null=True, blank=True, validators=[FileExtensionValidator(['jpeg', 'jpg', 'png'])])

    original_price = models.FloatField(null=True, blank=True, default=0)
    discount_rate = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discounted_price = models.FloatField(null=True, blank=True, default=0)

    description = models.TextField(default="", blank=True)


    def save(self, *args, **kwargs):
        if not self.id:
            latest_combo = ComboDeal.objects.order_by('-id').first()
            if latest_combo:
                latest_id = int(latest_combo.id.split('_')[1])
                count = latest_id + 1
                self.id = f"COMBO_{count:05d}"
            else:
                self.id = "COMBO_00001"
         
        self.discounted_price = self.original_price - (self.original_price * (self.discount_rate / 100)) # type: ignore

        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.id
    


class CartCombo(BaseModel):
    PRODUCT_STATUS = (
        ('Pending', "PENDING"),
        ('Placed', "PLACED"),
        ('Cancelled', "CANCELLED")
    )

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_combo_items')
    product = models.ForeignKey(ComboDeal, on_delete=models.CASCADE, related_name='cart_combo')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    subtotal = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending", max_length=25)

    def __str__(self):
        return f"{self.cart}: {self.product}"

    def calculate_item_amount(self):
        if not self.status == "Cancelled":
            return self.product.discounted_price * self.qty # type:ignore
        else:
            return 0

    def save(self, *args, **kwargs):
        self.subtotal = self.calculate_item_amount()
        super().save(*args, **kwargs)
    



class HotDeal(models.Model):
    id = models.CharField(max_length=125,unique=True, primary_key=True, editable=False)

    name = models.CharField(max_length=125)
    photo = models.ImageField(upload_to='hot_deals/', null=True, blank=True, validators=[FileExtensionValidator(['jpeg', 'jpg', 'png'])])

    original_price = models.FloatField(null=True, blank=True, default=0)
    discount_rate = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discounted_price = models.FloatField(null=True, blank=True, default=0)

    description = models.TextField(default="", blank=True)

    weight = models.FloatField(default=0, null=True, blank=True)


    class Meta:
        verbose_name = "Hot Deal"
        verbose_name_plural = "Hot Deals"

    def save(self, *args, **kwargs):
        if not self.id:
            latest_combo = HotDeal.objects.order_by('-id').first()
            if latest_combo:
                latest_id = int(latest_combo.id.split('_')[1])
                count = latest_id + 1
                self.id = f"HOT_{count:05d}"
            else:
                self.id = "HOT_00001"
         
        self.discounted_price = self.original_price - (self.original_price * (self.discount_rate / 100)) # type: ignore

        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.id
    

class CartHot(BaseModel):
    PRODUCT_STATUS = (
        ('Pending', "PENDING"),
        ('Placed', "PLACED"),
        ('Cancelled', "CANCELLED")
    )

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_hot_items')
    product = models.ForeignKey(HotDeal, on_delete=models.CASCADE, related_name='cart_hot')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    subtotal = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending", max_length=25)

    def __str__(self):
        return f"{self.cart}: {self.product}"

    def calculate_item_amount(self):
        if not self.status == "Cancelled":
            return self.product.discounted_price * self.qty # type:ignore
        else:
            return 0

    def save(self, *args, **kwargs):
        self.subtotal = self.calculate_item_amount()
        super().save(*args, **kwargs)




class SamplePack(models.Model):
    id = models.CharField(unique=True, primary_key=True, editable=False, max_length=20)

    name = models.CharField(max_length=125)
    photo = models.ImageField(upload_to='combo_deals/', null=True, blank=True, validators=[FileExtensionValidator(['jpeg', 'jpg', 'png'])])

    original_price = models.FloatField(null=True, blank=True, default=0)
    discount_rate = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    discounted_price = models.FloatField(null=True, blank=True, default=0)

    description = models.TextField(default="", blank=True)

    weight = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        verbose_name = "Sample Pack"
        verbose_name_plural = "Sample Packs"

    def save(self, *args, **kwargs):
        if not self.id:
            latest_combo = SamplePack.objects.order_by('-id').first()
            if latest_combo:
                latest_id = int(latest_combo.id.split('_')[1])
                count = latest_id + 1
                self.id = f"SAMPLE_{count:05d}"
            else:
                self.id = "SAMPLE_00001"
         
        self.discounted_price = self.original_price - (self.original_price * (self.discount_rate / 100)) # type: ignore

        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.id
    



class CartSample(BaseModel):
    PRODUCT_STATUS = (
        ('Pending', "PENDING"),
        ('Placed', "PLACED"),
        ('Cancelled', "CANCELLED")
    )

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_sample_items')
    product = models.ForeignKey(SamplePack, on_delete=models.CASCADE, related_name='cart_sample')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    subtotal = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending", max_length=25)

    def __str__(self):
        return f"{self.cart}: {self.product}"

    def calculate_item_amount(self):
        if not self.status == "Cancelled":
            return self.product.discounted_price * self.qty # type:ignore
        else:
            return 0

    def save(self, *args, **kwargs):
        self.subtotal = self.calculate_item_amount()
        super().save(*args, **kwargs)
    


class OrderHot(BaseModel):
    PRODUCT_STATUS = (
        ('Pending', "PENDING"),
        ('Placed', "PLACED"),
        ('Cancelled', "CANCELLED")
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_hot_items')
    product = models.ForeignKey(HotDeal, on_delete=models.CASCADE, related_name='order_hot')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending", max_length=25)

    def __str__(self):
        return f"{self.order}: {self.product}"



class OrderCombo(BaseModel):
    PRODUCT_STATUS = (
        ('Pending', "PENDING"),
        ('Placed', "PLACED"),
        ('Cancelled', "CANCELLED")
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_combo_items')
    product = models.ForeignKey(ComboDeal, on_delete=models.CASCADE, related_name='order_combo')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending", max_length=25)

    def __str__(self):
        return f"{self.order}: {self.product}"



class OrderSample(BaseModel):
    PRODUCT_STATUS = (
        ('Pending', "PENDING"),
        ('Placed', "PLACED"),
        ('Cancelled', "CANCELLED")
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_sample_items')
    product = models.ForeignKey(SamplePack, on_delete=models.CASCADE, related_name='order_sample')
    qty = models.IntegerField(validators=[MinValueValidator(0)])
    price = models.FloatField(default=0, validators=[MinValueValidator(0)])
    status = models.CharField(choices=PRODUCT_STATUS, default="Pending", max_length=25)

    def __str__(self):
        return f"{self.order}: {self.product}"
