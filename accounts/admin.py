from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserChangeForm, UserCreationForm
from .models import User
from django.contrib.auth.models import Group


# Register your models here.

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superadmin', 'is_staff', 'last_login', 'date_joined')})
    )

    add_fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'password1', 'password2')}),
    )

    list_display = (
        'email', 'first_name', 'last_name', 'last_login', 'date_joined', 'is_active',
    )

    list_display_links = (
        'email', 'first_name', 'last_name'
    )

    readonly_fields = (
        'last_login', 'date_joined'
    )

    ordering = (
        '-date_joined',
    )

    search_fields = ('email', 'username')

    filter_horizontal = ()
    list_filter = ()


admin.site.register(User, UserAdmin)
