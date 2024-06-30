from django.contrib import admin
from .models import Customer,Products,CartItem,Cart,Order,OrderItem

# Register your models here.
class CustomerAdmin(admin.ModelAdmin):
    list_display=['id','customer_name','email','contact','address']
admin.site.register(Customer,CustomerAdmin)

class ProductsAdmin(admin.ModelAdmin):
    list_display=['id','product_name','description','price','image']
admin.site.register(Products,ProductsAdmin)

'''
class CartAdmin(admin.ModelAdmin):
    list_display=['customer','products']

admin.site.register(Cart,CartAdmin)

class CartItemAdmin(admin.ModelAdmin):
    list_display=['cart','product','quantity']
admin.site.register(CartItem,CartItemAdmin)
'''

class CartItemInline(admin.TabularInline):
    model = CartItem

class CartAdmin(admin.ModelAdmin):
    list_display = ['customer']
    inlines = [CartItemInline]

class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity']

admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)

class OrderItemInline(admin.TabularInline):
    model=OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'order_date','subtotal_amount','tax','total_amount']
    inlines=[OrderItemInline]
admin.site.register(Order,OrderAdmin)


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'quantity']
admin.site.register(OrderItem,OrderItemAdmin)
