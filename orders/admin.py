from django.contrib import admin
from .models import Order, OrderItem, Coupon


# Register your models here.


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'updated', 'pied')
    list_filter = ('pied',)
    ordering = ('-pied',)
    inlines = (OrderItemInline,)


admin.site.register(Coupon)
