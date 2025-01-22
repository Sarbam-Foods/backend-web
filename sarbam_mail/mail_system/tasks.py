from celery import shared_task

from django.core.mail import EmailMessage, send_mail
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.conf import settings


@shared_task
def send_otp_email(email, otp, expiry, name, reset_url):
   subject = "Password Reset OTP"
   message = (
      f"Hello {name},\n\n"
      f"Your OTP for resetting your password is {otp}.\n"
      f"This OTP is valid until {expiry}.\n\n"
      f"If you did not request this, please ignore this email."
      f"\n\n"
      f"Reset your password using the link {reset_url}"
   )
   from_email = settings.EMAIL_HOST_USER
   recipient_list = [email]
   send_mail(subject, message, from_email, recipient_list)


@shared_task
def send_order_email_task(order_id, customer_name, customer_email, address, total_amount, items):
   try:
      order_date = now().date()

      email_body = render_to_string('mail_template.html', {
            'order_id': order_id,
            'name': customer_name,
            'email': customer_email,
            'address': address,
            'total_amount': total_amount,
            'order_date': order_date,
            'items': items,
         }
      )

      subject = "Your order has been placed!"
      from_email = settings.DEFAULT_FROM_EMAIL

      email = EmailMessage(
         subject=subject,
         body=email_body,
         from_email=from_email,
         to=[customer_email],
      )

      email.content_subtype = 'html'
      email.send()

      return {'status': "success", "message": "Email sent successfully!"}
   
   except Exception as e:
      return {'status': "error", "message": str(e)}