from django.urls import path

from . import views


urlpatterns = [
    path('login/', views.user_login),
    path('logout/', views.logout_view),
    path('customers/create/', views.create_customer),
    path('customers/update/', views.update_customer),
    path('customers/read/', views.read_customer),
    path('customers/get_all/', views.get_all_customers),
    path('customers/delete/', views.delete_customer),
    path('meter/create/', views.create_meter),
    path('meter/read/', views.read_meter),
    path('bill/create/', views.create_billing),
    path('bill/read/', views.read_billing),
    path('receipt/create/', views.receipt),
    path('verifytoken/', views.verfyTokens),
    path('receipt/read/', views.read_receipt)
]

