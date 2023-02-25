from django.contrib import admin
from .models import Category, Product, Comment


# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = (
        'name', 'slug', 'is_sub'
    )
    ordering = (
        'is_sub',
    )


admin.site.register(Category, CategoryAdmin)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = (
        'name', 'slug'
    )
    raw_id_fields = ('category',)


@admin.register(Comment)
class Comment(admin.ModelAdmin):
    list_display = ('user', 'post', 'created', 'is_reply')
    raw_id_fields = ('user', 'post', 'reply')
