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
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from .models import Log, Patient, Profile
from .forms import  PatientForm, CustomUserCreationForm, UserForm, PasswordForm, LinkUserForm, UnlinkUserForm
from .views import SiteView


def render_error(request, message):
    '''
        Send basic error message to browser.
    '''
    context = {'error_message': message}
    return render(request, 'logger/error.html', context)

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

class ProfileSettingsView( SiteView, DetailView ):
    '''View the details a profile '''
    model = Profile
    permission_required = ('logger.view_log')
    
    def get_object(self):
        user = self.request.user
        return(get_object_or_404(Profile, user=user))

class ProfileSettingsUpdateView(SiteView, UpdateView):
    ''' Update the profile  '''
    model = Profile
    fields = ["otp_enabled"]
    template_name_suffix = '_update'
    success_url = reverse_lazy('logger:ProfileSettingsView')
    
    def get_object(self):
        user = self.request.user
        return(get_object_or_404(Profile, user=user))
   
