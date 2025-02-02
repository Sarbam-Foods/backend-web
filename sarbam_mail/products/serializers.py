from rest_framework import serializers

from products.models import (
   Category,
   OrderCombo,
   OrderHot,
   OrderSample,
   Product,
   Cart,
   CartProduct,
   Order,
   OrderItem,
   ComboDeal,
   HotDeal,
   SamplePack,
)

from accounts.serializers import UserActivePromoCodeSerializer


class CategorySerializer(serializers.ModelSerializer):
   class Meta:
      model = Category
      fields = ('id', 'category_name',)


class ProductSerializer(serializers.ModelSerializer):
   category = CategorySerializer(read_only=True)

   class Meta:
      model = Product
      fields = ('id', 'name', 'photo', 'description', 'price', 'qty', 'weight', 'category')



class ProductInCartSerializer(serializers.ModelSerializer):
   category = CategorySerializer(read_only=True)

   class Meta:
      model = Product
      fields = ('id', 'name', 'photo', 'description', 'price', 'weight', 'category')


class CartProductSerializer(serializers.ModelSerializer):
   product = ProductInCartSerializer(read_only=True)

   class Meta:
      model = CartProduct
      fields = ('id', 'product', 'qty', 'subtotal', 'status')
      read_only_fields = ('id', 'cart')



class OrderItemSerializer(serializers.ModelSerializer):
   product = ProductSerializer(read_only=True)
   class Meta:
      model = OrderItem
      fields = ('id', 'product', 'qty', 'price', 'status')


class OrderComboSerializer(serializers.ModelSerializer):
   product = ProductSerializer(read_only=True)
   class Meta:
      model = OrderCombo
      fields = ('id', 'product', 'qty', 'price', 'status')



class OrderHotSerializer(serializers.ModelSerializer):
   product = ProductSerializer(read_only=True)
   class Meta:
      model = OrderHot
      fields = ('id', 'product', 'qty', 'price', 'status')

   
class OrderSampleSerializer(serializers.ModelSerializer):
   product = ProductSerializer(read_only=True)
   class Meta:
      model = OrderSample
      fields = ('id', 'product', 'qty', 'price', 'status')


class OrderSerializer(serializers.ModelSerializer):
   coupon_id = UserActivePromoCodeSerializer(read_only=True)
   order_items = OrderItemSerializer(many=True, read_only=True)
   order_hot_items = OrderHotSerializer(many=True, read_only=True)
   order_combo_items = OrderComboSerializer(many=True, read_only=True)
   order_sample_items = OrderSampleSerializer(many=True, read_only=True)

   class Meta:
      model = Order
      fields = ('order_id', 'total_amount', 'order_items', 'order_hot_items', 'order_combo_items', 'order_sample_items', 'status', 'coupon_id', 'is_coupon_applied', 'created_at')


class ProductInComboSerializer(serializers.ModelSerializer):
   class Meta:
      model = Product
      fields = ('id', 'name', 'photo', 'price', 'weight')



class ComboDealSerializer(serializers.ModelSerializer):

   class Meta:
      model = ComboDeal
      fields = ('id', 'name', 'photo', 'original_price', 'discount_rate', 'discounted_price', 'description')



class HotDealSerializer(serializers.ModelSerializer):

   class Meta:
      model = HotDeal
      fields = ('id', 'name', 'photo', 'original_price', 'discount_rate', 'discounted_price', 'description', 'weight')



class SamplePackSerializer(serializers.ModelSerializer):

   class Meta:
      model = SamplePack
      fields = ('id', 'name', 'photo', 'original_price', 'discount_rate', 'discounted_price', 'description', 'weight')


class CartComboSerializer(serializers.ModelSerializer):
   product = ComboDealSerializer(read_only=True)

   class Meta:
      model = CartProduct
      fields = ('id', 'product', 'qty', 'subtotal', 'status')
      read_only_fields = ('id', 'cart')



class CartSerializer(serializers.ModelSerializer):
   user = serializers.CharField(source='user.name', read_only=True)
   cart_items = CartProductSerializer(many=True, read_only=True)
   cart_combo_items = CartComboSerializer(many=True, read_only=True)

   class Meta:
      model = Cart
      fields = ('id', 'user', 'total_amount', 'address', 'checked_out', 'cart_items', 'cart_combo_items')
