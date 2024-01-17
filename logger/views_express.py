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
from django.core.mail import send_mail, EmailMessage
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
from .forms import LoginForm, LogForm, UpdateLogForm, PatientForm, CustomUserCreationForm, UserForm, PasswordForm, LinkUserForm, UnlinkUserForm, DoseForm, ExpressTokenForm, ExpressLogForm
from django.core.mail import EmailMessage

# Load credentials from .env file
credentials = {}
with open('/var/www/loewetechsoftware_com/loewetechsoftware_com/.env', 'r') as f:
    for line in f:
        key, var = line.strip('\n').split('=')
        credentials[key] = var



def render_error(request, message):
    '''
        Send basic error message to browser.
    '''
    context = {'error_message': message}
    return render(request, 'logger/error.html', context)


def render_express(request,token_str):
    '''
        render the express add log page. uses token to retreive
        the patient data needed for the express add page.
    '''
    # Get the token from db or send error
    try:
        token = ExpressToken.objects.get(token = token_str)
        
        # get patient from token
        patient = token.patient
        
        # Get the logs, ordered most recent first
        logs = Log.objects.filter(patient_id = patient.id, steps=None).order_by('-date')[:20]
        
        # populate new form with access token 
        form = ExpressLogForm(initial = {'patient' : patient, 
                              'user': patient.user, 
                              'date': datetime.now(), 
                              'token': token.token})
                              
        # render
        context = {'patient': token.patient, 'form': form, 'log_list': logs}
        return render(request, 'logger/Express_add.html', context)

        # Handle no token found
    except ExpressToken.DoesNotExist:
        return render_error(request, f"Token not found: {token_str}")

class ExpressGenericView(View):
    
    def generate_token_form(self, token, Form):
        '''
            takes a token db object and populates the ExpressAddForm
            with info.
        '''
        # get patient from token
        patient = token.patient
        
        # populate new form with access token 
        form = Form(initial = {'patient' : patient, 
                              'user': patient.user, 
                              'date': datetime.now(), 
                              'token': token.token})
        return(form)
        
    def get_logs(self, token):
        '''
            Get the patient logs using the token
        '''
        # Get the patient
        patient = token.patient
        
        # Get the logs, ordered most recent first
        logs = Log.objects.filter(patient_id = patient.id, steps=None).order_by('-date')[:20]
        
        return(logs)
        


class ExpressView(ExpressGenericView):
    '''
        Entry point for the express access system. This route servers
        the client side script that then submits the access token
    '''
    def get(self, request):
        # server the js snippit that will post token to this endpoint
        form = ExpressTokenForm()
        context = {'form': form}
        return render(request, 'logger/Express.html', context)
    
    def post(self, request):
        # Handle token and send log form with user info

        # Validate form first
        form = ExpressTokenForm(request.POST)
        if form.is_valid():
            token_str = form.cleaned_data['token']
            
            return render_express(request, token_str)
        else:
            return render_error("Invalid form")

class ExpressDeleteView(ExpressGenericView):
    '''
        View a log
    '''
    def post(self, request, token, log):
        # Validate form first
        form = ExpressLogForm(request.POST)
        if form.is_valid():
            token_str = form.cleaned_data['token']
            # retreive patient via access token
            try:
                # get token object from db
                token = ExpressToken.objects.get(token = token_str)
                
                # get log from database
                log = Log.objects.get(log = log)
                
                # check if token can access this log
                if log.token_used == token.label:
                    log.delete()
                
                context = {'patient': token.patient, 'form': form}
                return render(request, 'logger/Express_add_confirm.html', context)
            except ExpressToken.DoesNotExist:
                return render_error(request, f"Token not found: {token_str}")
        else:
            context = {'patient': token.patient, 'form': form, 'error': 'Invalid Form'}
            return render(request, 'logger/Express_add_confirm.html', context)

class ExpressAddConfirmView(ExpressGenericView):
    '''
        Recieve form from express access add log form and 
        validate. Then render confirmation screen.
    '''
    def post(self, request):

        # Validate form first
        form = ExpressLogForm(request.POST)
        if form.is_valid():
            token_str = form.cleaned_data['token']
            # retreive patient via access token
            print(token_str)
            try:
                # get token object from db
                token = ExpressToken.objects.get(token = token_str)
                context = {'patient': token.patient, 'form': form, 'token': token_str}
                return render(request, 'logger/Express_add_confirm.html', context)
            except ExpressToken.DoesNotExist:
                return render_error(request, f"Token not found: {token_str}")
        else:
            context = {'patient': token.patient, 'form': form, 'error': 'Invalid Form'}
            return render(request, 'logger/Express_add_confirm.html', context)

class ExpressAddView(ExpressGenericView):
    '''
        Entry point for the express access system. This route servers
        the client side script that then submits the access token
    '''


    def post(self, request):

        # Validate form first
        form = ExpressLogForm(request.POST)
        if form.is_valid():
            token_str = form.cleaned_data['token']
            # retreive patient via access token
            print(token_str)
            try:
                # get token object from db
                token = ExpressToken.objects.get(token = token_str)
                
                # Create and save new log
                new_log = Log(patient = token.patient,
                              user = token.patient.user,
                              token_used = token.label,
                              date = form.cleaned_data['date'],
                              bloodsugar = form.cleaned_data['bloodsugar'],
                              carbs =  form.cleaned_data['carbs'],
                              insulin =  form.cleaned_data['insulin'],
                              notes = form.cleaned_data['notes'],
                              basal =  form.cleaned_data['basal'])
                new_log.save()
                
                # Send user back to Express Access Add screen 
                
                # Create populated form
                form = self.generate_token_form(token, ExpressLogForm)
                
                # get recent patient logs 
                logs = self.get_logs(token)
                
                # render
                context = {'patient': token.patient, 'form': form, 'log_list': logs}
                return render(request, 'logger/Express_add.html', context)
                
                              
            except ExpressToken.DoesNotExist:
                return render_error(request, f"Token not found: {token_str}")

            return HttpResponseRedirect(reverse_lazy('logger:ExpressView'))
        else:
            return render_error("Invalid form")
