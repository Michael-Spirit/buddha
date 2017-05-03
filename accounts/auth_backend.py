from django.contrib.auth.backends import ModelBackend

from accounts.models import User


class PinBackend(ModelBackend):

    def authenticate(self, **credentials):
        pin = credentials.get('pin')
        if pin:
            try:
                return User.objects.get(pin=pin)
            except User.DoesNotExist as error:
                raise error

        return None
