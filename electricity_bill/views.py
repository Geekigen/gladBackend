from datetime import datetime, timedelta
import json

<<<<<<< HEAD
import jwt
=======
from django.contrib.auth.decorators import login_required
>>>>>>> 90d5c653b84b484cb90c70693a28f63a1791c4f5
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

<<<<<<< HEAD
    try:
        data = clean_data(request)
        customer_data = Customer.customer_create(**data)
        return JsonResponse({"response_status": "success", "code": 200, "data": customer_data})

=======
        # if request.user.is_authenticated:
        data = clean_data(request)
        return JsonResponse({Customer.customer_create(**data)})
        # else:
        # return JsonResponse({"error": "login required", "code": "401"})
>>>>>>> 90d5c653b84b484cb90c70693a28f63a1791c4f5
    except Exception as e:
        print(e)
        return JsonResponse({"error": "Error creating customer"}, status=400)


def update_customer(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method. Use POST'}, status=400)

    try:
        data = clean_data(request)
        customer_data = Customer.customer_update(**data)
        return JsonResponse({"response_status": "success", "code": 200, "data": customer_data})

    except Exception as e:
        print(e)
        return JsonResponse({"error": "Error creating customer"}, status=400)


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

<<<<<<< HEAD
@authenticate_token
=======

@csrf_exempt
>>>>>>> 90d5c653b84b484cb90c70693a28f63a1791c4f5
def create_meter(request):
    data = clean_data(request)
    response = MeterFxn.meter_create(**data)
    return response


@csrf_exempt
def read_meter(request):
    data = clean_data(request)
    response = MeterFxn.meter_read(**data)
    return response


@csrf_exempt
def create_billing(request):
    data = clean_data(request)
    response = Billed.create_bill(**data)
    return response


@csrf_exempt
def read_billing(request):
    data = clean_data(request)
    response = Billed.read_bill(**data)
    return response


@csrf_exempt
def receipt(request):
    data = clean_data(request)
    response = Paying.generate_receipt(**data)
    return response


def read_receipt(request):

        data = clean_data(request)
        response = Paying.read_receipt(**data)
        return response



@csrf_exempt
def user_login(request):
    data = json.loads(request.body)
    print(data)
    username = data.get('username')
    password = data.get('password')

    if not all([username, password]):
        return JsonResponse({'status': 'Missing username or password'}, status=400)
    user = CustomUser.objects.get(username=username)
    print(user)

    print(user)
    if user is None:
        return JsonResponse({'status': 'Invalid credentials'}, status=400)

    login(request, user)

    payload = {
        'user_id': user.username,
        'exp': datetime.now() + timedelta(minutes=settings.JWT_EXP),
        'iat': datetime.now()
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return JsonResponse({'message': 'logged in', 'token': token})


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
