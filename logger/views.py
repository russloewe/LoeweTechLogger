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
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import pytz
from django.views import generic
from django.utils import timezone
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import  login, logout, authenticate
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Log, Patient
from .forms import LogForm, PatientForm, CustomUserCreationForm, UserForm, PasswordForm, LinkUserForm, UnlinkUserForm
from .plots import  ordinal, Chart
# Our own mix up
class SiteView(LoginRequiredMixin, View):
  name = None
  login_url = '/logger/user/login/'
  redirect_field_name = 'next'
  
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
  if request.user.is_authenticated:
    owner_patients = Patient.objects.filter(user_id = request.user.id)
    connected_patients = Patient.objects.filter(connected = request.user.id)
    patients = owner_patients | connected_patients
    print(patients)
    if len(patients) == 1:
        # if this profile has more than 1 patient go to a different page
        # but for now go to first patient in list.
      patient = patients[0]
      return redirect('logger:PatientView', patient.id)
    else:
      return redirect('logger:PatientListView')
  else:
    return redirect('logger:LoginView')

# LOG VIEWS
        
class LogView( SiteView):
  '''
    View the details of a single log
  '''

  permission_required = ('logger.view_log')
    
  def get(self, request, pk):
      log = get_object_or_404(Log, pk=pk)
      context = {'log': log} # also success_message and error_message
      return render(request, 'logger/views/logView.html', context)

class LogCreateView(SiteView):

  def post(self, request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = LogForm(request.POST)
    if patient.user.id == request.user.id or request.user in patient.connected.all():
      if form.is_valid():
        basal = None
        if form.cleaned_data['basalcheck']:
          basal = form.cleaned_data['basal']
        log = Log.objects.create(date=timezone.now(),
                                  user = request.user,
                                  insulin = form.cleaned_data['insulin'],
                                  bloodsugar = form.cleaned_data['bloodsugar'],
                                  carbs = form.cleaned_data['carbs'],
                                  steps = form.cleaned_data['steps'],
                                  patient = patient,
                                  basal = basal)
        try:
          log.save()
          return redirect('logger:PatientView', pk)
        except Exception as e:
          context = {'error_message' : str(e)}
          return render(request, 'logger/views/errorView.html', context)
      else:
        context = {'form': form, 'patient': patient}
        return render(request, 'logger/views/LogCreateView.html', context)
    else:
      context = {"error_message": "You don't have permission to create logs for that patient."}
      return render(request, 'logger/views/errorView.html', context)

class LogUpdateView(SiteView):
    ''' Edit a log. 
        - GET: renders the /logger/update.html form
        - POST: Updates db then renders /logger/update.html with result
                '''
    def get(self, request, pk):
        log = get_object_or_404(Log, pk=pk) # load log
        form = LogForm(initial={'datetime': log.date,
                                'bloodsugar': log.bloodsugar,
                                'carbs': log.carbs,
                                'insulin': log.insulin,
                                'basal': log.basal,
                                'steps': log.steps})
        context = {'form': form,
                   'log_id': log.id}
        # GET render edit page
        return render(request, 'logger/views/logUpdateView.html', context)
        
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
                context = {'error_message': 'Error saving log'}
                return render(request, 'logger/views/errorView.html', context)
            else:
              return redirect('logger:LogView', log.id)
          else:
            context = {'form': form}
            return render(request, 'logger/views/logUpdateView.html', context)

class LogDeleteView(SiteView):
    
    def get(self, request, pk):

      log = get_object_or_404(Log, pk=pk)
      
      # Check permissions
      if request.user not in [log.user, log.patient.user]:
        context = {'log': log,
          'error_message':"""You don't have permission to delete this log.
          Only user that created the log or the patient's owner account can delete logs."""}
        return render(request, 'logger/views/LogDeleteView.html', context)
      else:
        # Render the view
        context = {'log': log}
        return render(request, 'logger/views/LogDeleteView.html', context)
 
    
    def post(self, request, pk):
      log = get_object_or_404(Log, pk=pk)
      patient = log.patient
      context = {'log': log}

      # Check permissions
      if request.user not in [log.user, log.patient.user]:
        context = {'log': log,
          'error_message':"""You don't have permission to delete this leg.
          Only user that created the log or the patient's owner account can delete logs."""}
        return render(request, 'logger/views/LogDeleteView.html', context)
      else:
        # Delete log or error message
        try:
            log.delete()
            return redirect('logger:PatientView', patient.id)
        except Exception as e:
            context = {'log': log,
              'error_message':"Failed to delete log."}
            return render(request, 'logger/views/LogDeleteView.html', context)


# PATIENT VIEWS

class PatientView(SiteView):
    '''
    This page displays a single user's page with components such as
    recent logs, log adder, quickstats, etc...
    ''' 
    def get(self, request, pk):
        ''' Render Form '''
        patient = get_object_or_404(Patient, pk=pk)

        if patient.user.id == request.user.id or request.user in patient.connected.all():
          # Get the patient's logs
          logs = patient.getLogs()
          # Graph past BG
          bgData = patient.getBG()
          inData = patient.getIN()
          #carbData = patient.getCarb()
          # New log Form
          form = LogForm(initial={'patient': patient.id,
                'datetime': timezone.now(),
                'basal': patient.basal_dose})
          context = { 'patient': patient,
                      'logs' : logs,
                      'form': form,
                      'bgData': bgData,
                      'inData': inData,
                      'carbData': bgData
                      }
          return render(request, 'logger/views/PatientView.html', context)
        else:
          context = {'error_message': '''You don't have permission to
                                    view that patient'''}
          return render(request, 'logger/views/errorView.html', context)

class PatientLinkView(SiteView):

  def get(self, request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if patient.user.id != request.user.id:
      context = {'error_message': 'Only the patient owner can link accounts.'}
      return render(request, 'logger/views/errorView.html', context)
    else:
      form = LinkUserForm()
      context = {'form': form, 'patient': patient}
      return render(request, 'logger/views/PatientLinkView.html', context)
  
  def post(self, request, pk):
    # Check permissions first
    patient = get_object_or_404(Patient, pk=pk)
    if patient.user.id != request.user.id:
      context = {'error_message': 'Only the patient owner can link accounts.'}
      return render(request, 'logger/views/errorView.html', context)
    # Validate form second
    form = LinkUserForm(request.POST)
    if form.is_valid():
      user = form.cleaned_data['username']
      patient.connected.add(user.id)
      return HttpResponseRedirect(reverse('logger:PatientDetailView', args=[patient.id]), request)
    else:
      context = {'form': form, 'patient': patient}
      return render(request, 'logger/views/PatientLinkView.html', context)


class PatientUnlinkView(SiteView):

  def get(self, request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if patient.user.id != request.user.id:
      context = {'error_message': 'Only the patient owner can link accounts.'}
      return render(request, 'logger/views/errorView.html', context)
    else:
      form = UnlinkUserForm(instance=patient)
      context = {'form': form, 'patient': patient}
      return render(request, 'logger/views/PatientUnlinkView.html', context)
  
  def post(self, request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = UnlinkUserForm(request.POST, instance=patient)
    if patient.user.id != request.user.id:
      context = {'error_message': 'Only the patient owner can link accounts.'}
      return render(request, 'logger/views/errorView.html', context)
    if form.is_valid():
      user = form.cleaned_data['connected']
      patient.connected.remove(user)
      patient.save()
      return redirect('logger:PatientDetailView', pk=patient.id)
    else:
      context = {'form': form, 'patient': patient}
      return render(request, 'logger/views/PatientUnlinkView.html', context)

class PatientListView(SiteView):
  
  def get(self, request):
    user_patients = Patient.objects.filter(user_id = request.user.id)
    connected_patients = Patient.objects.filter(connected = request.user.id)
    patients = user_patients | connected_patients
    context = {'patients': patients}
    return render(request, 'logger/views/PatientListView.html', context)

class PatientDetailView(SiteView):
    '''
    This page displays a single user's page with components such as
    recent logs, log adder, quickstats, etc...
    ''' 
    def get(self, request, pk):
        ''' Render Form '''
        patient = get_object_or_404(Patient, pk=pk)

        if patient.user.id == request.user.id or request.user in patient.connected.all():
          context = { 'patient': patient
                      }
          return render(request, 'logger/views/PatientDetailView.html', context)
        else:
          context = {'error_message': '''You don't have permission to
                                    view that patient'''}
          return render(request, 'logger/views/errorView.html', context)

class PatientUpdateView(SiteView):
    '''
    This view displays an input form with patient attributes filled in
    and handls the form submission to update a patient in the db
    ''' 
    def get(self, request, pk):
        ''' Render Form '''
        patient = get_object_or_404(Patient, pk=pk)
        if request.user.id != patient.user.id:
          context = {'error_message': 'You cannot edit that patient. Only the patient owner account may make changes.'}
          return render(request, 'logger/views/errorView.html', context)
        else:
          form = PatientForm(instance=patient)
          context = { 'patient': patient, 'form': form}
          return render(request, 'logger/views/PatientUpdateView.html', context)

    def post(self, request, pk):
      patient = get_object_or_404(Patient, pk=pk)
      form = PatientForm(request.POST, instance=patient)
      if form.is_valid():
        form.save()
        return redirect('logger:PatientDetailView', pk)
      else:
        context = { 'patient': patient, 'form': form}
        return render(request, 'logger/views/PatientUpdateView.html', context)

class PatientDeleteView(SiteView):

    def get(self, request, pk):
      patient = get_object_or_404(Patient, pk=pk)
      
      # Check permission
      if request.user.id != patient.user.id:
        context = {'patient': patient,
          'error_message': """You cannot delete that patient. 
            Only the patient owner account may make changes."""}
        return render(request, 'logger/views/PatientDeleteView.html', context)
      else:
        # Render the view
        context = {'patient': patient}
        return render(request, 'logger/views/PatientDeleteView.html', context)

    def post(self, request, pk):
      patient = get_object_or_404(Patient, pk=pk)
      
      # Check permission
      if request.user.id != patient.user.id:
        context = {'patient': patient,
          'error_message': """You cannot delete that patient. 
            Only the patient owner account may make changes."""}
        return render(request, 'logger/views/PatientDeleteView.html', context)
      else:
        try:
          patient.delete()
          return redirect('logger:ProfileView')
        except Exception as e:
          context = {'patient': patient,
            'error_message': "Unable to delete patient."}
          return render(request, 'logger/views/PatientDeleteView.html', context)

class PatientCreateView(SiteView):

  def get(self, request):
    form = PatientForm()
    context = { 'form' : form}
    return render(request, 'logger/views/PatientCreateView.html', context)

  def post(self, request):
    try:
      form = PatientForm(request.POST)
      if form.is_valid():
        patient = form.save(commit=False)
        patient.user_id = request.user.id
        patient.save()
        return HttpResponseRedirect(reverse('logger:ProfileView'), request)
      else:
        context = { 'form' : form}
        return render(request, 'logger/views/PatientCreateView.html', context)
    except Exception as e:
      context = { 'error_message': str(e)}
      return render(request, 'logger/views/errorView.html', context)
# USER VIEWS

class LoginView(View):

  def get(self, request):
    try:
      self.next = request.GET['next']
    except Exception:
      pass
    # On GET request just render login page
    context = {}
    return render(request, 'logger/views/userLoginView.html', context)

  def post(self, request):
    try:
      username = request.POST['username']
      password = request.POST['password']
    except Exception:
      context = {'error_message': "Something wack with your request",
      }
      return render(request, 'logger/views/userLoginView.html', context)

    # Try to retreive the user from the backend 
    user = authenticate(username = username,
    password = password)
    if user is not None:
      # log the user in
      login(request, user)
      # send them on their way or bounce to homepage
      try:
       # next = self.next
        return HttpResponseRedirect(next, request)
      except Exception:
        response = HttpResponseRedirect(reverse('logger:index'), request)
        return response
    else:
      # If user is none then send back to login page to try again
      context = {'error_message': "Something wack with auth"}
      return render(request, 'logger/views/userLoginView.html', context)

class LogoutView(View):

  def get(self, request):
    return render(request, 'logger/views/userLogoutView.html', {})

  def post(self, request):
    logout(request)
    return redirect('logger:LoginView')

class RegisterView(View):
  
  def get(self, request):
    #form = CustomUserCreationForm()
    #context = { 'form' : form }
    return render(request, 'logger/views/tempRegisterView.html', {})
    
  def post(self, request):
      #f = CustomUserCreationForm(request.POST)
      #if f.is_valid():
      #    f.save()
      #    return(HttpResponseRedirect(reverse('logger:ProfileView')))
      return render(request, 'logger/views/tempRegisterView.html', {})

# PROFILE VIEWS

class ProfileView(SiteView):

  def get(self, request):
    context = {}
    try:
      # Retrive the Profile for the logged in user
      patients = Patient.objects.filter(user_id = request.user.id)
      connected_patients = Patient.objects.filter(connected = request.user.id)
      context = { 'patients': patients,
        'connected_patients': connected_patients}    
    except Exception as e:
      context = { 'error_message': str(e)}    
    return render(request, 'logger/views/ProfileView.html', context)

class ProfileUpdateView(SiteView):
  
  def get(self, request):
    form = UserForm(instance=request.user)
    context = {'form': form}
    return render(request, 'logger/views/ProfileUpdateView.html', context)

  def post(self, request):
    form = UserForm(request.POST, instance=request.user)
    if form.is_valid():
      form.save()
      return redirect('logger:ProfileView')
    else:
      return render(request, 'logger/views/ProfileUpdateView.html', {'form': form})

class ProfileUpdatePasswordView(SiteView):

  def get(self, request):
    form = PasswordForm()
    context = {'form': form}
    return render(request, 'logger/views/ProfileUpdatePasswordView.html', context)

  def post(self, request):
    form = PasswordForm(request.POST)
    if form.is_valid():
      request.user.set_password(form.cleaned_data['password1'])
      return redirect('logger:ProfileView')
    else:
      return render(request, 'logger/views/ProfileUpdatePasswordView.html', {'form': form})

# DATA IO VIEWS

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

