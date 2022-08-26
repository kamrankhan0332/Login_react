from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response

from script_backend.authentication import SafeJWTAuthentication
from .models import Users
from rest_framework import exceptions, status
import datetime
import jwt
from django.conf import settings


def generate_access_token(user):
    access_token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=4),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_token_payload,
                              settings.SECRET_KEY, algorithm='HS256')
    return access_token


def generate_refresh_token(user):
    refresh_token_payload = {
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    refresh_token = jwt.encode(refresh_token_payload, settings.REFRESH_TOKEN_SECRET, algorithm='HS256')
    return refresh_token


@api_view(['POST'])
def login_view(request):
    email = request.data.get('email')
    password = request.data.get('password')
    response = Response()
    if (email is None) or (password is None):
        raise exceptions.AuthenticationFailed(
            'email and password required')

    user = Users.objects.get(email=email)
    if user is None:
        raise exceptions.AuthenticationFailed('user not found')
    if not user.check_password(password):
        raise exceptions.AuthenticationFailed('wrong password')

    access_token = generate_access_token(user)
    refresh_token = generate_refresh_token(user)
    # response.set_cookie(key='refreshtoken', value=refresh_token, httponly=True)
    response.data = {
        'token': refresh_token,
        'access_token': access_token,
        'user': user.id,
    }
    print('cookies')
    print(response.cookies)
    return Response({'data': response.data}, status=status.HTTP_200_OK)


@api_view(['POST'])
def refresh_token_view(request):
    refresh_token = request.data.get('refreshtoken')
    if refresh_token == 'None':
        raise exceptions.AuthenticationFailed(
            'PLease login')
    try:
        payload = jwt.decode(
            refresh_token, settings.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise exceptions.AuthenticationFailed(
            'expired refresh token, please login again.')

    user = Users.objects.get(id=payload.get('user_id'))
    if user is None:
        raise exceptions.AuthenticationFailed('User not found')

    if not user.is_active:
        raise exceptions.AuthenticationFailed('user is inactive')

    access_token = generate_access_token(user)
    return Response({'access_token': access_token})


@api_view(['POST'])
def logout_view(request):
    response = Response()
    response.set_cookie(key='refreshtoken', value=None, httponly=True)
    response.data = {
        'access_token': '',
        'user': '',
    }
    return response


@api_view(['POST'])
def sign_up(request):
    try:
        if request.method == 'POST':
            data = request.data['value']
            user = Users.objects.create(username=data['username'], email=data['email'])
            user.set_password(data['password'])
            user.save()
            return Response({"Response": "User has been created"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([SafeJWTAuthentication])
def change_password(request):
    try:
        print(request.data.get('access_token'))
        print(request.data.get('token'))
        email = request.data.get('email')
        password = request.data.get('password')
        if (email is None) or (password is None):
            raise exceptions.AuthenticationFailed(
                'username and password required')
        user_data = Users.objects.get(email=email)
        user_data.set_password(password)
        user_data.save()
        return Response({"Response": "Password has been changed"}, status=status.HTTP_200_OK)
    except Exception as e:
        print(str(e))
        return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



