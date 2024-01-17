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
import qrcode
import io
import base64
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.core.exceptions import ValidationError
from .models import  Patient, ExpressToken
from .forms import PatientForm, CustomUserCreationForm, UserForm, PasswordForm, LinkUserForm, UnlinkUserForm
from .views import SiteView


def generate_qr_code(input_string):
    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # Add data to the QR code
    qr.add_data(input_string)
    qr.make(fit=True)

    # Create an image from the QR code instance
    qr_img = qr.make_image(fill_color="black", back_color="white")

    # Convert the image to bytes
    image_bytes = io.BytesIO()
    qr_img.save(image_bytes)

    # Get the bytes value
    image_bytes = image_bytes.getvalue()
    
    encoded_string = base64.b64encode(image_bytes).decode('utf-8')
    return encoded_string


# PATIENT VIEWS
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

class PatientListView(SiteView, ListView):
    model = Patient

    def get_queryset(self):
        user_patients = Patient.objects.filter(user_id = self.request.user.id)
        connected_patients = Patient.objects.filter(connected =self.request.user.id)
        patients = user_patients | connected_patients
        return(user_patients | connected_patients)
   
class PatientDetailView(SiteView, DetailView):
    '''
    This page displays a single user's page with components such as
    recent logs, log adder, quickstats, etc...
    ''' 
    model = Patient
    
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        
        # Check if there are any ExpressAccessTokens associated with the patient
        express_access_tokens = self.object.expresstoken_set.all()

        if express_access_tokens:
            # If there are tokens, retrieve the first one (you can modify this based on your logic)
            express_token = express_access_tokens[0].token
            
            # Create the URL for the ExpressView with the token
            express_url = self.request.build_absolute_uri(reverse('logger:ExpressView') + f'#token={express_token}')
            
            # Generate QR code for that url
            express_qr_code = generate_qr_code(express_url)

            context['express_url'] = express_url
            context['express_qr_code'] = express_qr_code

        return context
        
class PatientUpdateView(SiteView, UpdateView):
    '''
    This view displays an input form with patient attributes filled in
    and handls the form submission to update a patient in the db
    ''' 
    model = Patient
    fields = ['dob', 'first_name', 'last_name', 'basal_dose']
    template_name_suffix = '_update'

    def get_success_url(self):
        pk = self.kwargs['pk']
        model = get_object_or_404(self.model, pk=pk)
        p_id = model.id
        return(reverse('logger:PatientDetailView', args=[p_id]))
    
class PatientDeleteView(SiteView, DeleteView):
    model = Patient
    success_url = reverse_lazy('logger:PatientListView')
  
class PatientCreateView(SiteView, CreateView):
    model = Patient
    fields = ['dob', 'first_name', 'last_name',  'basal_dose']
    success_url = reverse_lazy('logger:ProfileView')
    template_name_suffix = "_create"
    
    def form_valid(self, form):
         user = self.request.user
         form.instance.user = user
         return super(PatientCreateView, self).form_valid(form)
         
class GraphView(SiteView, DetailView):
  model = Patient
  template_name_suffix = "_graphs"

