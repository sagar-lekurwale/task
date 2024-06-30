from django.urls import path
from django.contrib.auth import views as auth_views
from .views import registerview,loginview,productsview,singleproductview,logoutview,CartView,addtocartview
from .views import update_quantity_view,create_order_view,get_total_order,order_items_view,delete_order,delete_cart_itmes
from .views import password_reset_complete,adminview,top_sell_product,adminorderview,userview,activateuser,edituser
from .views import create_invoice_pdf,report_render,render_invoice_for_user,create_pdf_for_user
from .views import home, generate_signature, verify_signature
urlpatterns=[
    path('reg/',registerview,name='register_url'),
    path('login/',loginview,name='login_url'),
    path('',productsview,name='products_url'),
    path('single/<int:id>/',singleproductview,name='singleproduct'),
    path('logout/',logoutview,name='logout_url'),
    path('cart/',CartView.as_view(),name='cart_url'),
    path('addtocart/<int:id>/',addtocartview,name='addtocart_url'),
    path('update-quantity/<int:id>/',update_quantity_view, name='update_quantity_url'),
    path('create_order/',create_order_view,name='create_order_url'),
    path('orders/',get_total_order,name='orders_url'),
    path('orderitemdetails/<int:order_id>/',order_items_view,name='orderitem_url'),
    path('delete_order/<int:order_id>/',delete_order,name='delete_order_url'),
    path('delete_cart_item/<int:order_id>/',delete_cart_itmes,name='delete_cart_items_url'),
    path('ad/',adminview,name='adminview_url'),
    path('top_sell/',top_sell_product,name='top_sell_product_url'),
    path('all_order/',adminorderview,name='admin_order_url'),
    path('users/',userview,name='userview_url'),
    path('acdc/<int:id>/',activateuser,name='active_deactive_url'),
    path('edituser/<int:id>/',edituser,name='edituser_url'),
    path('report/',report_render,name='report_render_url'),
    path('create_report_pdf/',create_invoice_pdf,name='report_pdf_url'),
    path('invoice_for_user/<int:id>/',render_invoice_for_user,name='render_invoice_user_url'),
    path('create_pdf_for_user/<int:order_id>/',create_pdf_for_user,name='create_pdf_for_user_url'),

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='frontend/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='frontend/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='frontend/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),

    path('home/', home, name='home'),
    path('generate_signature/', generate_signature, name='generate_signature'),
    path('verify_signature/', verify_signature, name='verify_signature'),
]