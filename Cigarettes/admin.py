from django.contrib import admin
from django.utils.safestring import mark_safe

from Cigarettes.models import *


class MainCart(admin.ModelAdmin):
    list_display = ('id', 'quantity', 'chat_id', 'get_sum')
    readonly_fields = ['get_sum']

    def get_sum(self, obj):
        return obj.Multiply

    get_sum.short_description = 'Сумма'


class MainProduct(admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'volume', 'brand', 'price', 'get_html_photo')
    search_fields = ('name', 'category__name',)
    list_display_links = ('name', 'id')
    readonly_fields = ['get_html_photo']

    def get_html_photo(self, obj):
        if obj.photo_url:
            print(obj.photo_url.url)
            return mark_safe(f'<img src="{obj.photo_url.url}" style="max-width:100px">')
        else:
            return mark_safe('<img src= "default.jpg">')

    get_html_photo.short_description = 'Миниатюра'


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')



class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'cart', 'free_delivery', 'sum', 'address', 'status', 'comment')


admin.site.register(ModelProduct, MainProduct)
admin.site.register(ModelCategory, CategoryAdmin)
admin.site.register(ModelBrand, BrandAdmin)
admin.site.register(ModelOrder, OrderAdmin)
