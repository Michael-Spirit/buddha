from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import (
    AbstractBaseUser, PermissionsMixin, BaseUserManager)
from model_utils import Choices


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    STATUS_CHOICES = Choices(
        ('creating', 'creating', _('creating')),
        ('activated', 'activated', _('activated')),
        ('closing', 'closing', _('closing')),
        ('closed', 'closed', _('closed')),
    )

    email = models.EmailField(_('email address'), unique=True)
    password = models.CharField(
        _('password'), max_length=128, null=True, blank=True)
    pin = models.CharField(_('pin code'), max_length=10, blank=True, null=True)
    balance = models.IntegerField(_('account balance'), default=0)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    passport_number = models.CharField(
        _('passport number'), max_length=8, null=True, blank=True)
    status = models.CharField(
        _('account status'), max_length=10, blank=True, null=True)
    status_changed = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_manager = models.BooleanField(_('manager status'), default=False)
    is_active = models.BooleanField(_('active status'), default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    PERSONAL_INFO_FIELDS = ['first_name', 'last_name', 'passport_number']

    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_short_name(self):
        return self.get_full_name()
