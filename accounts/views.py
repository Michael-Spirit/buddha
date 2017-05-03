import string
from factory.fuzzy import FuzzyText

from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from rest_framework.response import Response
from rest_framework import status, viewsets, mixins
from rest_auth.views import LoginView as BaseLoginView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import list_route, detail_route
from rest_auth.registration.urls import RegisterView as BaseRegisterView

from accounts.models import User
from accounts.permissions import IsManager
from accounts.serializers import (
    UserSerializer,
    RegisterSerializer,
    LoginSerializer
)


class RegisterView(BaseRegisterView):
    """
    API call to register new client
    
    Required fields: email, first_name, last_name, passport_number
    """
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginView(BaseLoginView):
    """
    API cal for login
    
    Required field: pin code 
    (pin code generated when manager activate client account)
    """
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        if not User.objects.filter(pin=request.data['pin']).exists():
            return Response({"detail": _("User with this pin does not exist")},
                            status=status.HTTP_404_NOT_FOUND)

        return super().post(request, *args, **kwargs)

    def process_login(self):
        authenticate(pin=self.request.data['pin'])


class UserAPI(mixins.RetrieveModelMixin,
              mixins.ListModelMixin,
              viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (IsManager, )

    def get_queryset(self):
        return User.objects.filter(is_manager=False)

    def filter_queryset(self, queryset):
        queryset = self.get_queryset()
        if self.request.method == 'GET':
            if 'status' in self.request.query_params:
                status = self.request.query_params['status']
                queryset = queryset.filter(status=status)

                if status == 'closed':
                    queryset = queryset.order_by('status_changed')

        return queryset

    def list(self, request, *args, **kwargs):
        """
        API call for client list
        
        :query_param client status (creating, activated, closing, closed)
        """
        queryset = self.filter_queryset(self.queryset)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        API call for account detail
        """
        return super().retrieve(request, *args, **kwargs)

    @detail_route(methods=['PATCH'], permission_classes=[IsManager])
    def activate(self, request, pk=None):
        """
        API call for activate new client
        After activation will sen email to client with generated pin
        
        :param pk: Client id what will be activated
        """
        user = self.get_queryset().get(pk=pk)
        user.is_active = True
        user.status = User.STATUS_CHOICES.activated
        user.status_changed = timezone.now()
        user.pin = FuzzyText(length=15, chars=string.digits).fuzz()

        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        mail_context = {
            'pin': user.pin,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        template_path = 'email/client_account_have_been_activated.txt'
        manager_mails = list(User.objects.filter(is_manager=True).
                             values_list('email', flat=True))
        send_mail(  # Mail pin to client
            subject=_('Your account approved in buddha application!'),
            message=render_to_string(template_path, mail_context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=manager_mails)

        return Response(serializer.data)

    @list_route(methods=['PATCH'], permission_classes=[IsAuthenticated])
    def deactivate(self, request):
        """
        API call for client to deactivate his account. 
        Client can deactivate only himself (must be logged in)
        """
        self.request.user.status = User.STATUS_CHOICES.closing
        self.request.user.status_changed = timezone.now()
        self.request.user.is_active = False

        serializer = self.get_serializer(
            instance=self.request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @detail_route(methods=['PATCH'], permission_classes=[IsManager])
    def deactivate_confirm(self, request, pk=None):
        """
        API call for confirm user deactivation account
        :param pk: pk=id for user with closing status
        """
        user = self.get_queryset().get(pk=pk)
        user.status = User.STATUS_CHOICES.closed
        user.status_changed = timezone.now()

        serializer = self.get_serializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
