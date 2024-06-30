from django.shortcuts import render,redirect
import requests
import base64
from django.views import View
from django.contrib.auth import logout
from django.core.paginator import Paginator
from datetime import datetime
from django.views.generic import View
from django.contrib import messages
from django.contrib.auth.models import User
from Cart.models import Order,Products,OrderItem,Customer
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import render_to_string
from datetime import date
from django.http import HttpResponse
from django.template.loader import get_template
import pdfkit
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
# defining the function to convert an HTML file to a PDF file


def home(request):
    return render(request, 'frontend/home.html')

private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

private_key_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)

def generate_signature(request):
    if request.method == 'POST':
        data = request.POST.get('data')  # Assuming the form field name is 'data'

        # Generate the digital signature
        signature = generate_digital_signature(data)

        return render(request, 'frontend/signature.html', {'signature': signature})

def verify_signature(request):
    if request.method == 'POST':
        data = request.POST.get('data')  # Assuming the form field name is 'data'
        signature = request.POST.get('signature')  # Assuming the form field name is 'signature'

        # Verify the digital signature
        is_valid = verify_digital_signature(data, signature)

        return render(request, 'frontend/verification.html', {'is_valid': is_valid})

def generate_digital_signature(data):
    data_bytes = data.encode()

    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # Encode the signature using Base64
    signature_base64 = base64.b64encode(signature).decode()

    return signature_base64

def verify_digital_signature(data, signature):
    with open('private_key.pem', 'rb') as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
            backend=default_backend()
        )
    
    try:
        public_key = private_key.public_key()
        public_key.verify(
            bytes.fromhex(signature),
            data.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

with open('private_key.pem', 'wb') as f:
    f.write(private_key_pem)

def registerview(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        customer_name = request.POST.get('customer_name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        address = request.POST.get('address')
        city=request.POST.get('city')
        state=request.POST.get('state')
        zipcode=request.POST.get('zipcode')

    
        data = {
            'username': username,
            'password': password,
            'customer_name': customer_name,
            'email': email,
            'contact': contact,
            'address': address,
            'city':city,
            'state':state,
            'zipcode':zipcode
        }
        try:
            response = requests.post(url='http://127.0.0.1:8000/api/createcustomer/', data=data)
            response.raise_for_status()  # Raise exception for non-successful response status codes
            json_response = response.json()
            return redirect('login_url')
        except requests.exceptions.RequestException as e:
            if hasattr(e, 'response') and e.response.status_code == 400:
                error_response = e.response.json()
                error_message = error_response.get('error')
            return render(request, 'frontend/error.html', {'error_message': error_message,'data':data})
    return render(request, 'frontend/register.html')



def loginview(request):
    if request.method== 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        print(username,password)

        data={
            'username':username,
            'password':password
        }

        response=requests.post(url='http://127.0.0.1:8000/api/login/',data=data)
        if response.status_code == 200:
            data=response.json()
            auth_token = data.get('auth_token')
            is_superuser = data.get('is_superuser')
            if auth_token:
                request.session['user_token']=auth_token
                request.session['username'] = username
                request.session['is_superuser']=is_superuser
            else:
                messages.error(request, 'Incorrect username or password')
                return redirect('login_url')

            if is_superuser:
                return redirect('adminview_url')
            else:
                return redirect('products_url')
        elif response.status_code == 401:
            messages.error(request, 'Incorrect username or password')
            return redirect('login_url')
    return render(request,'frontend/login.html')


def logoutview(request):
    if request.method == 'POST':
        logout(request)
        return redirect('products_url')
    return render(request,'frontend/confirmation.html')

def password_reset_complete(request):
    return render(request,'frontend/password_reset_complete.html')


def superuser_check(user):
    return user.is_superuser


#@login_required(login_url='login_url')
#@user_passes_test(superuser_check)
def adminview(request):
    auth_token = request.session.get('is_superuser')
    if not auth_token:
        return render(request, 'frontend/error.html')
    if auth_token:
        users=User.objects.all()[:5]
        len_user=len(User.objects.all())
        orders=Order.objects.all()[:5]
        order_len=len(Order.objects.all())
        top_selling_products = Products.objects.annotate(total_quantity_sold=Sum('orderitem__quantity')).order_by('-total_quantity_sold')[:10]
        return render(request,'frontend/index.html',{'len_user':len_user,'top_selling_products':top_selling_products,'order':orders,'order_len':order_len,'user':users})
    else:
        return redirect('products_url')

def top_sell_product(request):
    auth_token = request.session.get('is_superuser')
    if not auth_token:
        return render(request, 'frontend/error.html')
    top_selling_products = Products.objects.annotate(total_quantity_sold=Sum('orderitem__quantity')).order_by('-total_quantity_sold')[:10]
    return render(request,'frontend/top_sell.html',{'top_selling_products':top_selling_products})


def adminorderview(request):
    auth_token = request.session.get('is_superuser')
    if not auth_token:
        return render(request, 'frontend/error.html')
    orders = Order.objects.annotate(order_total=Sum('total_amount'))
    total_amount_sum = orders.aggregate(total_amount_sum=Sum('total_amount')).get('total_amount_sum', 0)
    return render(request,'frontend/total_order.html',{'order':orders,'sum_of_total':total_amount_sum})


def render_invoice_for_user(request,id):
    auth_token = request.session.get('user_token')
    
    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = f'http://localhost:8000/api/orderitem/{id}'
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        orders = response.json()
        user =User.objects.get(auth_token=auth_token)
        customer = Customer.objects.get(user=user)

        order=Order.objects.get(id=id)
        order_date=order.order_date
        for order in orders:
            order['total_price'] = order['price'] * order['quantity']
        total_amount_sum = sum((order['total_price']) for order in orders) 
        tax_amount = total_amount_sum * 0.09 
        total_amount=total_amount_sum+tax_amount          
        context={'orders': orders,
                'user':user,
                'customer':customer,
                'total_amount_sum':total_amount_sum,
                'tax_amount':tax_amount,
                'total_amount':total_amount,
                'order_id':id,
                'order_date': order_date}
        
        return render(request, 'frontend/invoice.html',context)
    else:
        return render(request, 'frontend/error.html')

def create_pdf_for_user(request,order_id):
    auth_token = request.session.get('user_token')
    
    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = f'http://localhost:8000/api/orderitem/{order_id}'
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        orders = response.json()
        user =User.objects.get(auth_token=auth_token)
        customer = Customer.objects.get(user=user)

        for order in orders:
            order['total_price'] = order['price'] * order['quantity']
        total_amount_sum = sum((order['total_price']) for order in orders) 
        tax_amount = total_amount_sum * 0.09 
        total_amount=total_amount_sum+tax_amount          
        context={'orders': orders,
                'user':user,
                'customer':customer,
                'total_amount_sum':total_amount_sum,
                'tax_amount':tax_amount,
                'total_amount':total_amount,
                'order_id':order_id}
        
        html_string = render_to_string('frontend/invoice.html', context)
        
        pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

        pdf = pdfkit.from_string(html_string,False,configuration=pdfkit_config)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="invoice.pdf"'
        response.write(pdf)

        return response

    return render(request,'frontend/error.html')
        

def report_render(request):
    auth_token = request.session.get('is_superuser')
    if auth_token:
        orders=Order.objects.all()
        subtotal=Order.objects.all().aggregate(Sum('subtotal_amount'))
        subtotal_amount=subtotal['subtotal_amount__sum']
        tax=Order.objects.all().aggregate(Sum('tax'))
        tax_amount=tax['tax__sum']
        total=Order.objects.all().aggregate(Sum('total_amount'))
        total_bill=total['total_amount__sum']
        today=date.today()
        context = {
            'today': today,
            'order': orders,
            'subtotal_amount': subtotal_amount,
            'tax': tax_amount,
            'total_bill': total_bill
        }
    return render(request,'frontend/report.html',context)

def create_invoice_pdf(request):
    auth_token = request.session.get('is_superuser')
    if not auth_token:
        return render(request, 'frontend/error.html')
    orders=Order.objects.all()
    subtotal=Order.objects.all().aggregate(Sum('subtotal_amount'))
    subtotal_amount=subtotal['subtotal_amount__sum']
    tax=Order.objects.all().aggregate(Sum('tax'))
    tax_amount=tax['tax__sum']
    total=Order.objects.all().aggregate(Sum('total_amount'))
    total_bill=total['total_amount__sum']
    today=date.today()
    context={'today': today, 'order': orders, 'subtotal_amount': subtotal_amount, 'tax': tax_amount, 'total_bill': total_bill}
    html_string = render_to_string('frontend/report.html', context)
        
    pdfkit_config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

    pdf = pdfkit.from_string(html_string,False,configuration=pdfkit_config)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="invoice.pdf"'
    response.write(pdf)

    return response
    #pdf=pdf_creator('frontend/report.html',context)
    #return HttpResponse(pdf, content_type='application/pdf')


def userview(request):
    auth_token = request.session.get('is_superuser')
    if not auth_token:
        return render(request, 'frontend/error.html')
    user=User.objects.all()
    return render(request,'frontend/user.html',{'user':user})

def activateuser(request,id):
    try:
        user=User.objects.get(id=id)
    except User.DoesNotExist:
        return render(request,'frontend/error.html')
    
    if user.is_active == False:
        user.is_active=True
        user.save()
        return redirect('userview_url')
    else:
        user.is_active=False
        user.save()
        return redirect('userview_url')

def edituser(request,id):
    try:
        user=User.objects.get(id=id)
    except User.DoesNotExist:
        return render(request,'frontend/error.html')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        contact = request.POST.get('contact')

        if User.objects.exclude(id=id).filter(username=username).exists():
            return render(request, 'frontend/error.html')

        # Check if the new email already exists
        if User.objects.exclude(id=id).filter(email=email).exists():
            return render(request, 'frontend/error.html')

        # Check if the new contact already exists in the Customer model
        if Customer.objects.exclude(user=user).filter(contact=contact).exists():
            return render(request, 'frontend/error.html')

        # Update the user information
        user.username = username
        user.email = email
        user.save()

        try:
            customer = user.customer
            customer_name = request.POST.get('customer_name')
            address = request.POST.get('address')
            city=request.POST.get('city')
            state=request.POST.get('state')
            zipcode=request.POST.get('zipcode')
            customer.customer_name = customer_name
            customer.email = email
            customer.contact = contact
            customer.address = address
            customer.city=city
            customer.state=state
            customer.zipcode=zipcode
            customer.save()
            return redirect('userview_url')
        except Customer.DoesNotExist:
            return render(request,'frontend/error.html')

    context = {'user': user}
    return render(request, 'frontend/singleuser.html', context)

def productsview(request):
    req=requests.get(url='http://127.0.0.1:8000/api/products/')
    response=req.json()
    paginator = Paginator(response, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    cart_items_count = 0
    if 'user_token' in request.session:
        auth_token = request.session['user_token']
        headers = {
            'Authorization': f'Token {auth_token}',
            'Content-Type': 'application/json'
        }
        cart_url = 'http://127.0.0.1:8000/api/cart/'
        cart_response = requests.get(cart_url, headers=headers)
        if cart_response.status_code == 200:
            cart_data = cart_response.json()
            cart_items = cart_data.get('cart_items', [])
            cart_items_count = len(cart_items)
    context={'page_obj':page_obj,
             'cart_items_count': cart_items_count}
    return render(request,'frontend/products.html',context)



def singleproductview(request,id):
    req=requests.get(url=f'http://127.0.0.1:8000/api/products/{id}/')
    if req.status_code == 200:
        product=req.json()
        price = product['price']
        tax=0.09
        tax_amount=price*tax
        total_price = price + tax_amount
        context={'product':product,'total_price': total_price,'tax_amount':tax_amount}
    else:
        context={}
    return render(request,'frontend/singleproduct.html',context)





class CartView(View):
    template_name = 'frontend/cartitem.html' 

    def get(self, request):
        auth_token = request.session.get('user_token')
        if not auth_token:
            return render(request, 'frontend/error.html', {'error_message': 'please login first !!'})

        try:
            api_url = 'http://localhost:8000/api/cart/'  
            headers = {
                'Authorization': f'Token {auth_token}',
                'Content-Type': 'application/json'
            }
            response = requests.get(api_url, headers=headers)
            response.raise_for_status() 

            data = response.json()
            cart_items = data.get('cart_items')
            subtotal = data.get('subtotal', 0)
            tax = data.get('tax', 0)
            total_amount = data.get('total_amount', 0)

            return render(request, self.template_name, {'cart_items': cart_items, 'subtotal': subtotal, 'tax': tax, 'total_amount': total_amount})
        except requests.exceptions.RequestException as e:
            return render(request, 'frontend/error.html', {'error_message': str(e)})
        except (KeyError, ValueError):
            return render(request, 'frontend/error.html', {'error_message': 'Invalid response from the API'})


def addtocartview(request,id):
    auth_token = request.session.get('user_token')
    if not auth_token:
        return redirect('login_url')

    api_url = 'http://localhost:8000/api/cart/' 
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }
    quantity=request.GET.get('quantity')
    data = {
        'product_id':id,
        'quantity':quantity
    }
    response = requests.post(api_url, headers=headers, json=data)

    if response.status_code == 201:
        return redirect('cart_url')
    else:
        return render(request, 'frontend/error.html')
    


def update_quantity_view(request, id):
    auth_token = request.session.get('user_token')
    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = f'http://localhost:8000/api/cart/{id}/' 
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }
    quantity = request.POST.get('quantity')
    data = {
        'product_id': id,
        'quantity': quantity
    }
    print(request.POST.get('quantity'))

    response = requests.put(api_url, headers=headers, json=data)

    if response.status_code == 205:
        return redirect('cart_url')
    else:
        return render(request, 'frontend/error.html')

def delete_cart_itmes(request, order_id):
    auth_token = request.session.get('user_token')
    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = f'http://localhost:8000/api/cart/{order_id}/'  # Update with your API URL
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }

    response = requests.delete(api_url, headers=headers)

    if response.status_code == 204:
        return redirect('cart_url')
    else:
        return render(request, 'frontend/error.html', {'error_message': 'Failed to delete order'})



def create_order_view(request):
    auth_token = request.session.get('user_token')

    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = 'http://localhost:8000/api/generate_order/'

    headers = {
        'Authorization': f'Token {auth_token}',
    }

    response = requests.post(api_url, headers=headers)

    if response.status_code == 201:
        order_data = response.json()
        return redirect('orders_url')
    else:
        error_message = response.json().get('error', 'Unknown error')
        return render(request, 'frontend/error.html', {'error_message': error_message})




def get_total_order(request):
    auth_token = request.session.get('user_token')
    
    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = 'http://localhost:8000/api/total_orders/'
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        orders = response.json()
        for order in orders:
            order['order_date'] = datetime.strptime(order['order_date'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%B %d, %Y, %I:%M %p')
            total_amount_sum = sum((order['total_amount']) for order in orders)
        return render(request, 'frontend/orderdetails.html', {'orders': orders,'total_amount_sum':total_amount_sum})
    else:
        return render(request, 'frontend/error.html')


def delete_order(request, order_id):
    auth_token = request.session.get('user_token')
    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = f'http://localhost:8000/api/total_orders/{order_id}/'  # Update with your API URL
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }

    response = requests.delete(api_url, headers=headers)

    if response.status_code == 204:
        return redirect('orders_url')
    else:
        return render(request, 'frontend/error.html', {'error_message': 'Failed to delete order'})




def order_items_view(request,order_id):
    auth_token = request.session.get('user_token')
    
    if not auth_token:
        return render(request, 'frontend/error.html', {'error_message': 'Authentication token not found'})

    api_url = f'http://localhost:8000/api/orderitem/{order_id}'
    headers = {
        'Authorization': f'Token {auth_token}',
        'Content-Type': 'application/json'
    }

    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        orders = response.json()
        return render(request, 'frontend/orderitem.html', {'orders': orders})
    else:
        return render(request, 'frontend/error.html')





