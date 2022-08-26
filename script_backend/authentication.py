import jwt
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from django.conf import settings
from rest_framework import exceptions


class SafeJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):

        User = get_user_model()
        authorization_heaader = request.headers.get('Authorization')

        if not authorization_heaader:
            raise exceptions.AuthenticationFailed('access_token is empty')
        try:
            # header = ''Token' token value'
            access_token = authorization_heaader.split(' ')[1]
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('access_token expired')
        except IndexError:
            raise exceptions.AuthenticationFailed('Token prefix missing')
        except jwt.InvalidSignatureError:
            raise exceptions.AuthenticationFailed('Token signature is not valid')

        user = User.objects.get(id=payload['user_id'])
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('user is inactive')
