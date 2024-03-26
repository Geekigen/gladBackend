import datetime
import json
import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from electricity_management import settings
from ..models import Bill, Meter, Role, Status, CustomUser, Receipt
from django.contrib.auth import authenticate, login, logout


# from electricity_bill.models import Role,Status,CustomUser


class Customer:
    def customer_create(**kwargs):
        try:
            role = kwargs.get('role')
            status = kwargs.get('status')
            if not all([role, status, kwargs.get('username'), kwargs.get('password')]):
                return JsonResponse({'message': 'Missing required fields', 'code': '400'})

            # Get role and status objects (avoid redundant lookups)
            role_obj = get_object_or_404(Role, name=role)
            status_obj = get_object_or_404(Status, name=status)

            new_user = CustomUser.objects.create(
                id_no=kwargs.get('id_no', ''),
                first_name=kwargs.get('first_name', ''),
                username=kwargs.get('username', ''),
                last_name=kwargs.get('last_name', ''),
                address=kwargs.get('address', ''),
                contact_no=kwargs.get('contact_no', ''),
                role=role_obj,
                status=status_obj,
                password=kwargs.get('password')
            )

            # Return success response with user data
            data = {
                "uuid": new_user.uuid,
                "id_no": new_user.id_no,
                "first_name": new_user.first_name,
                "username": new_user.username,
                "last_name": new_user.last_name,
                "address": new_user.address,
                "contact_no": new_user.contact_no,
                "role": role,  # Include role and status names
                "status": status,
            }
            return JsonResponse({'response_status': 'success', 'data': data,"code":"201"})

        except Exception as e:
            return JsonResponse({'message': 'Error occurred while creating customer', 'code': '500'})

    def customer_read(**kwargs):
        try:
            id_no = kwargs.get('id_no')
            customer = CustomUser.objects.get(id_no=id_no)
            if not customer:
                return JsonResponse({'message': 'Customer not found', 'code': '404'})
            data = {"first_name": customer.first_name,
                    'last_name': customer.last_name,
                    'address': customer.address,
                    'contact_no': customer.contact_no,
                    'role': customer.role.name,
                    'status': customer.status.name,
                    }
            return JsonResponse({'data': data})
        except Exception as ex:
            return JsonResponse({'message': "Invalid Id", 'code': '500'})

    def customer_delete(**kwargs):
        try:
            id_no = kwargs.get('id_no')
            if not id_no:
                return JsonResponse({'message': 'Invalid is required', 'code': '400'})
            customer = CustomUser.objects.filter(id_no=kwargs.get('id_no'))
            if not customer:
                return JsonResponse({'message': 'Customer not found', 'code': '404'})

            customer.delete()
            return JsonResponse({'message': 'Customer deleted successfully', 'code': '200'})
        except Exception as ex:
            return JsonResponse({'message': 'Error Occurred', 'code': '500'})

    def customer_update(**kwargs):
        try:
            id_no = kwargs.get('id_no')
            if not id_no:
                return JsonResponse({'message': 'Invalid is required', 'code': '400'})
            customer = CustomUser.objects.get(id_no=id_no)
            if not customer:
                return JsonResponse({'message': 'Customer not found', 'code': '404'})
            kwargs.pop('token')
            CustomUser.objects.filter(id_no=id_no).update(**kwargs)
            return JsonResponse({'message': 'Customer updated successfully', 'code': '200'})
        except Exception as ex:
            return JsonResponse({'message': 'Error Occurred', 'code': '500'})

    def get_all_customers(self):
        try:
            customers = CustomUser.objects.all().values("id_no", "first_name", "last_name", "contact_no", "address",
                                                        "status__name", "role__name")
            if customers is None:
                return JsonResponse({'message': 'No customers found', 'code': '404'})

            all_customers = list(customers)

            return JsonResponse({'data': all_customers, 'code': '200'})
        except Exception as ex:
            print("This is the Error", str(ex))
            return JsonResponse({'message': 'Error occurred while fetching customers', 'code': '500'})


class MeterFxn:

    def meter_create(**kwargs):
        try:
            meter_count = Meter.objects.count()
            meter_no = meter_count + 1

            meter_info = {
                'customer': CustomUser.objects.get(id_no=kwargs.get('id_no')),
                'meter_no': meter_no
            }
            Meter.objects.create(**meter_info)
            return JsonResponse({'message': 'Meter created successfully', 'code': '201'})
        except Exception as ex:

            return JsonResponse({'error': 'Error occurred while creating meter', 'code': '500'})

    def meter_read(**kwargs):
        try:
            meter_no = int(kwargs.get('meter_no'))
            meter = Meter.objects.get(meter_no=meter_no)
            if meter:
                data = {
                    "customer": meter.customer.id_no,
                    "meter_no": meter.meter_no,
                    "installation_date": meter.installation_date
                }
                return JsonResponse({'data': data, 'code': '200'})
            else:
                return JsonResponse({'message': 'Meter not found', 'code': '404'})
        except Exception as e:
            return JsonResponse({'error': 'Error occurred while reading meter', 'code': '500'})


class Billed:

    def create_bill(**kwargs):
        try:
            customer_id = kwargs.get('id_no')
            customer = CustomUser.objects.get(id_no=customer_id)
            meter = Meter.objects.filter(customer=customer).first()

            if meter:
                bill_info = {
                    "meter": meter,
                    "current_reading": kwargs.get('current_reading'),
                    'previous_reading': kwargs.get('previous_reading'),
                    'due_date': kwargs.get('due_date'),
                    'payment_method': kwargs.get('payment_method')
                }
                bill_info["amount_paid"] = Billed.generate_bill(**bill_info)
                bill = Bill.objects.create(**bill_info)
                bill.save()

                if not bill:
                    return JsonResponse({'message': 'Bill not created', 'code': '404'})
                return JsonResponse({'message': 'Bill created successfully', 'code': '201'})
            else:
                return JsonResponse({'message': 'Meter not found', 'code': '404'})
        except Exception as e:
            print("********", str(e))
            return JsonResponse({'error': 'Error occurred while creating bill', 'code': '500'})

    def read_bill(**kwargs):
        meter_no = kwargs.get('meter_no')
        if not meter_no:
            return JsonResponse({'message': 'meter_no is required', 'code': '400'})

        try:
            meter = Meter.objects.filter(meter_no=meter_no).first()
            if not meter:
                return JsonResponse({'message': 'Meter not found', 'code': '404'})
            bill = Bill.objects.filter(meter=meter).first()

            if not bill:
                return JsonResponse({'message': 'Bill not found', 'code': '404'})

            data_bill = {"id_no": bill.meter.customer.id_no,
                         "first_name": bill.meter.customer.first_name,
                         "last_name": bill.meter.customer.last_name,
                         "address": bill.meter.customer.address,
                         "contacts_no": bill.meter.customer.contact_no,
                         "role": bill.meter.customer.role.name,
                         "status": bill.meter.customer.status.name,
                         "reading_date": bill.reading_date,
                         "previous_reading": bill.current_reading,
                         "billing_date": bill.billing_date,
                         "amount_paid": bill.amount_paid,
                         "due_date": bill.due_date,
                         "payment_method": bill.payment_method
                         }
            return JsonResponse({'data': data_bill, 'code': '200'})

        except Exception as ex:
            return JsonResponse({'message': 'Error occurred while reading bill', 'code': '500'})

    def generate_bill(**data):
        # TODO: Add exception handling
        # TODO: Rewrite Bill table model. Have only one reading field
        # TODO: Consequently review ALL Bill methods
        current_reading = data.get('current_reading')
        previous_reading = data.get('previous_reading')
        unit_cost = 25
        meter = data.get('meter')
        units = int(current_reading) - int(previous_reading)
        total_cost = units * unit_cost
        return total_cost


class Paying:

    def generate_receipt(**kwargs):
        try:
            bill_id = kwargs.get('bill_id')
            bill = Bill.objects.get(uuid=bill_id)
            payment_date = datetime.datetime.now()
            if not bill:
                return JsonResponse({'message': 'Bill not found', 'code': '404'})
            receipt_information = {

                "bill": bill,
                "payment_method_used": bill.payment_method,
                "amount_paid": bill.amount_paid,
                "payment_date": payment_date,
                "status": Status.objects.get(name="Paid")

            }

            receipt_info = {
                "first_name": bill.meter.customer.first_name,
                "last_name": bill.meter.customer.last_name,
                "address": bill.meter.customer.address,
                "contact_no": bill.meter.customer.contact_no,
                "meter": bill.meter.meter_no,
                "payment_method_used": bill.payment_method,
                "amount_paid": bill.amount_paid,
                "payment_date": payment_date,
                "status": Status.objects.get(name="Paid").name
            }
            receipt = Receipt.objects.create(**receipt_information)

            if not receipt:
                return JsonResponse({'message': 'Receipt not created', 'code': '404'})
            return JsonResponse({'data': receipt_info, 'code': '201'})
        except Exception as e:
            return JsonResponse({'error': 'Error occurred while creating receipt', 'code': '500'})

    def read_receipt(**kwargs):
        try:

            bill_id = kwargs.get('bill_id')
            bill = Bill.objects.get(uuid=bill_id)
            if not bill:
                return JsonResponse({'message': 'Bill not found', 'code': '404'})
            pay = Receipt.objects.filter(bill_id=bill).first()
            bill_data = {
                "first_name": bill.meter.customer.first_name,
                "last_name": bill.meter.customer.last_name,
                "address": bill.meter.customer.address,
                "contact_no": bill.meter.customer.contact_no,
                "meter": bill.meter.meter_no,
                "payment_method_used": bill.payment_method,
                "amount_paid": bill.amount_paid,
                "payment_date": bill.billing_date,

            }
            if not pay:
                return JsonResponse({'message': 'Receipt not found', 'code': '404'})

            pay_info = {
                'balance': pay.amount_paid,
                'payment_date': pay.payment_date,
                'payment_method_used': pay.payment_method_used,
                'bill': bill_data,
                'status': pay.status.name

            }
            return JsonResponse({'data': pay_info, 'code': '200'})
        except Exception as e:
            return JsonResponse({'error': 'Error occurred while reading receipt', 'code': '500'})


class OAuth:
    @staticmethod
    def user_login(request):
        if request.method != 'POST':
            return {'error': 'Invalid request method. Use POST'}

        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not all([username, password]):
                return {'error': 'Missing username or password'}

            user = authenticate(request, username=username, password=password)

            if user is None:
                raise ObjectDoesNotExist('Invalid username or password')

        except ObjectDoesNotExist as e:
            print(e)
            return {'status': 'Invalid credentials', 'code': '401'}

        except Exception as e:
            print(e)
            return {'error': 'An error occurred during login', 'code': '401'}

        login(request, user)

        payload = {
            'user_id': user.id_no,  # Use user ID instead of UUID for JWT standard
            'exp': datetime.now() + datetime.timedelta(minutes=settings.JWT_EXP),
            'iat': datetime.now()
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

        return ({'message': 'logged in', 'Token': token})

    @staticmethod
    def logout_user(request):
        try:
            logout(request)
            return {'message': 'logged out'}
        except Exception as ex:
            print(ex)
            return {"message": "repeat"}
