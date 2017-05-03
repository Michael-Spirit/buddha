from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from allauth.account.adapter import get_adapter
from allauth.utils import email_address_exists
from rest_framework import serializers, exceptions

from accounts.models import User


class UserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    balance = serializers.ReadOnlyField()
    passport_number = serializers.ReadOnlyField()
    is_staff = serializers.ReadOnlyField()
    is_manager = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name',  'last_name', 'balance',
                  'passport_number', 'is_staff', 'is_manager', 'is_active')


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    passport_number = serializers.CharField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise serializers.ValidationError(_("A user is already registered "
                                                "with this e-mail address."))
        return email

    def validate(self, attrs):
        passport_number = attrs['passport_number']
        if User.objects.filter(passport_number=passport_number).exists():
            raise serializers.ValidationError(
                _("A user is already registered with "
                  "this passport number address."))
        return attrs

    def get_cleaned_data(self):
        return {
            'email': self.validated_data.get('email', ''),
            'passport_number': self.validated_data.get('passport_number', '')
        }

    def create(self, validated_data):
        user = User.objects.create(**validated_data,
                                   status=User.STATUS_CHOICES.creating)

        mail_context = {
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        template_path = 'email/client_registered_mail.txt'
        send_mail(  # Mail to client
            subject=_('You have been registered in buddha application!'),
            message=render_to_string(template_path, mail_context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[validated_data['email']])

        mail_context = {
            'waiting': User.objects.filter(status='creating').count()
        }
        template_path = 'email/client_registered_mail_to_manager.txt'
        manager_mails = list(User.objects.filter(is_manager=True).\
                             values_list('email', flat=True))
        send_mail(  # Mail to managers
            subject=_('New client registered in buddha application!'),
            message=render_to_string(template_path, mail_context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=manager_mails)

        return user


class LoginSerializer(serializers.Serializer):
    pin = serializers.CharField(style={'input_type': 'password'})

    def _validate_pin(self, pin):
        if pin:
            user = authenticate(pin=pin)
        else:
            msg = _('Must include "pin".')
            raise exceptions.ValidationError(msg)

        return user

    def validate(self, attrs):
        pin = attrs.get('pin')

        try:
            user = User.objects.get(pin=pin)
            attrs['user'] = user
        except User.DoesNotExist:
            pass

        return attrs
