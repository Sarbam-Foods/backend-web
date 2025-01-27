from rest_framework import serializers

from products.models import (
   Category,
   Product,
   Cart,
   CartProduct,
   Order,
   OrderItem,
   ComboDeal,
   ComboProducts,
   HotDeal,
   HotDealProducts,
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
   cart = serializers.CharField(source = 'cart.user.name')

   class Meta:
      model = CartProduct
      fields = ('id', 'cart', 'product', 'qty', 'subtotal', 'status')
      read_only_fields = ('id', 'cart')


class CartSerializer(serializers.ModelSerializer):
   user = serializers.CharField(source='user.name', read_only=True)
   cart_items = CartProductSerializer(many=True, read_only=True)

   class Meta:
      model = Cart
      fields = ('id', 'user', 'total_amount', 'checked_out', 'cart_items')


class OrderItemSerializer(serializers.ModelSerializer):
   product = ProductSerializer(read_only=True)
   class Meta:
      model = OrderItem
      fields = ('id', 'product', 'qty', 'price', 'status')


class OrderSerializer(serializers.ModelSerializer):
   order_items = OrderItemSerializer(many=True, read_only=True)

   class Meta:
      model = Order
      fields = ('order_id', 'total_amount', 'order_items', 'order', 'status', 'created_at')


class ProductInComboSerializer(serializers.ModelSerializer):
   class Meta:
      model = Product
      fields = ('id', 'name', 'photo', 'price', 'weight')


class ComboProductSerializer(serializers.ModelSerializer):
   product = ProductInComboSerializer(read_only=True)
   
   class Meta:
      model = ComboProducts
      fields = ('product',)


class ComboDealSerializer(serializers.ModelSerializer):
   combo_deal = ComboProductSerializer(read_only=True, many=True)

   class Meta:
      model = ComboDeal
      fields = ('combo_id', 'name', 'photo', 'combo_deal', 'original_price', 'discount_rate', 'discounted_price', 'description', 'weight')


class HotDealProductSerializer(serializers.ModelSerializer):
   product = ProductInComboSerializer(read_only=True)
   
   class Meta:
      model = HotDealProducts
      fields = ('product',)


class HotDealSerializer(serializers.ModelSerializer):
   hot_deal = ComboProductSerializer(read_only=True, many=True)

   class Meta:
      model = HotDeal
      fields = ('hot_deal_id', 'name', 'photo', 'hot_deal', 'original_price', 'discount_rate', 'discounted_price', 'description', 'weight')