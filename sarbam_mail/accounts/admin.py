from django.contrib import admin

from accounts.models import User, PromoCode, Address

# Register your models here.
class AddressInline(admin.TabularInline):
   model = Address
   fields = ('province', 'municipality', 'district', 'location')
   extra = 0
   readonly_fields = ('province', 'municipality', 'district', 'location')
   can_delete = False


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
   inlines = (AddressInline,)