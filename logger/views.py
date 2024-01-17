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
import random
import string
import csv
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
import pytz
from datetime import datetime
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.utils import timezone
from django.utils.timezone import localtime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import  login, logout, authenticate
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Log, Patient, Dose, Profile, ExpressToken
from .forms import LoginForm, CustomUserCreationForm, UserForm
from .forms import UploadCSVForm

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

def render_error(request, message):
    '''
        Send basic error message to browser.
    '''
    context = {'error_message': message}
    return render(request, 'logger/error.html', context)


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
      return redirect('logger:LogListCreateView', patient.id)
    else:
      return redirect('logger:PatientListView')
  else:
    return redirect('logger:LoginView')

# Site Generic Views
class PatientItemListCreateView(SiteView, ListView):

    def get_queryset(self):
        pk = self.kwargs['pk']
        if self.model == Log:
            return(self.model.objects.filter(patient_id = pk, steps=None).order_by(self.order_by)[:20])
        return(self.model.objects.filter(patient_id = pk).order_by(self.order_by)[:20])

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        pk = self.kwargs['pk']
        patient = get_object_or_404(Patient, pk=pk)
        context['patient'] = patient
        #context['lastDoseRelTime'] = patient.lastDoseRelTime()
        context['form'] = self.form(initial = {'patient' : patient, 'user': self.request.user, 'date':datetime.now() })
        return context


    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        form = self.form(request.POST)
        if patient.user.id == request.user.id or request.user in patient.connected.all():
          if form.is_valid():
            try:
                form.cleaned_data['patient'] = patient
                form.cleaned_data['user'] = self.request.user
                form.save()
                return redirect(self.list_url_name, patient.id)
            except Exception as e:
              context = {'error_message' : str(e)}
              return render(request, 'logger/views/errorView.html', context)
          else:
            context = {'error': 'error', 'form': form, 'patient': patient, self.model.__name__.lower()+'_list': self.model.objects.filter(patient_id = patient.id).order_by(self.order_by)}
            return render(request, "logger/{}_list.html".format( self.model.__name__.lower()), context)
        else:
          context = {"error_message": "You don't have permission to create/edit entires for that patient."}
          return render(request, 'logger/views/errorView.html', context)
        
class GenericPatientItem(SiteView):
    
    #Overload the success url func to go to the item's patient list page of that item
    def get_success_url(self):
        pk = self.kwargs['pk']
        model = get_object_or_404(self.model, pk=pk)
        patient = model.patient
        return(reverse(self.list_url_name, args=[patient.id]))
    
    #Overload context func to add patient to contenx
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        #Add patient to context
        pk = self.kwargs['pk']
        dw = get_object_or_404(self.model, pk=pk)
        context['patient'] = dw.patient
        return context

# USER VIEWS 
class LoginView(FormView):
    template_name = 'logger/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('logger:PatientListView')
    
    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        
        # First use submitted credentials to authenticate user
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(username = username, password = password)
        
        if user is not None:
            
            # If user is valid load profile info and check if 2FA is 
            # enabled
            profile = Profile.objects.get(user=user)
            # if profile.otp_enabled:
                
                # # If 2FA is enabled, first load user cell number
                # cell_number = profile.cell_number
                
                # # Then genarate random number as code
                # code = random.randrange(100000, 800000, 1)
                
                # # Then generate random endpoint url for this code
                # endpoint = ''.join([random.choice(''.join([string.ascii_uppercase, string.ascii_lowercase])) for i in range(30)])
                
                # # Save the code and endpoint in database
                # otp = Otp.objects.create(user = user, code=code, endpoint=endpoint, success_url=self.success_url)
                
                # if cell_number != None:
                    # # Create and send SMS message to user
                    # client = Client(twilio_account_sid, twilio_auth_token)
                    # message = client.messages.create(
                         # body="Loewe Tech Logger\nYour one time code is: {}".format(code),
                         # from_='+17473024930',
                         # to= cell_number
                     # )    
                
                # # Format and send email
                # msg_html = render_to_string('logger/comps/email_otp.html', {'otp_code': code, 'otp_endpoint': endpoint, 'request': self.request})
                # msg = EmailMessage(subject="Otp Code", body=msg_html, from_email='logger@loewetechsoftware.com', bcc=[user.email])
                # msg.content_subtype = "html"  # Main content is now text/html
                # msg.send()
                
                # # Redirect user to the genarted OTP endpoint
                # return(redirect(reverse('logger:OtpView', args=[endpoint])))
            # else:
                # If user doesnt have OTP enbled just log them in
            login(self.request, user)
        return super().form_valid(form)

class AdminLoginView(LoginView):
    template_name = 'logger/login.html'
    form_class = LoginForm
    success_url = '/admin/'
    
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

# # DATA IO VIEWS

class ExportView(SiteView):
  
  def get(self, request, pk):
      patient = get_object_or_404(Patient, pk=pk)
      return render(request, 'logger/views/export_csv.html', {})

    
class ImportView(SiteView):
    def post(self, request):
        fileUp = request.FILES['fileupload']
        return HttpResponse(str(keys))
        
    def get(self, request):
        template = loader.get_template('logger/views/importView.html')
        context = {}
        return HttpResponse(template.render(context, request))

class UploadCSV(SiteView):
    template = 'logger/upload_csv.html'
    
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        form = UploadCSVForm()
        return render(request, self.template, {'form': form, 'patient': patient})
        
    def post(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            
            user = request.user  # Assuming the current user is the uploader
            
            c = 0
            s = 0

            for row in reader:
                if Log.create_from_csv_row(row, patient, user):
                    c += 1
                else:
                    s += 1

            messages.success(request, f'CSV file uploaded  {c} rows successfully!')
            return render(request, self.template, {'form': UploadCSVForm(), 'patient': patient, 'row_count': c, 'skip_count': s})
            #return redirect('logger:upload_csv', patient.id)  # Redirect to the same page after successful upload
        return render(request, self.template, {'form': form, 'patient': patient})
      
