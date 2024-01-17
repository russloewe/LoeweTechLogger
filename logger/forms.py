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

from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import  login, logout, authenticate
from django.core.exceptions import ValidationError
from .models import Patient, Log, Dose, ExpressToken
import datetime

this_year = datetime.date.today().year
BIRTH_YEAR_CHOICES = [ str(year) for year in range(this_year, this_year-99, -1)]
# DAYS_OF_WEEK = (
    # (0, 'Monday'),
    # (1, 'Tuesday'),
    # (2, 'Wednesday'),
    # (3, 'Thursday'),
    # (4, 'Friday'),
    # (5, 'Saturday'),
    # (6, 'Sunday'),
# )


class LogForm(forms.ModelForm):
    class Meta:
        model = Log
        fields = ["date", "bloodsugar", "carbs", "insulin", "basal",  "patient", "user", "notes", "direction"]
        widgets = {
            'patient': forms.HiddenInput,
            'user': forms.HiddenInput
            }

    
    basalcheck_attrs = {'class': 'custom-control-input',
                    'data-toggle': 'collapse',
                    'data-target': '#bas',
                    'aria-controls':'collapseBas',
                    'aria-expanded': 'false'}
    basal_attrs = {'class': 'form-control',
                   'aria-controls': 'collapseBas'}
    form_control_class = {'class': 'form-control'}
    
    # patient = forms.IntegerField(label="patient", 
      # widget=forms.HiddenInput())

    date = forms.DateTimeField(label="Datetime", required=True,
      widget=forms.DateTimeInput(attrs={'placeholder':'Datetime (yyyy/mm/dd hh:mm', 'class': 'date'}))
    
    bloodsugar = forms.IntegerField(label="Bloodsugar", required=False,
      widget=forms.NumberInput(attrs={'placeholder': "Bloodsugar (mg/dL)", 'class': 'bloodsugar'}))
    
    carbs = forms.IntegerField(label="Carbs", required=False,
      widget=forms.NumberInput(attrs={'placeholder' : 'Carbs (g)', 'class': 'carbs'}))
      
    notes = forms.CharField(label="notes", required=False, 
        widget=forms.TextInput(attrs={'placeholder': 'Notes', 'class': 'notes'}))
    
    insulin = forms.FloatField(label="Insulin", required=False,
      widget=forms.NumberInput(attrs={'placeholder': 'Insulin (units)', 'class': 'insulin'}))
    
    # steps = forms.IntegerField(label="Steps", required=False,
      # widget=forms.NumberInput(attrs={'placeholder': 'Steps', 'class': 'steps'}))
      
    basal = forms.IntegerField(label="Basal", required=False,
      widget=forms.NumberInput(attrs={'placeholder': 'Basal', 'class': 'basal'}))
    

    def as_div(self):
      "Return this form rendered as HTML <div>s."
      return self._html_output(
          normal_row='''<div class="d-flex flex-row p-2"%(html_class_attr)s>
                          <div class="col-1 "><h4>%(label)s</h4></div>
                          <div class="col input-lg"> %(field)s%(help_text)s</div>
                        </div>''',
          error_row='%s',
          row_ender='</div>',
          help_text_html=' <span class="helptext">%s</span>',
          errors_on_separate_row=True,
      )

class UpdateLogForm(forms.ModelForm):
  class Meta:
    model = Log
    fields = '__all__'
    widgets = {
  #    'patient': forms.HiddenInput,
   #   'user': forms.HiddenInput
    }


class UploadCSVForm(forms.Form):
    csv_file = forms.FileField()
    
class DoseForm(forms.ModelForm):
    class Meta:
        model = Dose
        fields = ['patient', 'label',  'start', 'end', 'carb_ratio', 'correction_start', 'correction_step', 'active', 
                  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        widgets = {
            'patient': forms.HiddenInput}

class UserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email']   
    
class PatientForm(forms.ModelForm):
  class Meta:
    model = Patient
    fields = ['dob', 'first_name', 'last_name',  'basal_dose']
    labels = {'dob': "Date of Birth"}
    widgets = {'dob': forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES)}

class OtpForm(forms.Form):
    code = forms.CharField(label="Code")
    
class ExpressTokenForm(forms.Form):
    token = forms.CharField(label="token", widget=forms.HiddenInput)
     # class Meta:
        # model = ExpressAccessToken
        # fields = [ "token"]
        # #widgets = {'token': forms.HiddenInput()}

class ExpressLogForm(LogForm, ExpressTokenForm):
    '''
        form to add new log using express access token.
    '''

class LoginForm(forms.Form):
    username = forms.CharField(label = 'Username')
    password = forms.CharField(label='Enter password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = authenticate(username = username,  password = password)
        if user is  None:
          #  login(request, user)
            raise ValidationError(
                "Invalid username or password "
                )

class LinkUserForm(forms.Form):
  username = forms.CharField(label = 'Username')
  
  def clean_username(self):
    username = self.cleaned_data['username'].lower()
    r = User.objects.filter(username=username)
    if r.count() != 1:
        raise  ValidationError("Username not found.")
    return r[0]

class UnlinkUserForm(forms.ModelForm):
  def __init__(self, *args, **kwargs):
    super(UnlinkUserForm, self).__init__(*args, **kwargs)
    self.fields['connected'] = forms.ModelChoiceField(
            queryset=self.instance.connected.all(),
            label="Choose user account to disconnect:" )

  class Meta:
    model = Patient
    fields = ['connected']

 
  
class ImportForm(forms.Form):
  date_col = forms.CharField(label = 'date column', max_length = 50)
  
class ExportForm(forms.Form):
  output = forms.CharField(label = 'output', max_length=50)
  

class PasswordForm(forms.Form):
  password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
  password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

  def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2



class CustomUserCreationForm(forms.Form):
    username = forms.CharField(label='Enter Username', min_length=4, max_length=150)
    email = forms.EmailField(label='Enter email')
    password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        r = User.objects.filter(username=username)
        if r.count():
            raise  ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        r = User.objects.filter(email=email)
        if r.count():
            raise  ValidationError("Email already exists")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

    def save(self, commit=True):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password1']
        )
        return user
