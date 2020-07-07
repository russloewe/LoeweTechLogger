# Loewe Tech Logger, Type 1 Diabetes Logging webapp.
# Copyright (C) 2019 Russell Loewe  

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import datetime
import pytz
from functools import reduce
from django.test import TestCase, Client
from django.test.utils import setup_test_environment
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import login, logout, authenticate
from .models import Log, Patient, Profile, PendingUser
from .forms import PatientForm, LogForm, ProfileForm, ImportForm, ExportForm, SignupForm
from .plots import ordinal
from .oauth import grantUrl


# Utility Functions

def printSuccess(func):
    ''' 
        Function decorator to print when test 
        finishes without errors.
    '''
    def func_wrapper(*args, **kwargs):
       func(*args, **kwargs)
       print('\nSUCCESS:  {}'.format(func.__name__))
    return func_wrapper

class OauthTests(TestCase):
    
    @printSuccess
    def test_grantUrl(self):
        '''Test grantUrl'''
        # test without args
        host = 'www.fake.com'
        path = '/test/'
        url = grantUrl(host, path, {})
        self.assertIs(url == 'www.fake.com/test/', True)
        
        # test with args
        args = {'token': 23, 'url' : 'www.stuff.com'}
        url = grantUrl(host, path, args)
        self.assertEqual(url, 'www.fake.com/test/?token=23&url=www.stuff.com')
   

class ModelTests(TestCase):
    def setUp(self):
      self.user = User.objects.create(username='test')
      self.user.set_password('test')
      self.user.save()
      
    def test_PendingPatient(self):
      ''' Test PendingPatient Model'''
      pending_user = PendindUser.objects.create(first_name = 'test1',
                                                last_name = 'test2',
                                                email = 'test@server.com')
      pending_user.save()
      user = PendingUser.objects.order_by('id')[0]
      self.assertIs(user.first_name, 'test1')
      
      
    
    @printSuccess
    def test_Patient(self):
        '''Test create, save and load Patient'''
        # Create Patient
        patient = Patient()
        patient.dob = datetime.date(2019, 9, 16)
        patient.first_name = 'test1'
        patient.last_name = 'test2'
        # Save
        patient.save()
        # Retrieve
        patient2 = Patient.objects.order_by('id')[0]
        self.assertIs(type(patient) == type(patient2), True)
        self.assertIs(patient.first_name == patient2.first_name, True)
        # .as_dict()
        data = patient.as_dict()
        items = [data[key] for key in data]
        self.assertEqual(len(items) > 0, True)

    @printSuccess
    def test_Profile(self):
        ''' Test add, remove and get userid perms'''
        patient = Patient.objects.create(dob = datetime.date(2014,1,2),
                                     first_name = 'test',
                                     last_name = 'test',
                                     carb_ratio = 20,
                                     correction_step = 50,
                                     correction_start = 150)
        patient.save()
        # Create
        profile = Profile()
        profile.user = self.user
        # Save
        profile.save()
        # Load
        profile2 = Profile.objects.order_by('id')[0]
        self.assertIs(type(profile) == type(profile2), True)
        self.assertIs(profile.user == profile2.user, True)
    
    @printSuccess
    def test_Log(self):
        '''Test if log = Log()'''
        # Create
        patient = Patient.objects.create(dob = datetime.date(2014,1,2),
                                     first_name = 'test',
                                     last_name = 'test',
                                     carb_ratio = 20,
                                     correction_step = 50,
                                     correction_start = 150)
        patient.save()
        log = Log()
        log.patient = patient
        log.date = timezone.now()
        # Save
        log.save()
        # Load
        log2 = Log.objects.order_by('id')[0]
        self.assertIs(type(log) == type(log2), True)
        self.assertIs(log.patient == log2.patient, True)

class PlotTests(TestCase):
 
  @printSuccess
  def test_ordinal(self):
    date = datetime.datetime(2018, 1, 1, 1, 1, 2)
    age = ordinal(date)
    self.assertIs(age < 0, True)
    
class ModelRelationTests(TestCase):
    '''
        Test relationships between differnt models in
        the database
    '''
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.user.set_password('test')
        self.user.save()
        self.patient = Patient.objects.create(dob = datetime.date(2014,1,2),
                                       first_name = 'test',
                                       last_name = 'test',
                                       carb_ratio = 20,
                                       correction_step = 50,
                                       correction_start = 150)
        self.patient.save()
        # Create
        self.profile = Profile()
        self.profile.user = self.user
        # Save
        self.profile.save()
        # Add couple of logs
        for j in range(1,10):
          log = Log()
          log.patient = self.patient
          log.bloodsugar = 1
          log.carbs = 2
          log.insulin = 3
          log.basal = 4
          log.date = timezone.datetime(2015, 1, 1, j, 11, 1) 
          log.save()
            
    @printSuccess
    def test_patient_getBg(self):
      ''' test patient.getBg()'''
      logs = self.patient.getBG()
      self.assertTrue(len(logs) > 0)
      
    def test_patient_last(self):
      '''test .lastCarbs, .lastInsulin ...
      '''
      patient = create_test_patient()
      for i in range(10):
          log = Log()
          log.patient = patient
          log.bloodsugar = 1
          log.carbs = 2
          log.insulin = 3
          log.basal = 4
          log.date = timezone.now()
          log.save()
      self.assertEqual(patient.lastCarbs().carbs, 2)
      self.assertEqual(patient.lastInsulin().insulin, 3)
      self.assertEqual(patient.lastBasal().basal, 4)
      self.assertEqual(patient.lastBloodsugar().bloodsugar, 1)
      
 
    def test_get_logs_by_patient(self):
        '''test making logs and saving and getting by patient'''
        patient = create_test_patient()
        for i in range(10):
            log = Log()
            log.patient = patient
            log.bloodsugar = 1
            log.insulin = 3
            log.basal = 4
            log.date = timezone.now()
            log.save()
        # .getLogs()
        logs = patient.getLogs()
        self.assertIs(len(logs) == 10 , True)
        for log in logs:
            self.assertIs(type(Log()) == type(log), True)
        for i in range(10):
          self.assertIs(logs[i].bloodsugar == 1, True)
        # .getBG()
        data = patient.getBG()
        self.assertEqual(len(data)>0, True)
         # .logstodict
        logdict = patient.logstodict()
        self.assertIs(type(logdict['bloodsugar']), type([]))
        self.assertIs((0, 1) in logdict['bloodsugar'], True)
        self.assertIs(type(logdict['insulin']), type([]))
        self.assertIs((0, 3) in logdict['insulin'], True)
        self.assertIs(type(logdict['basal']), type([]))
        self.assertIs((0, 4) in logdict['basal'], True)
        
 
    def test_lookup_user_profile(self):
        ''' test Profile.getUserProfile() '''
        profile = Profile.objects.get(user = self.user.id)
        self.assertIs(type(profile), type(Profile()))

 
    def test_addpatient_removepatient_profile_users(self):
        ''' add patient and remove patient to profile patient list'''
        user1 = create_test_user()
        user2 = create_test_user(username='twe')
        user3 = create_test_user(username='th')
        patient1 = create_test_patient()
        patient2 = create_test_patient()
        
        # Profile 1 for user 1 with patient 1
        profile1 = Profile()
        profile1.user = user1
        profile1.addPatient(patient1)
        profile1.save()
        
        # Profile 2 for user 2 with patients 1 and 2
        profile2 = Profile()
        profile2.user = user2
        profile2.addPatient(patient1)
        profile2.addPatient(patient2)
        
        # Profile 3 for user 3 with no patients
        profile3 = Profile.objects.create(user = user3)
        profile3.save()
        
        # Test profile 1
        self.assertIs(patient1.id in profile1.getPatientIds(), True)
        self.assertIs(patient2.id in profile1.getPatientIds(), False)
        # Test profile 2
        self.assertIs(patient1.id in profile2.getPatientIds(), True)
        self.assertIs(patient2.id in profile2.getPatientIds(), True)
        # Test profile 3
        self.assertIs(patient1.id in profile3.getPatientIds(), False)
        self.assertIs(patient2.id in profile3.getPatientIds(), False)
        
        profile2.removePatient(patient1)
        profile2.removePatient(patient2)
        
        self.assertIs(patient1.id in profile2.getPatientIds(), False)
        self.assertIs(patient2.id in profile2.getPatientIds(), False)

class FormTests(TestCase):
  
  @printSuccess
  def test_PatientForm(self):
    '''Test the patient form'''
    form_data = {'dob' : datetime.date(2016,2,3),
                 'first_name': 'test',
                 'last_name': 'test',
                 'carb_ratio': 20,
                 'correction_start': 150,
                 'correction_step': 100,
                 'basal_dose': 6}
    form = PatientForm(data = form_data)
    self.assertTrue(form.is_valid())
    
  @printSuccess
  def test_LogForm(self):
    ''' Test LogForm '''
    form_data = {
                 'bloodsugar': 1,
                 'carbs': 2,
                 'insulin': 3.5,
                 'basal': 4,
                 'steps': 5,
                 'basal_check': 'False',
                 'now_radio': 'now'}
    form = LogForm(data = form_data)
    self.assertTrue(form.is_valid())
    
  def test_ProfileForm(self):
    ''' Test ProfileForm '''
    form_data = { }
    form = ProfileForm(data=form_data)
    self.assertTrue(form.is_valid())
    
  def test_ImportForm(self):
    ''' Test ImportForm '''
    form_data = { }
    form = ImportForm(data=form_data)
    self.assertTrue(form.is_valid())
    
  def test_ExportForm(self):
    ''' Test ExportForm '''
    form_data = { }
    form = ExportForm(data=form_data)
    self.assertTrue(form.is_valid())
  
  def test_SignupForm(self):
    ''' test SignupForm '''
    form_data = { }
    form = SignupForm(data=form_data)
    self.assertTrue(form.is_valid())

class ViewTests(TestCase):
    templates = ['logger/comps/base.html', 'logger/comps/navbar.html',
            'logger/comps/userbox.html', 'logger/header/bootstrap.html',
            'logger/header/favicon.html', 'logger/header/google.html',
            'logger/header/og_meta.html']
            
    def setUp(self):
        # Create admin
        user = User.objects.create(username='admin')
        user.set_password('test')
        user.save()
        admin = Profile.objects.create(user=user)
        #  Create users
        for i in range(1,5):
          # user
          user_name = 'test_user{}'.format(i)
          user = User.objects.create(username=user_name)
          user.set_password('test')
          user.save()
          
          # Create profile attached to user
          profile = Profile.objects.create(user=user)
          date = datetime.datetime(2015, 1,1,11,1).date()
          
          # Create patient
          patient = Patient.objects.create(dob = date,
                                     first_name = user_name,
                                     last_name = 'test',
                                     carb_ratio = 20,
                                     correction_step = 50,
                                     correction_start = 150)
          patient.save()
          profile.addPatient(patient)
          admin.addPatient(patient)
          profile.save()
          
          # Add couple of logs
          for j in range(1,10):
            log = Log()
            log.patient = patient
            log.logger = profile
            log.bloodsugar = 1
            log.carbs = 2
            log.insulin = 3
            log.basal = 4
            log.date = timezone.datetime(2015, 1, 1, j, 11, 1) 
            log.save()

        admin.save()

    # Index
 
    def test_IndexView(self):
        '''
        test the home view
        '''
        self.assertEquals(True, False)
        # Not logged in
        client = Client()
        response = client.get(reverse('logger:index'))
        self.assertTemplateUsed(response, 'logger/views/index.html')
        self.assertTemplateUsed(response, 'logger/about.html')
        for template in self.templates:
            self.assertTemplateUsed(response, template) 

        # Logged in, this user has 1 patient
        client = Client()
        login = client.login(username='test2', password='test')
        response = client.get(reverse('logger:index'), follow=True)
        self.assertRedirects(response, reverse('logger:PatientView', args=[1]))
   
        # Logged in user has 2 patients
        client = Client()
        login = client.login(username='test3', password='test')
        response = client.get(reverse('logger:index'))
        #self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logger/views/index.html')
        for template in self.templates:
            self.assertTemplateUsed(response, template)
    
    # LOGS   

 
    def test_LogView(self):
        self.assertEquals(True, False)
        login = self.client.login(username='test2', password='test')
        response = self.client.get(reverse('logger:LogView', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logger/views/logView.html') 
            
 
    def test_LogUpdateView(self):
        self.assertEquals(True, False)
        login = self.client.login(username='test2', password='test')
        response = self.client.get(reverse('logger:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logger/index.html') 
        self.assertTemplateUsed(respones, self.templates)
      
 
    def test_LogDeleteView(self):
        self.assertEquals(True, False)
        login = self.client.login(username='test2', password='test')
        response = self.client.get(reverse('logger:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logger/index.html') 
        self.assertTemplateUsed(respones, self.templates)
 
    def test_LogView(self):
        self.assertEquals(True, False)
        login = self.client.login(username='test2', password='test')
        response = self.client.get(reverse('logger:LogView', args=[1]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logger/views/errorView.html') 
      
    # PATIENTS

    def test_PatientView(self):
        '''
        Make sure that the patientView is rendered for a user
        with correct permissions
        '''
        # Anon user should be redirected to login page with 'next' arg
        response = self.client.get(reverse('logger:PatientView', args=[1]))
        self.assertRedirects(response, "/logger/login/?next=/logger/patient/1/")
        
        # Logged in user that doesn't have permission should get error page
        login = self.client.login(username='test_user1', password='test')
        response = self.client.get(reverse('logger:PatientView', args=[3]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'logger/views/errorView.html') 
        
        # Logged in user should be able to get their patient
        for i in range(1,5):
          login = self.client.login(username='test_user{}'.format(i), password='test')
          response = self.client.get(reverse('logger:PatientView', args=[i]))
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'logger/views/patientView.html') 
        
        # Admin Should get all the patients
        login = self.client.login(username='admin', password='test')
        for i in range(1,5):
          response = self.client.get(reverse('logger:PatientView', args=[i]))
          self.assertEqual(response.status_code, 200)
          self.assertTemplateUsed(response, 'logger/views/patientView.html') 
          
        # Trying a non existant patient should get the error page
        login = self.client.login(username='test_user1', password='test')
        response = self.client.get(reverse('logger:PatientView', args=[12]))
        self.assertTemplateUsed(response, 'logger/views/errorView.html') 
          
        # An anon user shouldn't get a 404 page 
        response = Client().get(reverse('logger:PatientView', args=[12]))
        self.assertRedirects(response, "/logger/login/?next=/logger/patient/12/")
    
    def test_patientUpdateView(self):
        '''
            test the patient update view
        '''
        self.assertEquals(True, False)
        login = self.client.login(username='test2', password='test')
        response = self.client.get(reverse('logger:PatientUpdateView', args=[self.patient_id]))
        self.assertTemplateUsed(response, 'logger/views/patientUpdateView.html')
        user = User.objects.get(username = 'test2')
        self.assertEqual(response.status_code, 200)

    def test_patientDeleteView(self):
      self.assertEquals(True, False)
      
    def test_patientAddView(self):
      self.assertEquals(True, False)
      
    # USER
    def test_LoginView(self):
      self.assertEquals(True, False)
      
    def test_userLogoutView(self):
        '''
        Test the login screen
        '''
        self.assertEquals(True, False)
        response = self.client.get(reverse('logger:LoginView'))
        login = self.client.login(username='test2', password='test')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('logger:LogoutView'), follow=True)
        self.assertRedirects(response, '/logger/')
        
    # PROFILE
    def test_signUpView(self):
      ''' Test /logger/signup'''
      self.assertEquals(True, False)
      response = self.client.get(reverse('logger:SignUpView'))
      self.assertEqual(response.status_code, 200)
      self.assertTemplateUsed(response, self.templates)
    
    def test_profileView(self):
      self.assertEquals(True, False)
      
    def test_profileUpdateView(self):
      self.assertEquals(True, False)
    # DATA
    def test_exportView(self):
      self.assertEquals(True, False)
      
    def test_importView(self):
      pass
