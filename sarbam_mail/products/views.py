from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from accounts.models import PromoCode, User

from mail_system.tasks import send_order_email_task

from django_filters.rest_framework import DjangoFilterBackend

from products.models import (
   Category,
   OrderItem,
   Product,
   CartProduct,
   Cart,
   Order,
   ComboDeal,
   HotDeal,
   SamplePack
)

from products.serializers import (
   CategorySerializer,
   OrderItemSerializer,
   ProductSerializer,
   CartProductSerializer,
   CartSerializer,
   OrderSerializer,
   ComboDealSerializer,
   HotDealSerializer,
   SamplePackSerializer,
)

from django_filters import rest_framework as filters


# CATEGORY LIST VIEW
####################

class CategoryListAPIView(generics.ListAPIView):
   queryset = Category.objects.all()
   serializer_class = CategorySerializer
   filter_backends = (SearchFilter,)
   search_fields = ('name',)



# PRODUCT LIST VIEW
####################
class ProductFilter(filters.FilterSet):
   category_name = filters.CharFilter(field_name='category__category_name', lookup_expr='iexact')

   class Meta:
      model = Product
      fields = ['category_name']


class ProductListAPIView(generics.ListAPIView):
   queryset = Product.objects.select_related('category').prefetch_related('cart_products')
   serializer_class = ProductSerializer
   filter_backends = (SearchFilter, DjangoFilterBackend)
   search_fields = ('name',)
   filterset_class = ProductFilter


# ADD ITEM TO CART
######################

class AddProductToCartAPIView(generics.GenericAPIView):
   permission_classes = (IsAuthenticated,)
   serializer_class = CartProductSerializer

   def post(self, request, product_id, *args, **kwargs):
      try:
         product = Product.objects.prefetch_related('cart_products').get(id=product_id)
      except Product.DoesNotExist:
         return Response(
            {'message': "Product can't be found!"},
            status=status.HTTP_404_NOT_FOUND
         )
      
      qty = int(request.query_params.get('qty', 1))

      user_id = request.user.id
      user = User.objects.get(id=user_id)
      address = user.address

      cart, created = Cart.objects.get_or_create(
         user=user,
         checked_out=False,
      )

      if created:
         cart.address = address

      try:
         cart_product = CartProduct.objects.get(cart=cart, product=product, status="Pending")
         cart_product.qty += qty
         print('Cart Fetched!')
      
      except CartProduct.DoesNotExist:
         cart_product = CartProduct.objects.create(cart=cart, product=product, qty=qty)
         print("Cart Created!")

      cart_product.save()

      cart.update_total_amount()
      cart.save()

      return Response(
         {
            'id': cart_product.id, # type:ignore
            'message': "Product added to cart successfully!",
            'address': user.address
         },
         status=status.HTTP_201_CREATED
      )



# CART VIEW FOR A USER
######################

class CartListAPIView(generics.GenericAPIView):
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            cart = Cart.objects.get(user=user, checked_out=False)
        except Cart.DoesNotExist:
            return Response(
                {'message': "No Cart Found!"},
                status=status.HTTP_204_NO_CONTENT
            )

        serializer = self.serializer_class(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)


# CART AND CART ITEMS STATUS
############################

class CancelCartProductAPIView(generics.GenericAPIView):
   permission_classes = (IsAuthenticated,)
   serializer_class = CartProductSerializer

   def delete(self, request, product_id, *args, **kwargs):
      try:
         product = CartProduct.objects.select_related('cart').get(id = product_id)
      except CartProduct.DoesNotExist:
         return Response(
            {'message': "Cart Item not Found!"},
            status=status.HTTP_404_NOT_FOUND
         )
      
      if product.cart.user != request.user:
         return Response(
            {'message': "You are not authorized to cancel this item!"},
            status=status.HTTP_401_UNAUTHORIZED
         )
      
      product.delete()

      return Response(
         {'message': "Cart Item cancelled successfully!"},
         status=status.HTTP_204_NO_CONTENT
      )


class DeleteCartAPIView(APIView):
   permission_classes = (IsAuthenticated,)

   def delete(self, request, cart_id, *args, **kwargs):
      try:
         cart = Cart.objects.select_related('user').prefetch_related('cart_items').get(id=cart_id)
      except Cart.DoesNotExist:
         return Response(
            {'message': "Cart Not Found!"},
            status=status.HTTP_404_NOT_FOUND
         )
      
      if cart.user != request.user:
         return Response(
            {'message': "You are not authorized to delete this cart!"},
            status=status.HTTP_401_UNAUTHORIZED
         )
      
      cart.delete()

      return Response(
         {'message': "Cart deleted successfully!"},
         status=status.HTTP_204_NO_CONTENT
      )
   

# ORDER PLACE
############################
class PlaceOrderAPIView(generics.GenericAPIView):
   permission_classes = (IsAuthenticated,)
   serializer_class = OrderSerializer

   def post(self, request, *args, **kwargs):
      try:
         cart = Cart.objects.get(user=request.user, checked_out=False)
         order = cart.place_order()

         order_items = [
            {
               "name": item.product.name,
               "qty": int(item.qty),
               "price": float(item.price),
               "weight": item.product.weight
            }
            for item in order.order_items.all() # type:ignore
         ]

         send_order_email_task.delay(
            order_id = str(order.order_id),
            customer_name = order.user.name,
            customer_email = order.user.email,
            address = order.address,
            total_amount = float(order.total_amount),
            items = order_items,
         )

         serializer = self.serializer_class(order)

         return Response(
               {
                  "message": "Order placed successfully!",
                  "order": serializer.data
               },
               status=status.HTTP_201_CREATED,
         )
      
      except Cart.DoesNotExist:
         return Response({"error": "Active cart not found."}, status=status.HTTP_400_BAD_REQUEST)
      
      except ValueError as e:
         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


# ORDER AND ORDER ITEMS
#################################

class CancelOrderAPIView(APIView):
   permission_classes = (IsAuthenticated,)

   def patch(self, request, order_id, *args, **kwargs):
      user = request.user

      try:
         order = Order.objects.get(user=user, order_id=order_id)
      except Order.DoesNotExist:
         return Response(
            {'message': "No such order exists!"},
            status=status.HTTP_404_NOT_FOUND
         )
      
      order.status = "Cancelled"
      order.save()

      return Response(
         {"message": "Order cancelled successfully!"},
         status=status.HTTP_200_OK
      )


class CancelOrderItemAPIView(APIView):
   permission_classes = (IsAuthenticated,)

   def patch(self, request, order_item_id, *args, **kwargs):
      try:
         order_item = OrderItem.objects.get(id=order_item_id)
      except OrderItem.DoesNotExist:
         return Response(
            {'error': "Order Item doesn't exist!"},
            status=status.HTTP_404_NOT_FOUND
         )
      
      order_item.status = "Cancelled"
      order_item.save()

      return Response(
         {'message': "Order Item Cancelled."},
         status=status.HTTP_200_OK
      )



class UserOrdersAPIView(generics.GenericAPIView):
   permission_classes = (IsAuthenticated,)
   serializer_class = OrderSerializer

   def get(self, request):
      orders = Order.objects.filter(user=request.user).select_related('user').order_by('-created_at')
      serializer = self.serializer_class(orders, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
   


class ComboDealsAPIView(generics.GenericAPIView):
   queryset = ComboDeal.objects.all()
   permission_classes = (AllowAny,)
   serializer_class = ComboDealSerializer

   def get(self, request, *args, **kwargs):
      combo_deals = self.get_queryset()
      serializer = self.get_serializer(combo_deals, many=True)

      return Response(serializer.data, status=status.HTTP_200_OK)
   

class HotDealsAPIView(generics.GenericAPIView):
   queryset = HotDeal.objects.all()
   permission_classes = (AllowAny,)
   serializer_class = HotDealSerializer

   def get(self, request, *args, **kwargs):
      hot_deals = self.get_queryset()
      serializer = self.get_serializer(hot_deals, many=True)

      return Response(serializer.data, status=status.HTTP_200_OK)
   


class SamplePacksAPIView(generics.GenericAPIView):
   queryset = SamplePack.objects.all()
   permission_classes = (AllowAny,)
   serializer_class = SamplePackSerializer

   def get(self, request, *args, **kwargs):
      sample_packs = self.get_queryset()
      serializer = self.get_serializer(sample_packs, many=True)

      return Response(serializer.data, status=status.HTTP_200_OK)
   

class DeletePromoCodeFromUserAPIView(APIView):
   permission_classes = (IsAuthenticated,)

   def patch(self, *args, **kwargs):
      user_id = kwargs.get('user_id')
      promo_id = kwargs.get('promo_id')

      user = get_object_or_404(User, id=user_id)
      promo = get_object_or_404(PromoCode, id=promo_id)

      if not user.promocode.filter(id=promo_id).exists():
         return Response(
            {'message': "Promo Code for the user not found or invalid."},
            status=status.HTTP_400_BAD_REQUEST
         )
      
      user.promocode.remove(promo)

      return Response(
         {'message': "Promocode of the user deleted successfully!"},
         status=status.HTTP_204_NO_CONTENT
      )