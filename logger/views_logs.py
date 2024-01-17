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
from .forms import LogForm,   DoseForm
from .views import SiteView, GenericPatientItem, PatientItemListCreateView
# LOG VIEWS
        
class LogDetailView( GenericPatientItem, DetailView ):
    '''View the details of a single log '''
    model = Log
    permission_required = ('logger.view_log')
    
class LogExportView(SiteView):
    '''View export logs as csv'''
    model = Log
    order_by = '-date'
    
    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        logs = list(self.model.objects.filter(patient_id = pk, steps=None).order_by(self.order_by)[:400])
        return render(request, 'logger/log_export.html', {'log_list':logs, 'patient': patient})
        

class LogListCreateView(PatientItemListCreateView):
    ''' Combined view for both listing a patient's logs and adding a 
        new log for that patient. This is a called the patient dashboard
        on the site.
    '''
    model = Log
    order_by = '-date'
    form = LogForm
    list_url_name = 'logger:LogListCreateView'
  
class LogAddView(GenericPatientItem):
    '''Confirm adding the new log'''
    model = Log
    template_name_suffix = '_add'
    list_url_name = 'logger:LogListCreateView'

class LogUpdateView(GenericPatientItem, UpdateView):
    ''' Edit a log. 
                '''
    model = Log
    fields = ["date", "bloodsugar", "carbs", "insulin", "basal",  "steps", "notes"]
    template_name_suffix = '_update'
    list_url_name = 'logger:LogListCreateView'
   
class LogDeleteView(GenericPatientItem,  DeleteView):
    model = Log
    list_url_name = 'logger:LogListCreateView'
    
    
