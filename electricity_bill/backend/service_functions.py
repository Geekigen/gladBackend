import datetime
import json

import jwt
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

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
                return {"response_status": "error", "message": "Missing required fields"}

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
            return {"response_status": "success", "code": "200", "data": data}

        except Exception as e:
            print(e)
            return {"response_status": "error", "data": "Error creating customer"}

    def customer_read(**kwargs):
        try:
            id_no = kwargs.get('id_no')
            customer = CustomUser.objects.get(id_no=id_no)
            data = {"first_name": customer.first_name,
                    'last_name': customer.last_name,
                    'address': customer.address,
                    'contact_no': customer.contact_no,
                    'role': customer.role.name,
                    'status': customer.status.name,
                    }
            return {"message": data}
        except Exception as ex:
            print(ex)
        return {'message': "invalid"}

    def customer_delete(**kwargs):
        try:
            id_no = kwargs.get('id_no')
            if not id_no:
                return {"message": 'invalid customer'}
            customer = CustomUser.objects.filter(id_no=kwargs.get('id_no'))
            if customer:
                customer.delete()
                return {"message": 'successfully deleted'}
            else:
                return {"message": 'invalid customer'}

        except Exception as ex:
            print(ex)
        return {'message': 'invalid'}

    def customer_update(**kwargs):
        try:
            id_no = kwargs.get('id_no')
            if not id_no:
                return {'message': 'invalid input'}
            customer = CustomUser.objects.get(id_no=id_no)
            if not customer:
                return {'message': 'invalid customer'}
            CustomUser.objects.filter(id_no=id_no).update(**kwargs)
            return {'message': 'successfully updated'}
        except Exception as ex:
            print(ex)
        return {'message': 'invalid input'}

    def get_all_customers(self):
        try:
            customer = CustomUser.objects.all().values("id_no", "first_name", "last_name", "contact_no")
            if customer is None:
                return {'message': 'No Customer'}

            all_customers = list(customer)

            return {"message": all_customers}
        except Exception as ex:
            print(ex)
        return {'message': "invalid"}


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
            return {'message': 'meter number created successfully'}
        except Exception as ex:
            print(ex)
        return {'message': 'Invalid input'}

    def meter_read(**kwargs):
        try:
            meter_no = kwargs.get('meter_no')
            meter = Meter.objects.get(meter_no=meter_no)
            if meter:
                return {"message": meter}
        except Exception as e:
            print(e)
        return {'message': 'invalid input'}


class Billed:

    def create_bill(**kwargs):
        try:
            customer_id = kwargs.get('id_no')
            customer = CustomUser.objects.get(id_no=customer_id)
            meter = Meter.objects.filter(customer=customer).first()  # TODO: START HERE\

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

                if not bill:
                    return "Bill not created"

                return f"Bill: {bill} Created Successfully"
        except Exception as e:
            print(e)
        return {'message': 'invalid'}

    def read_bill(**kwargs):
        meter_no = kwargs.get('meter_no')
        bill = Bill.objects.filter(meter__meter_no=meter_no).first()
        try:
            if not bill:
                return {'message': "Bill not found"}

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
            return {'message': data_bill}
        except Exception as ex:
            print(ex)
        return {'message': 'invalid'}

    def generate_bill(**data):
        # TODO: Add exception handling
        # TODO: Rewrite Bill table model. Have only one reading field
        # TODO: Consequently review ALL Bill methods
        current_reading = data.get('current_reading')
        previous_reading = data.get('previous_reading')
        unit_cost = 25
        meter = data.get('meter')
        units = current_reading - previous_reading
        total_cost = units * unit_cost
        return total_cost


class Paying:

    def generate_receipt(**kwargs):
        print("huhuh")
        try:
            bill_id = kwargs.get('bill_id')
            bill = Bill.objects.get(uuid=bill_id)
            payment_date = datetime.datetime.now()
            print(bill)
            if not bill:
                return {'message': "bill not existing"}
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
            print(receipt_info)
            receipt = Receipt.objects.create(**receipt_information)
            print(receipt)
            return {'message': receipt_info}
        except Exception as e:
            print(e)
        return {'message': 'Invalid'}

    def read_receipt(**kwargs):
        transaction_id = kwargs.get('transaction_id')
        pay = Receipt.objects.filter(transaction_id=transaction_id).first()
        if pay:
            try:
                pay_info = {
                    'balance': pay.balance,
                    'payment_date': pay.payment_date,
                    ' payment_method_used': Receipt.payment_method_used
                }
                return {'message': pay_info}
            except Exception as e:
                print(e)
            return {'message': 'invalid'}


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
            'user_id': user.id,  # Use user ID instead of UUID for JWT standard
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
