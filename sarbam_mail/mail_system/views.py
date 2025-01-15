from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from mail_system.tasks import send_order_email_task

class PlaceOrderMailView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = request.data

            order_id = data.get('order_id')
            customer_name = data.get('customer_name')
            customer_email = data.get('customer_email')
            address = data.get('address')
            total_amount = data.get('total_amount')
            items = data.get('item')
            link = data.get('link')

            order_date = timezone.now().date()

            send_order_email_task.delay(
                order_id,
                customer_name,
                customer_email,
                address,
                total_amount,
                items,
                link
            )

            return Response(
                {'message': "Email Task Initiated!"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {'error': f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
