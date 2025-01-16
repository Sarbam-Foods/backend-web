from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from django_filters.rest_framework import DjangoFilterBackend

from mail_system.tasks import send_order_email_task

from products.models import (
   Category,
   Product,
   CartProduct,
   Cart,
   Order,
)

from products.serializers import (
   CategorySerializer,
   ProductSerializer,
   CartProductSerializer,
   CartSerializer,
   OrderSerializer,
)


# CATEGORY LIST VIEW
####################

class CategoryListAPIView(generics.ListAPIView):
   queryset = Category.objects.all()
   serializer_class = CategorySerializer
   filter_backends = (SearchFilter,)
   search_fields = ('name',)




# PRODUCT LIST VIEW
####################

class ProductListAPIView(generics.ListAPIView):
   queryset = Product.objects.select_related('category').prefetch_related('cart_products')
   serializer_class = ProductSerializer
   filter_backends = (SearchFilter, DjangoFilterBackend)
   search_fields = ('name',)
   filterset_fields = ('category',)



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

      user = request.user

      cart, created = Cart.objects.get_or_create(user=user, checked_out=False)

      try:
         cart_product = CartProduct.objects.get(cart=cart, product=product)
         cart_product.qty += qty
         print('Cart Fetched!')
      
      except CartProduct.DoesNotExist:
         cart_product = CartProduct.objects.create(cart=cart, product=product, qty=qty)
         print("Cart Created!")

      cart_product.save()
      cart.update_total_amount()
      cart.save()

      return Response(
         {'message': "Product added to cart successfully!"},
         status=status.HTTP_201_CREATED
      )


# CART VIEW FOR A USER
######################

class CartListAPIView(generics.ListAPIView):
   serializer_class = CartSerializer
   permission_classes = (IsAuthenticated,)

   def get_queryset(self):
      user = self.request.user

      if user.is_authenticated and user.is_superuser:
         return Cart.objects.filter(user=user, checked_out=False).select_related('user').prefetch_related('cart_items')
      else:
         return Cart.objects.none()
      



# CART AND CART ITEMS DELETE
############################

class DeleteCartProductAPIView(generics.GenericAPIView):
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
            {'message': "You are not authorized to delete this item!"},
            status=status.HTTP_401_UNAUTHORIZED
         )
      
      product.delete()

      return Response(
         {'message': "Cart Item deleted successfully!"},
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
   

class PlaceOrderAPIView(generics.GenericAPIView):
   permission_classes = (IsAuthenticated,)

   def post(self, request, *args, **kwargs):
      try:
         cart = Cart.objects.get(user=request.user, checked_out=False)
         order = cart.place_order()

         # order_id = str(order.order_id)
         # customer_name = order.user.name
         # customer_email = order.user.email
         # address = order.user.address
         # total_amount = float(order.total_amount)
         
         # order_items = [
         #    {
         #       "name": item.product.name,
         #       "qty": int(item.qty),
         #       "price": float(item.price),
         #       "weight": item.product.weight
         #    }
         #    for item in order.order_items.all()
         # ] 
 
         # items = order_items


         # send_order_email_task.delay(
         #    order_id = str(order.order_id),
         #    customer_name = order.user.name,
         #    customer_email = order.user.email,
         #    address = order.user.address,
         #    total_amount = float(order.total_amount),
         #    items = order_items,
         # )

         order_date = timezone.now()

         # email_body = render_to_string('mail_template.html',{
         #    'order_id': order_id,
         #    'name': customer_name,
         #    'email': customer_email,
         #    'address': address,
         #    'total_amount': total_amount,
         #    'order_date': order_date,
         #    'items': items,
         # })

         # subject = "Your order has been placed!"
         # from_email = settings.DEFAULT_FROM_EMAIL

         # email = EmailMessage(
         #    subject=subject,
         #    body=email_body,
         #    from_email=from_email,
         #    to=[customer_email],
         # )

         # email.content_subtype = 'html'
         # email.send()

         return Response(
               {"message": "Order placed successfully!", "order_id": str(order.order_id)},
               status=status.HTTP_201_CREATED,
         )
      
      except Cart.DoesNotExist:
         return Response({"error": "Active cart not found."}, status=status.HTTP_400_BAD_REQUEST)
      
      except ValueError as e:
         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
   
class UserOrdersAPIView(APIView):
   permission_classes = [IsAuthenticated]

   def get(self, request):
      orders = Order.objects.filter(user=request.user, delivered=False).select_related('user').order_by('-created_at')
      serializer = OrderSerializer(orders, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)