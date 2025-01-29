from django.contrib import admin

from accounts.models import User, PromoCode


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
   list_display = ('code', 'discount')
   list_display_links = ('code', 'discount')


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
   list_display = ('name', 'email', 'phone_number')
   list_display_links = ('name', 'email', 'phone_number')
   search_fields = ('name', 'email')
   list_filter = ('is_superuser',)
   exclude = ('otp', 'otp_expiry', 'password', 'groups', 'user_permissions')
   readonly_fields = ('email', 'name', 'phone_number', 'last_login')