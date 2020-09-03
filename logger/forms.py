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
from django.core.exceptions import ValidationError
from .models import Patient
import datetime

this_year = datetime.date.today().year
BIRTH_YEAR_CHOICES = [ str(year) for year in range(this_year, this_year-99, -1)]

class LogForm(forms.Form):
    datetime_attrs = {}
    bg_attrs = {'style':'background: #ffaaaa',
                'class': 'form-control',
                'onchange':'update_bg()',
                'onkeyup': 'update_bg()'}
    carbs_attrs = {'style':'background: #aaffaa',
                  'class': 'form-control',
                  'onchange': 'update_carbs()',
                  'onkeyup': 'update_carbs()'}
    insulin_attrs = {'style':'background: #aaaaff',
                    'class': 'form-control'}
    basalcheck_attrs = {'style':'background: #aaaaaa',
                    'class': 'custom-control-input',
                    'data-toggle': 'collapse',
                    'data-target': '#bas',
                    'aria-controls':'collapseBas',
                    'aria-expanded': 'false'}
    steps_attrs = {'style':'background: #ffffaa',
                   'class': 'form-control'}
    basal_attrs = {'style': 'background: #aaaaaa',
                   'class': 'form-control',
                   'aria-controls': 'collapseBas'}


    patient = forms.IntegerField(label="patient", 
      widget=forms.HiddenInput())

    datetime = forms.DateTimeField(label="Log Datetime", required=False,
      widget=forms.DateTimeInput(attrs=datetime_attrs))
    
    bloodsugar = forms.IntegerField(label="Bloodsugar", required=False,
      widget=forms.NumberInput(attrs=bg_attrs))
    
    carbs = forms.IntegerField(label="Carbs", required=False,
      widget=forms.NumberInput(attrs=carbs_attrs))
    
    insulin = forms.FloatField(label="Insulin", required=False,
      widget=forms.NumberInput(attrs=insulin_attrs))
    
    basalcheck = forms.BooleanField(label="Basal", required=False,
      widget=forms.CheckboxInput(attrs=basalcheck_attrs))
    
    steps = forms.IntegerField(label="Steps", required=False,
      widget=forms.NumberInput(attrs=steps_attrs))
      
    basal = forms.IntegerField(label="dose", required=False,
      widget=forms.NumberInput(attrs=basal_attrs))
    

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

class UserForm(forms.ModelForm):
  class Meta:
    model = User
    fields = ['first_name', 'last_name', 'email']   
    
class PatientForm(forms.ModelForm):
  class Meta:
    model = Patient
    fields = ['dob', 'first_name', 'last_name', 'carb_ratio', 'correction_start', 'correction_step', 'basal_dose']
    labels = {'dob': "Date of Birth"}
    widgets = {'dob': forms.SelectDateWidget(years=BIRTH_YEAR_CHOICES)}

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