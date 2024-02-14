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
from django.contrib.auth.models import User
from django.contrib.auth import  login, logout, authenticate
from django.core.exceptions import ValidationError
import datetime


class LoginForm(forms.Form):
    username = forms.CharField(label = 'Username')
    password = forms.CharField(label='Enter password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        user = authenticate(username = username,  password = password)
        if user is  None:
            raise ValidationError(
                "Invalid username or password "
                )

class PasswordForm(forms.Form):
  password1 = forms.CharField(label='Enter password', widget=forms.PasswordInput)
  password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

  def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            raise ValidationError("Password don't match")

        return password2

