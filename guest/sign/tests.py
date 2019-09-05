from django.test import TestCase

# Create your tests here.

'''
python manage.py test
python manage.py test sign
python manage.py test sign.tests
python manage.py test sign.tests.ModelTest
python manage.py test sign.tests.ModelTest.test_event_models
python manage.py test -p test*.py
'''
from django.test import TestCase
from sign.models import Event, Guest
from django.contrib.auth.models import User


class ModelTest(TestCase):
    def setUp(self):
        Event.objects.create(id=1, name='一加3 发布会', status=True, limit=2000, address='深圳',
                             start_time='2016-08-31 02:12:22')
        Guest.objects.create(id=1, event_id=1, realname='alen', phone='13711001101', email='alen@mail.com',
                             sign=False)

    def test_event_models(self):
        result = Event.objects.get(name='一加3 发布会')
        self.assertEqual(result.address, '深圳')
        self.assertTrue(result.status)

    def test_guest_models(self):
        result = Guest.objects.get(phone='13711001101')
        self.assertEqual(result.realname, 'alen')
        self.assertFalse(result.sign)


class IndexPageTest(TestCase):
    def text_index_page_renders_index_template(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class LoginActionTest(TestCase):
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')

    def test_add_admin(self):
        user = User.objects.get(username='admin')
        self.assertEqual(user.username, 'admin')
        self.assertEqual(user.email, 'admin@mail.com')

    def test_login_action_username_password_null(self):
        test_data = {'username': '', 'password': ''}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error !', response.content)

    def test_login_action_username_password_error(self):
        test_data = {'username': 'abc', 'password': '123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error !', response.content)

    def test_login_action_success(self):
        test_data = {'username': 'admin', 'password': 'admin123456'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302) # views.py line 24 redirect


class EventManageTest(TestCase):
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(name='xiaomi5', limit=2000, address='beijing', status=1,
                             start_time='2018-8-10 12:30:00')
        self.login_user = {'username': 'admin', 'password': 'admin123456'}

    def test_event_manage_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/search_name_event/', {'name': 'xiaomi5'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'xiaomi5', response.content)
        self.assertIn(b'beijing', response.content)


class GuestManageTest(TestCase):
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=1, name='xiaomi5', limit=2000, address='beijing', status=1,
                             start_time='2018-8-10 12:30:00')
        Guest.objects.create(realname='alen', phone=18611001100, email='alen@mail.com', sign=0, event_id=1)
        self.login_user = {'username': 'admin', 'password': 'admin123456'}

    def test_event_manage_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alen', response.content)
        self.assertIn(b'18611001100', response.content)

    def test_guset_manage_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alen', response.content)
        self.assertIn(b'18611001100', response.content)


class SignIndexActionTest(TestCase):
    def setUp(self):
        User.objects.create_user('admin', 'admin@mail.com', 'admin123456')
        Event.objects.create(id=1, name='xiaomi5', limit=2000, address='beijing', status=1,
                             start_time='2018-8-10 12:30:00')
        Event.objects.create(id=2, name='oneplus4', limit=2000, address='shenzhen', status=1,
                             start_time='2017-8-10 12:30:00')
        Guest.objects.create(realname='alen', phone=18611001100, email='alen@mail.com', sign=0, event_id=1)
        Guest.objects.create(realname='una', phone=18611001001, email='una@mail.com', sign=0, event_id=2)
        self.login_user = {'username': 'admin', 'password': 'admin123456'}

    def test_sign_index_action_phone_null(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {'phone': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'phone error', response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '18611001100'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'event id or phone error.', response.content)

    def test_sign_index_action_sign_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '18611001001'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'sign in success!', response.content)

    def test_sign_index_action_user_sign_has(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '18611001001'})
        response = self.client.post('/sign_index_action/2/', {'phone': '18611001001'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'user has sign in', response.content)
