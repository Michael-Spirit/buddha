from datetime import timedelta
from django.utils import timezone

from accounts.models import User
from accounts.tests.factories import UserFactory, ManagerFactory

from rest_framework.test import APITestCase
from rest_framework.reverse import reverse


class TestManagerAPI(APITestCase):

    def setUp(self):
        self.user = ManagerFactory()
        self.client.force_authenticate(user=self.user)

    def manager_get_all_users_and_filtered_users(self):
        usr1 = UserFactory(status=User.STATUS_CHOICES.creating)
        usr2 = UserFactory(status=User.STATUS_CHOICES.activated)
        usr3 = UserFactory(status=User.STATUS_CHOICES.closing)
        usr4 = UserFactory(status=User.STATUS_CHOICES.closed)

        url = reverse('accounts:users-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 4)
        self.assertContains(response, usr1.first_name)
        self.assertContains(response, usr2.first_name)
        self.assertContains(response, usr3.first_name)
        self.assertContains(response, usr4.first_name)

        data = {'status': User.STATUS_CHOICES.creating}
        response = self.client.get(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, usr1.first_name)

        data = {'status': User.STATUS_CHOICES.activated}
        response = self.client.get(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, usr2.first_name)

        data = {'status': User.STATUS_CHOICES.closing}
        response = self.client.get(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, usr3.first_name)

        data = {'status': User.STATUS_CHOICES.closed}
        response = self.client.get(url, data=data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, usr4.first_name)

    def test_not_manager_fail_to_use_users_list_api(self):
        usr = UserFactory()
        self.client.force_authenticate(user=usr)

        url = reverse('accounts:users-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_activate_creating_user(self):
        usr = UserFactory(status=User.STATUS_CHOICES.creating)

        self.assertEqual(usr.is_active, False)

        url = reverse('accounts:users-list')
        data = {'status': User.STATUS_CHOICES.creating}
        response = self.client.get(url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, usr.first_name)

        url = reverse('accounts:users-activate', kwargs={'pk': usr.pk})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 200)

        usr = User.objects.get(pk=usr.pk)
        self.assertEqual(usr.is_active, True)
        self.assertEqual(usr.status, User.STATUS_CHOICES.activated)

    def test_client_deactivate_himself(self):
        usr = UserFactory()
        self.client.force_authenticate(user=usr)

        url = reverse('accounts:users-deactivate')
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 200)

    def test_manager_confirm_deactivate_client_account(self):
        usr = UserFactory()
        self.client.force_authenticate(user=usr)

        url = reverse('accounts:users-deactivate')
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 200)

        self.client.force_authenticate(user=self.user)
        url = reverse('accounts:users-deactivate-confirm',
                      kwargs={'pk': usr.pk})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 200)

        usr = User.objects.get(pk=usr.pk)
        self.assertEqual(usr.status, User.STATUS_CHOICES.closed)

    def test_client_dont_have_perms_to_deactivate_confirm(self):
        usr = UserFactory()
        self.client.force_authenticate(user=usr)

        url = reverse('accounts:users-deactivate')
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 200)

        url = reverse('accounts:users-deactivate-confirm',
                      kwargs={'pk': usr.pk})
        response = self.client.patch(url)

        self.assertEqual(response.status_code, 403)

    def test_closed_clients_ordered_by_time_they_closed(self):
        usr1 = UserFactory(
            first_name='name1',
            status=User.STATUS_CHOICES.closed,
            status_changed=timezone.now() - timedelta(hours=48))
        usr4 = UserFactory(
            first_name='name4',
            status=User.STATUS_CHOICES.closed,
            status_changed=timezone.now() - timedelta(hours=12))
        usr2 = UserFactory(
            first_name='name2',
            status=User.STATUS_CHOICES.closed,
            status_changed=timezone.now() - timedelta(hours=36))
        usr3 = UserFactory(
            first_name='name3',
            status=User.STATUS_CHOICES.closed,
            status_changed=timezone.now() - timedelta(hours=24))

        data = {'status': User.STATUS_CHOICES.closed}
        url = reverse('accounts:users-list')
        response = self.client.get(url, data=data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['first_name'], usr1.first_name)
        self.assertEqual(response.data[1]['first_name'], usr4.first_name)
        self.assertEqual(response.data[2]['first_name'], usr2.first_name)
        self.assertEqual(response.data[3]['first_name'], usr3.first_name)
