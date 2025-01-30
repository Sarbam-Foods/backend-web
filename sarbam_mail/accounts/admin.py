from django.contrib import admin

from accounts.models import User, PromoCode


class UserInline(admin.TabularInline):
   model = User.promocode.through
   extra = 0
   can_delete = False
   readonly_fields = ('user',)
   verbose_name = "User"
   verbose_name_plural = "Users"
   

@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
   list_display = ('code', 'discount')
   list_display_links = ('code', 'discount')
   inlines = (UserInline,)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
   list_display = ('name', 'email', 'phone_number', "is_superuser")
   list_display_links = ('name', 'email', 'phone_number')
   search_fields = ('name', 'email')
   list_filter = ('is_superuser',)
   exclude = ('otp', 'otp_expiry', 'password', 'groups', 'user_permissions')
   readonly_fields = ('email', 'name', 'address', 'phone_number', 'promocode', 'last_login')