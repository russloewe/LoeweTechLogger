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

from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
import pytz
from django.views import generic
from django.utils import timezone
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import  login, logout, authenticate
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Log, Patient, Profile, PendingUser
from .forms import LogForm, PatientForm, SignupForm
from .plots import  ordinal, Chart
# Our own mix up

class SiteView(LoginRequiredMixin, View):
  name = None
  login_url = '/logger/login/'
  G_RECAPTCHA_CLIENT = '6LfR4ccUAAAAAAzR48MHWIutwQVqB3uwIDm4P4Wv'
  
  @staticmethod
  def getUserProfile(user):
    ''' Take a user object and return the assosciated '''
    if user == None:
        # Pull the test user if not logged in
        return(Profile.objects.get(user_id = 1))
    else:
        return(Profile.objects.get(user_id = user.id))


  @staticmethod
  def checkPerm(profile, patient):
    ''' Return True if profile has permission to access patient,
    else return False 
    '''
    if patient.id == 1:
        return(True)
    if (profile == None) or (patient == None):
        return(False)
    patients = profile.getPatientIds()
    if patient.id in patients:
      return(True)
    else:
      return(False)
          
  def error(self, message):
      context = {'error_message': message}
      template = loader.get_template('logger/views/errorView.html')
      return(HttpResponse(template.render(context, request)))

# Views Start Here
def index(request):
  ''' 
  General entry point for site. If not logged in than show the typical
  landing page. If they are logged in then they are bounced to their 
  home page
  '''
  template = loader.get_template('logger/views/index.html')
  if request.user.is_authenticated:
      profile = Profile.objects.get(user = request.user.id)
      patients = profile.getPatients()
      if len(patients) == 1:
          # if this profile has more than 1 patient go to a different page
          # but for now go to first patient in list.
        patient = patients[0]
        return(HttpResponseRedirect(reverse('logger:PatientView', args=[patients[0].id])))
      else:
          # If this profile has more than 1 patient, render the index template
          # which lists the users          
        for patient in patients:
          patient.lastBasal()
          patient.lastBloodsugar()
          patient.lastInsulin()
        pdata = [ patient.logstodict() for patient in patients]
        context = {'patients' : patients,
                   }
        return(HttpResponse(template.render(context, request)))
  else:
    return(HttpResponseRedirect(reverse('logger:PatientView', args=[1])))


# LOG VIEWS

        
class LogView( SiteView):
    
    redirect_field_name = 'next'
    permission_required = ('logger.view_log')
    
    def get(self, request, pk):
        log = get_object_or_404(Log, pk=pk)
        template = loader.get_template('logger/views/logView.html')
        context = {'log': log} # also success_message and error_message
        return HttpResponse(template.render(context, request))

class LogUpdateView(SiteView):
    ''' Edit a log. 
        - GET: renders the /logger/update.html form
        - POST: Updates db then renders /logger/update.html with result
                '''
    def get(self, request, pk):
        log = get_object_or_404(Log, pk=pk) # load log
        template = loader.get_template('logger/views/logUpdateView.html') # load template
        form = LogForm(initial={'datetime': log.date,
                                'bloodsugar': log.bloodsugar,
                                'carbs': log.carbs,
                                'insulin': log.insulin,
                                'basal': log.basal,
                                'steps': log.steps})
        context = {'form': form,
                   'log_id': log.id}
        # GET render edit page
        return HttpResponse(template.render(context, request))
        
    def post(self, request, pk):
          log = get_object_or_404(Log, pk=pk) # load log
          optional_keys = ['insulin', 'carbs', 'bloodsugar']
      
          form = LogForm(request.POST)
          if form.is_valid():
            log.date = form.cleaned_data['datetime']
            log.insulin = form.cleaned_data['insulin']
            log.bloodsugar = form.cleaned_data['bloodsugar']
            log.carbs = form.cleaned_data['carbs']
            log.basal = form.cleaned_data['basal']
            log.steps = form.cleaned_data['steps']
            
            try:
                log.save()
            # Update Failure
            except Exception as e:
                template = loader.get_template('logger/views/errorView.html')
                context = {'error_message': 'Error saving log'}
                return HttpResponse(template.render(context, request))
            else:
              return(HttpResponseRedirect(reverse('logger:LogView', args=[log.id])))

class LogDeleteView(SiteView):
    login_url = '/logger/login/'
    redirect_field_name = 'next'
    permission_required = ('logger.view_log')
    
    login_url = '/logger/login/'
    redirect_field_name = 'next'
    permission_required = ('logger.delete_log')
    
    def get(self, request, **args):
        pk = args['pk']
        log = get_object_or_404(Log, pk=pk)

        try:
          patient = log.patient
          profile = SiteView.getUserProfile(request.user)
        except Exception:
          return(self.error('Database resource not found'))
        if ( patient == None) or ( profile == None):
          return(self.error('You dont have permission for that.'))
        try:
          SiteView.checkPerm(profile, patient)
        except Exception:
          return(self.error('You dont have permission for that.'))
        if SiteView.checkPerm(profile, patient) == False:
          return(self.error('You dont have permission for that.'))
        try:
            log.delete()
        except Exception as e:
            template = loader.get_template('logger/views/errorView.html')
            context = {'error_title': 'Error',
                       'error_message': 'Failed to delete log'}
            HttpResponse(template.render(context, request))
        else:
            return(HttpResponseRedirect(reverse('logger:PatientView', args=[patient.id])))
    
    def post(self, request, **args):
        pk = args['pk']
        log = get_object_or_404(Log, pk=pk)
        try:
            log.delete()
        except Exception as e:
            template = loader.get_template('logger/views/errorView.html')
            context = {'error_title': 'Error',
                       'error_message': 'Failed to delete log'}
            HttpResponse(template.render(context, request))
        else:
            return HttpResponseRedirect('/logger/')
      


class PatientView(SiteView):
    '''
    This page displays a single user's page with components such as
    recent logs, log adder, quickstats, etc...
    ''' 
    def get(self, request, pk):
        ''' Render Form '''
        try:
          patient = Patient.objects.get(id=pk)
        except Patient.DoesNotExist:
          context = {'error_message': '''Patient not found.'''}
          template = loader.get_template('logger/views/errorView.html')
          return(HttpResponse(template.render(context, request)))
        else:
          # Get the profile from the logged in user
          profile = SiteView.getUserProfile(request.user)          
          if SiteView.checkPerm(profile, patient):
            # Get the patient's logs
            logs = patient.getLogs()
            # Graph past BG
            bgData = patient.getBG()
            #inData = patient.getIN()
            #carbData = patient.getCarb()
            # New log Form
            form = LogForm(initial={'datetime': timezone.now(),
                                    'basal': patient.basal_dose})
            context = { 'patient': patient,
                        'logs' : logs,
                        'form': form,
                        'bgData': bgData,
                        'inData': bgData,
                        'carbData': bgData
                        }
            template = loader.get_template('logger/views/patientView.html')
            return(HttpResponse(template.render(context, request)))
          else:
            context = {'error_message': '''You don't have permission to
                                      view that patient'''}
            template = loader.get_template('logger/views/errorView.html')
            return(HttpResponse(template.render(context, request)))
   
    def post(self, request, pk):
        ''' 
            Add new log to database
            -POST adds new log to db then renders redirects to home
                    or error screen on error
        '''
        template2 = loader.get_template('logger/views/errorView.html')
        context = {'error_message': '''Error.'''}
        error= HttpResponse(template2.render(context, request))
        form = LogForm(request.POST)
        patient = None
        profile = None
        try:
          patient = Patient.objects.get(id = pk)
          profile = SiteView.getUserProfile(request.user)
        except Exception:
          return(self.error('Database resource not found'))
        if SiteView.checkPerm(profile, patient) != True:
            return(self.error('Database resource not found'))
        if form.is_valid():
          basal = None
          if form.cleaned_data['basalcheck']:
            basal = form.cleaned_data['basal']
          log = Log.objects.create(date=timezone.now(),
                                   insulin = form.cleaned_data['insulin'],
                                   bloodsugar = form.cleaned_data['bloodsugar'],
                                   carbs = form.cleaned_data['carbs'],
                                   steps = form.cleaned_data['steps'],
                                   patient = patient,
                                   basal = basal)
               # Save the log                    
          try:
              log.save()
          except Exception as e:
              template = loader.get_template('logger/views/errorView.html')
              context = {'error_message': '''Error trying to save new log :('''}
              return(HttpResponse(template.render(context, request)))
          else:
              return HttpResponseRedirect(reverse('logger:PatientView', args=[patient.id]))
        else:
              context = { 'patient': patient,
                          'form': form,
                }
              template = loader.get_template('logger/views/patientView.html')
              return(HttpResponse(template.render(context, request)))

class PatientUpdateView(SiteView):
    '''
    This view displays an input form with patient attributes filled in
    and handls the form submission to update a patient in the db
    ''' 
    def get(self, request, pk):
        ''' Render Form '''
        template = loader.get_template('logger/views/patientUpdateView.html')
        patient = get_object_or_404(Patient, pk=pk)
        form = PatientForm()
        context = { 'patient': patient,
                    'form': form}
        return(HttpResponse(template.render(context, request)))

class LoginView(View):

  def get(self, request):
    try:
      self.next = request.GET['next']
    except Exception:
      pass
    # On GET request just render login page
    template = loader.get_template('logger/views/userLoginView.html')
    context = {}
    return HttpResponse(template.render(context, request))

  def post(self, request):
    try:
      username = request.POST['username']
      password = request.POST['password']
    except Exception:
      template = loader.get_template('logger/views/userLoginView.html')
      context = {'error_message': "Something wack with your request",
      }
      return HttpResponse(template.render(context, request))

    # Try to retreive the user from the backend 
    user = authenticate(username = username,
    password = password)
    if user is not None:
      # log the user in
      login(request, user)
      # send them on their way or bounce to homepage
      try:
        next = self.next
        return HttpResponseRedirect(next, request)
      except Exception:
        response = HttpResponseRedirect(reverse('logger:index'), request)
        return response
    else:
      # If user is none then send back to login page to try again
      template = loader.get_template('logger/views/userLoginView.html')
      context = {'error_message': "Something wack with auth"}
      response = HttpResponse(template.render(context, request))
      response.status_code = 500
      return response


def Logout(request):
    ''' Logout User'''
    logout(request)
    return HttpResponseRedirect(reverse('logger:index'), request)

class SignUpView(View):
  
  def get(self, request):
    template = loader.get_template('logger/views/signupView.html')
    form = SignupForm()
    context = { 'form' : form }
    return(HttpResponse(template.render(context, request)))
    
  def post(self, request):
    form = SignupForm(request.POST)
    if form.is_valid():
      pending_user = PendingUser.objects.create(email=form.cleaned_data['email'],
                                 first_name=form.cleaned_data['first_name'],
                                 last_name=form.cleaned_data['last_name'])
      pending_user.save()
      template = loader.get_template('logger/views/signupView.html')
      return(HttpResponse(template.render({}, request)))

class ExportView(SiteView):
  
  def get(self, request, pk):
    pass
    
class ImportView(SiteView):
    def post(self, request):
        fileUp = request.FILES['fileupload']
        return HttpResponse(str(keys))
        
    def get(self, request):
        template = loader.get_template('logger/views/importView.html')
        context = {}
        return HttpResponse(template.render(context, request))

