from rest_framework import serializers
from .models import Customer,Products,Cart,CartItem,OrderItem,Order


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(max_length=None, allow_empty_file=False, use_url=True)
    class Meta:
        model = Products
        fields = ('id','product_name', 'description', 'image', 'price')



class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    product_name = serializers.CharField(source='product.product_name')
    price = serializers.FloatField(source='product.price')
    image = serializers.ImageField(source='product.image')
    description = serializers.CharField(source='product.description')
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'product_name', 'price', 'image', 'description']      

class CartSerializer(serializers.ModelSerializer):
    customer = serializers.StringRelatedField()
    items = CartItemSerializer(many=True)

    class Meta:
        model = Cart
        fields = ['id','customer', 'items']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    product_name = serializers.CharField(source='product.product_name')
    price = serializers.FloatField(source='product.price')
    image = serializers.ImageField(source='product.image')
    description = serializers.CharField(source='product.description')
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'product_name', 'price', 'image', 'description']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer','order_date','subtotal_amount','tax','total_amount','order_items']