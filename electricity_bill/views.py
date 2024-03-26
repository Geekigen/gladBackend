from datetime import datetime, timedelta
import json

import jwt
from django.views.decorators.csrf import csrf_exempt

from electricity_management import settings
from .backend.apitokenhandler import handleToken
from .backend.validatejwt import authenticate_token

from .models import CustomUser, Meter, Bill, Receipt
from django.http import JsonResponse
from electricity_bill.backend.service_functions import Customer, MeterFxn, Billed, Paying, OAuth
from utils import clean_data
from django.contrib.auth import logout, authenticate, login


def bill_generator(request):
    try:
        data = request
        pass
    except Exception as e:
        print(e)


@csrf_exempt
def create_customer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method. Use POST'}, status=400)

    data = clean_data(request)
    response = Customer.customer_create(**data)
    return response


@csrf_exempt
@authenticate_token
def update_customer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method. Use POST'}, status=400)

    data = clean_data(request)
    response = Customer.customer_update(**data)
    return response


@csrf_exempt
@authenticate_token
def read_customer(request):
    data = clean_data(request)
    response = Customer.customer_read(id_no=data.get('id_no'))
    return response


@csrf_exempt
@authenticate_token
def get_all_customers(request):
    response = Customer.get_all_customers(request)
    return response


@csrf_exempt
@authenticate_token
def delete_customer(request):
    data = clean_data(request)
    response = Customer.customer_delete(**data)
    return response


@authenticate_token
@csrf_exempt
def create_meter(request):
    data = clean_data(request)
    response = MeterFxn.meter_create(**data)
    return response


@authenticate_token
@csrf_exempt
def read_meter(request):
    data = clean_data(request)
    response = MeterFxn.meter_read(**data)
    return response


@csrf_exempt
@authenticate_token
def create_billing(request):
    data = clean_data(request)
    response = Billed.create_bill(**data)
    return response


@csrf_exempt
@authenticate_token
def read_billing(request):
    data = clean_data(request)
    response = Billed.read_bill(**data)
    return response


@csrf_exempt
@authenticate_token
def receipt(request):
    data = clean_data(request)
    response = Paying.generate_receipt(**data)
    return response


@csrf_exempt
@authenticate_token
def read_receipt(request):
    data = clean_data(request)
    response = Paying.read_receipt(**data)
    return response


@csrf_exempt
def user_login(request):
    data = json.loads(request.body)
    username = data.get('username')
    password = data.get('password')
    if not all([username, password]):
        return JsonResponse({'status': 'Missing username or password'}, status=400)
    user = CustomUser.objects.get(username=username)
    if user is None:
        return JsonResponse({'status': 'Invalid credentials'}, status=400)

    login(request, user)

    payload = {
        'user_id': user.id_no,
        'exp': datetime.now() + timedelta(minutes=settings.JWT_EXP),
        'iat': datetime.now()
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    user = {'id': user.id_no,
            'username': user.username,
            'email': user.email,
            'phone': user.contact_no,
            'role': user.role.name,
            'status': user.status.name}

    return JsonResponse({'token': token, 'user': user, 'code': '200', 'message': 'Login successful'})


def logout_view(request):
    try:
        response_data = OAuth.logout_user(request)
        return JsonResponse({"message": response_data})
    except Exception as ex:
        print(ex)
        response_data = {'error': 'logout error'}
        return JsonResponse(response_data)


@csrf_exempt
def verfyTokens(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get('token')
        response = handleToken(token)
        return response
    else:
        return JsonResponse({"Message": 'invalid request '})
