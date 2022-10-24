from django.contrib import admin
from .models import Category, Brand, Product, ProductImage, Promotion
# Register your models here.

# class ProductAdmin(admin.ModelAdmin):
    # list_display = ('Product object', 'name')
# admin.site.register(Product,ProductAdmin)    

# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ('name',)
# admin.site.register(Category,CategoryAdmin)

# class BrandAdmin(admin.ModelAdmin):
#     list_display = ('name',)
# admin.site.register(Brand,BrandAdmin)

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Brand)
admin.site.register(ProductImage)
admin.site.register(Promotion)
