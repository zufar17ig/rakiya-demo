import json
from datetime import date
from django.contrib.auth.models import User
from django.test import TestCase, Client, override_settings
from market.models import Profile

@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class MobileSessionTests(TestCase):
    def setUp(self):
        self.u=User.objects.create_user(username='+94778889999',password='NativeTest!72831',first_name='Native Test')
        Profile.objects.create(user=self.u,phone=self.u.username,role='worker',birth_date=date(1990,1,1))
        self.c=Client(enforce_csrf_checks=True)
    def signin(self):
        r=self.c.post('/mobile-api/login/',json.dumps({'phone':self.u.username,'password':'NativeTest!72831'}),content_type='application/json')
        self.assertEqual(r.status_code,200)
        return r.json()['token']
    def test_bearer_session_and_revocation(self):
        key=self.signin()
        state=self.c.get('/mobile-api/state/',HTTP_AUTHORIZATION='Bearer '+key)
        self.assertEqual(state.json()['user']['name'],'Native Test')
        self.assertEqual(state['Cache-Control'],'no-store')
        self.assertIsNone(self.c.get('/mobile-api/state/').json()['user'])
        self.assertEqual(self.c.post('/mobile-api/logout/','{}',content_type='application/json',HTTP_AUTHORIZATION='Bearer '+key).status_code,200)
        self.assertEqual(self.c.get('/mobile-api/state/',HTTP_AUTHORIZATION='Bearer '+key).status_code,401)
    def test_cookie_cannot_authenticate_native_endpoint(self):
        self.c.force_login(self.u)
        self.assertEqual(self.c.get('/mobile-api/applications/').status_code,401)
    def test_browser_endpoint_still_requires_csrf(self):
        self.signin()
        self.assertEqual(self.c.post('/api/profile/','{}',content_type='application/json').status_code,403)
    def test_invalid_token_and_missing_token(self):
        self.assertEqual(self.c.get('/mobile-api/state/',HTTP_AUTHORIZATION='Bearer invalid').status_code,401)
        self.assertEqual(self.c.get('/mobile-api/applications/').status_code,401)
    def test_native_registration_preserves_adult_rule(self):
        r=self.c.post('/mobile-api/register/',json.dumps({'phone':'+94778880000','password':'NativeTest!82496','role':'worker','name':'Child','birth_date':'2015-01-01'}),content_type='application/json')
        self.assertEqual(r.status_code,400)
