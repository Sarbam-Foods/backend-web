from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.template import loader
from django.utils import timezone

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
            items = data.get('item')
            link = data.get('link')

            print(data)

            order_date = timezone.now().date()

            email_body = render_to_string('mail_template.html', {
                'order_id': order_id,
                'name': customer_name,
                'email': customer_email,
                'address': address,
                'total_amount': total_amount,
                'order_date': order_date,
                'items_list': items,
                'link': link,
            })

            subject = f"Your order has been placed!"
            from_email = settings.DEFAULT_FROM_EMAIL

            email = EmailMessage(
                subject,
                body=email_body,
                from_email=from_email,
                to=[customer_email],
            )
            email.content_subtype = 'html'
            email.send()


            return Response(
                {'message': "Email Sent Successfully!"},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {'error': f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
