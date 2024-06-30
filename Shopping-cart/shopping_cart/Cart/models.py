from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
import os
from django.dispatch import receiver
# Create your models here.

def _delete_file(path):
    """ Deletes file from filesystem. """
    if os.path.isfile(path):
        os.remove(path)

class Customer(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    customer_name=models.CharField(max_length=20)
    email=models.EmailField(unique=True)
    contact=models.CharField(max_length=20,unique=True)
    address=models.TextField()
    city=models.CharField(max_length=50,default='city')
    state=models.CharField(max_length=50,default='state')
    zipcode=models.CharField(max_length=10,default='00000')

    def __str__(self):
        return self.customer_name


class Products(models.Model):
    product_name=models.CharField(max_length=100)
    description=models.CharField(max_length=255)
    image=models.ImageField(upload_to='upload',null=True,blank=True)
    price = models.FloatField(default=0.0)

    def __str__(self):
        return f'{self.product_name},{self.description},{self.image.url},{self.price}'
    
@receiver(models.signals.post_delete, sender=Products)
def delete_file(sender, instance, *args, **kwargs):
    """ Deletes thumbnail files on `post_delete` """
    if instance.image:
        _delete_file(instance.image.path)

class Cart(models.Model):
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='cart')
    products = models.ManyToManyField(Products, through='CartItem')

    def __str__(self):
        return f'Cart for {self.customer}'

    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.product} - Quantity: {self.quantity}'



class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ManyToManyField(Products, through='OrderItem')
    order_date = models.DateTimeField(auto_now_add=True)
    subtotal_amount = models.FloatField(default=0.0)
    tax = models.FloatField(default=0.0)
    total_amount = models.FloatField(default=0.0)

    def __str__(self):
        return f'Order {self.id} - Customer: {self.customer}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,related_name='order_items')
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'Order {self.order.id} - Product: {self.product} - Quantity: {self.quantity}'


