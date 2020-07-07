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


    datetime = forms.DateTimeField(label="Log Datetime", required=True,
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
    
    
class PatientForm(forms.Form):
    dob = forms.DateField(label="DOB")
    first_name = forms.CharField(label='first name', max_length=100)
    last_name = forms.CharField(label='last_name', max_length=100)
    carb_ratio = forms. IntegerField(label="carb ratio")
    correction_start = forms.IntegerField(label='correction start')
    correction_step = forms.IntegerField(label='correction step')
    basal_dose = forms.IntegerField(label='basal dose')
    
    
class ProfileForm(forms.Form):
  email = forms.EmailField(label = 'Email')
  
class ImportForm(forms.Form):
  date_col = forms.CharField(label = 'date column', max_length = 50)
  
class ExportForm(forms.Form):
  output = forms.CharField(label = 'output', max_length=50)
  
class SignupForm(forms.Form):
  email = forms.EmailField(label = 'Email')
  first_name = forms.CharField(label="First Name")
  last_name = forms.CharField(label="Last Name")

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
    
