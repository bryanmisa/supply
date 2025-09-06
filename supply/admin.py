from pyexpat.errors import messages
from django.contrib import admin
from  supply.models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from supply.models import CustomUser
from django.urls import reverse
from django.utils.html import format_html


# Register your models here.

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = ['username', 'email', 'first_name', 'last_name', 'user_type', 'is_staff', 'reset_password_link']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('User Type', {'fields': ('user_type',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'is_staff', 'is_superuser'),
        }),
    )
    
    def delete_model(self, request, obj):
        if obj.supplierprofile_set.exists():  # adjust relation name
            messages.error(request, "Cannot delete user with linked supplier profile.")
        else:
            super().delete_model(request, obj)

    def reset_password_link(self, obj):
        url = reverse('admin:auth_user_password_change', args=[obj.pk])
        return format_html('<a class="button" href="{}">Reset Password</a>', url)
    reset_password_link.short_description = 'Reset Password'


admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(SupplyManagerProfile)
admin.site.register(SupplierProfile)
admin.site.register(SupplyItem)
admin.site.register(SupplyItemTransaction)
admin.site.register(CustomerProfile)
admin.site.register(SupplyItemRequest)

