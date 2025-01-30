from rest_framework import serializers

from products.models import (
   Category,
   Product,
   Cart,
   CartProduct,
   Order,
   OrderItem,
   ComboDeal,
   HotDeal,
   SamplePack,
)


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


class CartSerializer(serializers.ModelSerializer):
   user = serializers.CharField(source='user.name', read_only=True)
   cart_items = CartProductSerializer(many=True, read_only=True)

   class Meta:
      model = Cart
      fields = ('id', 'user', 'total_amount', 'address', 'checked_out', 'cart_items')


class OrderItemSerializer(serializers.ModelSerializer):
   product = ProductSerializer(read_only=True)
   class Meta:
      model = OrderItem
      fields = ('id', 'product', 'qty', 'price', 'status')


class OrderSerializer(serializers.ModelSerializer):
   order_items = OrderItemSerializer(many=True, read_only=True)

   class Meta:
      model = Order
      fields = ('order_id', 'total_amount', 'order_items', 'status', 'coupon_id', 'is_coupon_applied', 'created_at')


class ProductInComboSerializer(serializers.ModelSerializer):
   class Meta:
      model = Product
      fields = ('id', 'name', 'photo', 'price', 'weight')




class ComboDealSerializer(serializers.ModelSerializer):

   class Meta:
      model = ComboDeal
      fields = ('id', 'name', 'photo', 'original_price', 'discount_rate', 'discounted_price', 'description', 'weight')



class HotDealSerializer(serializers.ModelSerializer):

   class Meta:
      model = HotDeal
      fields = ('id', 'name', 'photo', 'original_price', 'discount_rate', 'discounted_price', 'description', 'weight')



class SamplePackSerializer(serializers.ModelSerializer):

   class Meta:
      model = SamplePack
      fields = ('id', 'name', 'photo', 'original_price', 'discount_rate', 'discounted_price', 'description', 'weight')
