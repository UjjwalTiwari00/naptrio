from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Storefront
    path('', views.home, name='home'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('search/', views.search, name='search'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('corporate/', views.corporate, name='corporate'),

    # Cart
    path('cart/', views.cart_detail, name='cart'),
    path('cart/add/', views.cart_add, name='cart_add'),
    path('cart/remove/', views.cart_remove, name='cart_remove'),
    path('cart/update/', views.cart_update, name='cart_update'),

    # Checkout & order confirmation
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/create-payment/', views.create_razorpay_order, name='create_payment'),
    path('checkout/verify-payment/', views.verify_payment, name='verify_payment'),
    path('order/<int:order_id>/confirm/', views.order_confirm, name='order_confirm'),

    # Newsletter
    path('subscribe/', views.subscribe, name='subscribe'),
]
