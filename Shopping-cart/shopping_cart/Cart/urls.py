from django.urls import path
from .views import CustomerView,ProductApiView,LoginView,LogoutApiView,CreateCustomer,CartAPIView,GenerateOrderView
from .views import OrderListAPIView,SingleProductApiView,OrderItemAPIView



urlpatterns=[
    path('customer/',CustomerView.as_view(),name='create_customer'),
    path('createcustomer/',CreateCustomer.as_view(),name='createcustomer'),
    path('customer/<int:id>/',CustomerView.as_view(),name='customer_update'),
    path('products/', ProductApiView.as_view(), name='product-list-create'),
    path('products/<int:id>/',SingleProductApiView.as_view(), name='product-detail'),
    path('login/',LoginView.as_view(),name='login_url'),
    path('logout/',LogoutApiView.as_view(),name='logout'),
    path('cart/',CartAPIView.as_view(),name='cart_api'),
    path('cart/<int:cart_item_id>/',CartAPIView.as_view(),name='cart_api'),
    path('generate_order/',GenerateOrderView.as_view(),name='generate_order'),
    path('total_orders/',OrderListAPIView.as_view(),name='total_orders'),
    path('total_orders/<int:order_id>/',OrderListAPIView.as_view(),name='total_orders'),
    path('orderitem/<int:order_id>/',OrderItemAPIView.as_view(),name='orderdetails_url')
]