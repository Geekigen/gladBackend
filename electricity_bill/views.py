import datetime
import json

from django.contrib.auth.decorators import login_required

#

from .models import CustomUser, Meter, Bill, Receipt
from django.http import JsonResponse
from electricity_bill.backend.service_functions import Customer, MeterFxn, Billed, Paying, OAuth
from utils import clean_data
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.models import User


# Create your views here.


def bill_generator(request):
    try:
        data = request
        pass
    except Exception as e:
        print(e)


def create_customer(request):
    try:

        #if request.user.is_authenticated:
        data = clean_data(request)
        return JsonResponse({Customer.customer_create(**data)})
        #else:
           # return JsonResponse({"error": "login required", "code": "401"})
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Error occured while creating"})


def update_customer(request):
    try:
        data = clean_data(request)
        return JsonResponse(Customer.customer_update(**data))
    except Exception as ex:
        print(ex)
    return JsonResponse({"message": "invalid user"})


def read_customer(request):
    try:
        data = clean_data(request)
        customer = Customer.customer_read(id_no=data.get('id_no'))
        return JsonResponse({'customer data': customer})
    except Exception as y:
        print(y)
    return JsonResponse({'customer data': 'Invalid'})


def get_all_customers(request):
    try:
        customers = Customer.get_all_customers(request)
        print(customers)
        return JsonResponse({'data': customers})
    except Exception as y:
        print(y)
    return JsonResponse({'customer data': 'Invalid'})


def delete_customer(request):
    try:
        data = clean_data(request)
        customer = Customer.customer_delete(**data)
        return JsonResponse({'message': 'Customer deleted successfully'})
    except Exception as ex:
        print(ex)
    return JsonResponse({'message': 'Try again'})


def create_meter(request):
    try:
        data = clean_data(request)

        return JsonResponse({'message': MeterFxn.meter_create(**data)})
    except Exception as ex:
        print(ex)
    return JsonResponse({'message': 'Unsuccessfully generated'})


def read_meter(request):
    try:
        data = clean_data(request)
        meter = MeterFxn.meter_read(meter_no=data.get(meter_no='meter_no'))
        return JsonResponse({"message": meter})
    except Exception as ex:
        print(ex)
    return JsonResponse({"message": "invalid"})


def create_billing(request):
    try:
        data = clean_data(request)
        return JsonResponse({'message': Billed.create_bill(**data)})
    except Exception as ex:
        print(ex)
        return JsonResponse({'message': 'Unsuccessfully billed'})


def read_billing(request):
    try:
        data = clean_data(request)
        return JsonResponse(Billed.read_bill(**data))
    except Exception as e:
        print(e)
    return JsonResponse({"message": "invalid"})


def receipt(request):
    try:
        data = clean_data(request)
        return JsonResponse(Paying.generate_receipt(**data))
    except Exception as ex:
        print(ex)
    return JsonResponse({'message': 'Unsuccessfully'})


def read_receipt(request):
    try:

        data = clean_data(request)
        payments = Paying.object.get(payment=data.get('transaction_id'))
        return JsonResponse({"message": payments})
    except Exception as ex:
        print(ex)
    return JsonResponse({'message': 'invalid'})


def user_login(request):
    try:
        response_data = OAuth.user_login(request)
    except Exception as ex:
        print(ex)
        response_data = {'error': 'login_error'}
    return JsonResponse(response_data)


def logout_view(request):
    try:
        response_data = OAuth.logout_user(request)
        return JsonResponse({"message":response_data})
    except Exception as ex:
        print(ex)
        response_data = {'error': 'logout error'}
        return JsonResponse(response_data)
