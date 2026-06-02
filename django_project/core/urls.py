from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('account/',                       views.dashboard,    name='dashboard'),
    path('account/orders/',                views.orders,       name='orders'),
    path('account/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('account/profile/',               views.edit_profile, name='edit_profile'),
    path('signup/',                        views.signup,       name='signup'),
    path('signup/verify/',                 views.verify_otp,   name='verify_otp'),
    path('signup/resend-otp/',             views.resend_otp,   name='resend_otp'),
    path('signin/',                        views.signin,       name='signin'),
    path('signout/',                       views.signout,      name='signout'),
]
