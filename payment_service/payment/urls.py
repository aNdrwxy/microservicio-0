from django.contrib import admin
from django.urls import path
from payment.paymentApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/payments/<str:order_id>/', views.get_payment, name='get_payment'),
    path('api/payments/<str:paypal_order_id>/capture/', views.capture_payment, name='capture_payment'),
]