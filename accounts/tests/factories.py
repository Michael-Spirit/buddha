import factory
from datetime import timedelta
from django.utils import timezone
from factory import fuzzy

from accounts.models import User


TEST_PASSWORD = 'password'


class UserFactory(factory.django.DjangoModelFactory):
    email = factory.Sequence(lambda n: 'user%s@example.com' % n)
    password = factory.PostGenerationMethodCall('set_password', TEST_PASSWORD)
    pin = factory.Faker('password')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    passport_number = factory.Faker('password')
    status = fuzzy.FuzzyChoice(status[0] for status in User.STATUS_CHOICES)
    status_changed = fuzzy.FuzzyDateTime(timezone.now() - timedelta(hours=48))
    is_staff = False
    is_manager = False
    is_active = False

    class Meta:
        model = User
        django_get_or_create = ('email',)


class ManagerFactory(UserFactory):
    email = 'manager@buddha.com'
    is_manager = True
    is_active = True


class AdminFactory(ManagerFactory):
    email = 'admin@admin.com'
    is_superuser = True
