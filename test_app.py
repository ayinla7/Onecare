import unittest
from app import app
import io


class TestsSetup(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False

        self.app = app.test_client()
        self.assertEqual(app.debug, False)

    # executed after each test
    def tearDown(self):
        pass

class TestCase(unittest.TestCase):
    # test if patientprofile opens successfully
    def test_patientprofile_status(self):
        tester = app.test_client(self)
        response = tester.get('/profile', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

    # test if staffprofile opens successfully
    def test_staffprofile_status(self):
        tester = app.test_client(self)
        response = tester.get('/profilest', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

        # test if staffprofile opens successfully

    def test_records_status(self):
        tester = app.test_client(self)
        response = tester.get('/records', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

        # test if staffprofile opens successfully

    def test_settings_status(self):
        tester = app.test_client(self)
        response = tester.get('/settings', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)


    #Checking for Key words on Page
    def test_settings_content(self):
        tester = app.test_client(self)
        response = tester.get('/settings', content_type='html/text')
        self.assertTrue(b'dashboard' in response.data)  # passed the test


    def test_settings_content1(self):
        tester = app.test_client(self)
        response = tester.get('/profile', content_type='html/text')
        self.assertTrue(b'NHS' in response.data)

    def test_profile_content1(self):
        tester = app.test_client(self)
        response = tester.get('/profile', content_type='html/text')
        self.assertTrue(b'profile' in response.data)


    def test_profile_content2(self):
        tester = app.test_client(self)
        response = tester.get('/profile', content_type='html/text')
        self.assertTrue(b'vaccination' in response.data)


    def test_profile_content3(self):
        tester = app.test_client(self)
        response = tester.get('/profile', content_type='html/text')
        self.assertTrue(b'NHS' in response.data)


    def test_records_content(self):
        tester = app.test_client(self)
        response = tester.get('/records', content_type='html/text')
        self.assertTrue(b'NHS' in response.data)

    def test_records_content2(self):
        tester = app.test_client(self)
        response = tester.get('/records', content_type='html/text')
        self.assertTrue(b'Medication' in response.data)

    def test_records_content3(self):
        tester = app.test_client(self)
        response = tester.get('/records', content_type='html/text')
        self.assertTrue(b'Back' in response.data)

#Test for First Home Image
    def test_Home_images(self):
        self.test_app = app.test_client()

        with open('/Users/ayinlakwamdeen/PycharmProjects/LoginTest/static/images/icon_white.png', 'rb') as img1:
            imgStringIO1 = io.StringIO("")

        response = self.test_app.get('/',content_type='multipart/form-data',
                                        data={'image': (imgStringIO1, 'img1.jpg')})
        self.assertEqual(response.status, "200 OK")

    # test if Home Page opens successfully
    def test_home_status(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

      #Checking for Key words on Home page
    def test_home_content(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'dashboard' in response.data)  # passed the test

    def test_home_content2(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Coronavirus (COVID-19)' in response.data)  # passed the test

    def test_home_content3(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Get information about coronavirus on NHS.UK' in response.data)  # passed the test

    def test_home_content4(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Call for Emergency' in response.data)  # passed the test

    def test_home_content5(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Join Us today' in response.data)  # passed the test

    def test_home_content6(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Why OneCare?' in response.data)  # passed the test

    def test_home_content6(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'Sign In' in response.data)  # passed the test

    def test_home_content8(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'As Patient' in response.data)  # passed the test

    def test_home_content9(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'As Care-giver' in response.data)  # passed the test

    def test_home_content10(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        self.assertTrue(b'As Admin' in response.data)  # passed the test


    # test if Dashboard Page opens successfully
    def test_dashboard_status(self):
        tester = app.test_client(self)
        response = tester.get('/dashboard', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)


    # test if Staff View Page opens successfully
    def test_staffview_status(self):
        tester = app.test_client(self)
        response = tester.get('/staffview', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)


    # test if patients view Page opens successfully
    def test_patientview_status(self):
        tester = app.test_client(self)
        response = tester.get('/patientview', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

      #Checking for Key words on Dashboard page
    def test_dashboard_content(self):
        tester = app.test_client(self)
        response = tester.get('/dashboard', content_type='html/text')
        self.assertTrue(b'dashboard' in response.data)  # passed the test

        # Checking for Key words on patientview page

    def test_patientview_content(self):
        tester = app.test_client(self)
        response = tester.get('/patientview', content_type='html/text')
        self.assertTrue(b'dashboard' in response.data)  # passed the test

        # Checking for Key words on staffview page
    def test_staffview_content(self):
        tester = app.test_client(self)
        response = tester.get('/staffview', content_type='html/text')
        self.assertTrue(b'dashboard' in response.data)  # passed the test

    # test if GP Login Page opens successfully
    def test_logingp_status(self):
        tester = app.test_client(self)
        response = tester.get('/logingppage', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

    # test if Staff Login Page opens successfully
    def test_loginstaff_status(self):
        tester = app.test_client(self)
        response = tester.get('/loginstaffpage', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

    # test if Patients Login Page opens successfully
    def test_loginPage_status(self):
        tester = app.test_client(self)
        response = tester.get('/loginPage', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

        #Checking for Key words on Login pages page
    def test_logingp_content(self):
        tester = app.test_client(self)
        response = tester.get('/logingppage', content_type='html/text')
        self.assertTrue(b'SIGN IN' in response.data)  # passed the test

    def test_loginstaffpage_content(self):
        tester = app.test_client(self)
        response = tester.get('/loginstaffpage', content_type='html/text')
        self.assertTrue(b'SIGN IN' in response.data)  # passed the test

    def test_loginPage_content(self):
        tester = app.test_client(self)
        response = tester.get('/loginPage', content_type='html/text')
        self.assertTrue(b'SIGN IN' in response.data)  # passed the test

    # pass (test if Staff/GP/Patients Registration Page opens succefully)
    def test_StaffReg_status(self):
        tester = app.test_client(self)
        response = tester.get('/registerstaff', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)


    # pass (test if GP Registration Page opens succefully)
    def test_GPReg_status(self):
        tester = app.test_client(self)
        response = tester.get('/registergp', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)


    # pass (test if Patients Registration Page opens succefully)
    def test_PatientReg_status(self):
        tester = app.test_client(self)
        response = tester.get('/registerpatient', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # pass (test if the page renders successfully)

      #Checking for Key words on Patients Register page
    def test_signUppatient_content(self):
        tester = app.test_client(self)
        response = tester.get('/registerpatient', content_type='html/text')
        self.assertTrue(b'General information' in response.data)  # passed the test



if __name__ == '__main__':
    unittest.main()
