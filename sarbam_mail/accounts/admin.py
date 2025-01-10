from django.contrib import admin

from accounts.models import User, PromoCode

# Register your models here.

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
   readonly_fields = ('email', 'name', 'phone_number', 'address', 'last_login')
   exclude = ('password',)