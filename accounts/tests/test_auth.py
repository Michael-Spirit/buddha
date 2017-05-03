from django.core import mail

from accounts.models import User
from accounts.tests.factories import UserFactory, ManagerFactory

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse


class UserAuthTestCase(APITestCase):

    def test_successful_register(self):
        data = {
            'first_name': 'Michael',
            'last_name': 'Spirit',
            'email': 'user@example.com',
            'passport_number': 'BH404'
        }

        url = reverse('accounts:register')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 201)

    def test_just_registered_user_have_status_creating(self):
        data = {
            'first_name': 'Michael',
            'last_name': 'Spirit',
            'email': 'user@example.com',
            'passport_number': 'BH404'
        }

        url = reverse('accounts:register')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 201)

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(
            User.objects.first().status, User.STATUS_CHOICES.creating)

    def test_email_not_unique_register(self):
        data = {
            'first_name': 'Michael',
            'last_name': 'Spirit',
            'email': 'user@example.com',
            'passport_number': 'BH404'
        }
        data2 = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'user@example.com',
            'passport_number': 'BH201'
        }

        url = reverse('accounts:register')
        self.client.post(url, data=data, format='json')
        response = self.client.post(url, data=data2, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['email'],
            ['A user is already registered with this e-mail address.'])

    def test_passport_number_not_unique_register(self):
        data = {
            'first_name': 'Michael',
            'last_name': 'Spirit',
            'email': 'user@example.com',
            'passport_number': 'BH400'
        }
        data2 = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'user2@example.com',
            'passport_number': 'BH400'
        }

        url = reverse('accounts:register')
        self.client.post(url, data=data, format='json')
        response = self.client.post(url, data=data2, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['non_field_errors'],
                         ['A user is already registered with '
                          'this passport number address.'])

    def test_successful_login(self):
        user = UserFactory(pin='PIN111', is_active=True)

        data = {'pin': user.pin}
        url = reverse('accounts:login')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 200)

    def test_fail_login_bad_pin(self):
        UserFactory(pin='PIN111', is_active=True)

        data = {'pin': 'PIN222'}
        url = reverse('accounts:login')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.data['detail'], 'User with this pin does not exist')

    def test_after_user_registration_client_and_manager_receive_mails(self):
        self.user = ManagerFactory()
        self.client.force_authenticate(user=self.user)

        data = {
            'first_name': 'Michael',
            'last_name': 'Spirit',
            'email': 'user@example.com',
            'passport_number': 'BH404'
        }

        url = reverse('accounts:register')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(mail.outbox), 2)

        self.assertIn(data['first_name'], mail.outbox[0].body)
        self.assertIn(data['last_name'], mail.outbox[0].body)

        self.assertIn(self.user.email, mail.outbox[1].recipients())

    def test_new_user_generated_pin_and_mail_after_manager_confiramtion(self):
        data = {
            'first_name': 'Michael',
            'last_name': 'Spirit',
            'email': 'user@example.com',
            'passport_number': 'BH404'
        }

        url = reverse('accounts:register')
        response = self.client.post(url, data=data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

        usr = User.objects.get(email='user@example.com')
        self.assertIsNone(usr.pin)

        self.user = ManagerFactory()
        self.client.force_authenticate(user=self.user)

        url = reverse('accounts:users-activate', kwargs={'pk': usr.pk})
        self.client.patch(url)

        usr = User.objects.get(email='user@example.com')
        self.assertIsNotNone(usr.pin)

        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(usr.pin, mail.outbox[1].body)
