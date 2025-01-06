from django.core.mail import send_mail
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PlaceOrderView(APIView):
   def post(self, request, *args, **kwargs):
      try:
         data = request.data
         order_id = data.get('order_id')
         customer_name = data.get('customer_name')
         customer_email = data.get('customer_email')
         address = data.get('address')
         total_amount = data.get('total_amount')
         # items =  data.get('items')


         subject = f"Your order has been placed!"
         message = (
            f"Dear {customer_name},\n\n"
            f"Your order details for Order ID: {order_id} have been placed successfully.\n"
            f"Thank you for shopping with us!\n\n"
            f"Address: {address}\n"
            f"Total Amount: {total_amount}\n"
            # f"Items: {', '.join(item['name'] for item in items)}\n\n"
            f"Regards,\nSarbam Foods"
         )

         from_email = settings.DEFAULT_FROM_EMAIL

         send_mail(subject, message, from_email, [customer_email], fail_silently=False) # type: ignore

         return Response(
            {'message': "Email Sent Successfully!"},
            status=status.HTTP_200_OK
         )

      except Exception as e:
         return Response(
            {'error': f"An error occurred: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
         )