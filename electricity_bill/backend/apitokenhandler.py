import jwt
from datetime import datetime, timedelta

from django.http import JsonResponse

from electricity_management import settings


def handleToken(token):
    try:
        print("token in")
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
        print("token processed")
        user_id = payload['user_id']
        print(user_id)
        payload = {
            'user_id': user_id,
            'exp': datetime.now() + timedelta(minutes=settings.JWT_EXP),
            'iat': datetime.now()
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
        newToken = token
        json_response = JsonResponse({"code": "200.000.000", "message": "success"},
                                     status=200)
        json_response.set_cookie('token', newToken, httponly=True)
        return JsonResponse({"token": newToken}, status=200)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Token expired. Kindly login."}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Invalid token. Try logging in."}, status=401)




