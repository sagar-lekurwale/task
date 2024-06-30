import requests
from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import CustomerSerializer,ProductSerializer,CartSerializer,CartItemSerializer,OrderItemSerializer,OrderSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import Customer,Products,Cart,CartItem,Order,OrderItem
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,logout
from Cart.permission import IsOwnerOrReadOnly
from django.core.exceptions import ObjectDoesNotExist


class CreateCustomer(APIView):    
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')
        email=request.data.get('email')
        contact=request.data.get('contact')

        try:
            User.objects.get(username=username)
            return Response({'error': 'username already exist'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            pass
        
        try:
            User.objects.get(email=email)
            return Response({'error': 'Email already exist'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            pass

        try:
            Customer.objects.get(contact=contact)
            return Response({'error': 'Contact already exists'}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectDoesNotExist:
            pass

        user=User.objects.create_user(username=username,password=password,email=email)
        customer_name=request.data.get('customer_name')
        email=request.data.get('email')
        address=request.data.get('address')
        city=request.data.get('city')
        state=request.data.get('state')
        zipcode=request.data.get('zipcode')

        customer=Customer(user=user,customer_name=customer_name,email=email,contact=contact,address=address,city=city,state=state,zipcode=zipcode)
        customer.save()
        return Response({'msg':'customer Account created'},status=status.HTTP_201_CREATED)

class CustomerView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated,IsOwnerOrReadOnly]
    def get(self,request):
        customer=Customer.objects.all()
        serializer=CustomerSerializer(customer,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def put(self,request,id):
        try:
            customer=Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return Response({'msg':'Customer Does Not Exits'})
        if customer.user != request.user:
            return Response({'msg': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        serializer=CustomerSerializer(customer,data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_205_RESET_CONTENT)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        try:
            customer=Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return Response({'msg':'Customer Does Not Exits'})
        
        if customer.user != request.user:
            return Response({'msg': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        customer.delete()
        return Response({'msg':'Customer information deleted successfully'},status=status.HTTP_204_NO_CONTENT)
    

class LoginView(APIView):
    def post(self,request):
        username=request.data.get('username')
        password=request.data.get('password')

        user=authenticate(username=username,password=password)
        if user is not None:
            if user.is_superuser:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'auth_token': token.key,'is_superuser':True}, status=status.HTTP_200_OK)
            else:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({'auth_token': token.key,'is_superuser':False}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class LogoutApiView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    def post(self, request):
        if 'auth_token' in request.session:
            del request.session['auth_token'] 
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    

class ProductApiView(APIView):
    
    def get(self,request):
        product=Products.objects.all()
        serializer=ProductSerializer(product,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
    def post(self,request):
        serializer=ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class SingleProductApiView(APIView):
    def get(self,request,id):
        try:
            product=Products.objects.get(id=id)
        except Products.DoesNotExist:
            msg={'msg':'Record Not Found'}
            return Response({'msg':'Product not found'},status=status.HTTP_404_NOT_FOUND)
        serializer=ProductSerializer(product)
        return Response(serializer.data,status=status.HTTP_200_OK)

class CartAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]

    def get(self, request):
        customer = request.user.customer
        cart_items = CartItem.objects.filter(cart__customer=customer)
        auth_token = request.session.get('auth_token')
        print(auth_token)
        serializer = CartItemSerializer(cart_items, many=True)
        # Calculate subtotal, tax, and total amount for all products in the cart
        subtotal = sum(item.quantity * item.product.price for item in cart_items)
        tax = 0.09 * subtotal  # Assuming tax rate is 10% (adjust as needed)
        total_amount = subtotal + tax

        response_data = {
            'cart_items': serializer.data,
            'subtotal': subtotal,
            'tax': tax,
            'total_amount': total_amount
        }

        return Response(response_data, status=status.HTTP_200_OK)
        #return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        customer = request.user.customer

        # Check if the customer already has a cart
        if hasattr(customer, 'cart'):
            cart = customer.cart
        else:
            # Create a new cart for the customer
            cart = Cart(customer=customer)
            cart.save()

        # Add product to the cart
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        try:
            product = Products.objects.get(id=product_id)
        except Products.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        # Add the product to the cart with the specified quantity
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.save()

        cart_items = CartItem.objects.filter(cart=cart)
        subtotal = sum(item.quantity * item.product.price for item in cart_items)
        tax = 0.09 * subtotal  # Assuming tax rate is 10% (adjust as needed)
        total_amount = subtotal + tax

        serializer = CartItemSerializer(cart_item)
        response_data = serializer.data
        response_data['subtotal'] = subtotal
        response_data['tax'] = tax
        response_data['total_amount'] = total_amount

        return Response(response_data, status=status.HTTP_201_CREATED)

        #serializer = CartItemSerializer(cart_item)
        #return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self,request,cart_item_id):
        customer=request.user.customer

        try:
            cart_item=CartItem.objects.get(id=cart_item_id,cart__customer=customer)
        except CartItem.DoesNotExist:
            return Response({'error':'Cart Item Not Found'},status=status.HTTP_404_NOT_FOUND)
        
        if cart_item.cart.customer != customer:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        quantity=request.data.get('quantity',cart_item.quantity)
        cart_item.quantity=quantity
        cart_item.save()

        serializer=CartItemSerializer(cart_item,partial=True)
        return Response(serializer.data, status=status.HTTP_205_RESET_CONTENT)


    def delete(self, request, cart_item_id):
        customer = request.user.customer

        try:
            cart_item = CartItem.objects.get(id=cart_item_id, cart__customer=customer)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if cart_item.cart.customer != customer:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        # Remove the cart item from the cart
        cart_item.delete()

        return Response({'message': 'Cart item removed'}, status=status.HTTP_204_NO_CONTENT)
    


class GenerateOrderView(APIView):
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated,IsOwnerOrReadOnly]

    def post(self,request):
        customer=request.user.customer

        try:
            cart = Cart.objects.get(customer=customer)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        if cart.customer != customer:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        cart_items=cart.cartitem_set.all()

        if not cart_items:
            return Response({'error':'No Items In The Cart'},status=status.HTTP_400_BAD_REQUEST)

        order=Order.objects.create(customer=customer)
        
        subtotal_amount=0

        #cart_items=CartItem.objects.filter(cart__customer=customer)
        for cart_item in cart_items:
            OrderItem.objects.create(order=order,product=cart_item.product,quantity=cart_item.quantity)
            subtotal_amount += cart_item.product.price * cart_item.quantity

        tax= 0.09 * subtotal_amount
        total_amount= subtotal_amount + tax

        order.subtotal_amount=subtotal_amount
        order.tax = tax
        order.total_amount=total_amount
        order.save()

        cart_items.delete()

        serializer=OrderSerializer(order)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    
class OrderListAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self,request,order_id):
        customer=request.user.customer

        try:
            order=Order.objects.get(id=order_id,customer=customer)
        except Order.DoesNotExist:
            return Response({'error':'Order Not Found'},status=status.HTTP_400_BAD_REQUEST)
        
        if order.customer != customer:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        order.delete()

        return Response({'message':'Order Canceled'},status=status.HTTP_204_NO_CONTENT)


class OrderItemAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, order_id):
        customer = request.user.customer
        try:
            order = Order.objects.get(customer=customer, id=order_id)
            order_items = order.order_items.all()
            serializer = OrderItemSerializer(order_items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OrderItem.DoesNotExist:
            return Response({'error': 'Order items not found'}, status=status.HTTP_404_NOT_FOUND)










