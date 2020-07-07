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

from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views



app_name = 'logger'
urlpatterns = [
    # INDEX
    path('', views.index, name='index'), # Landing page for all
    # LOGS
    path('log/<int:pk>/', views.LogView.as_view(), name='LogView'),
    path('log/<int:pk>/update/', views.LogUpdateView.as_view(), name='LogUpdateView'),
    path('log/<int:pk>/delete/', views.LogDeleteView.as_view(), name='LogDeleteView'),
    path('log/<int:pid>/', views.LogView.as_view(), name='LogView'),
    # PATIENTS  
    path('patient/<int:pk>/', views.PatientView.as_view(), name="PatientView"),
    path('patient/<int:pk>/update/', views.PatientUpdateView.as_view(), name="PatientUpdateView"),
    # USER 
    path('login/', views.LoginView.as_view(), name="LoginView"),
    path('login/<str:next>', views.LoginView.as_view(), name="LoginView"),
    path('logout/', views.Logout, name="LogoutView"),
    # PROFILE
    path('signup/', views.SignUpView.as_view(), name="SignUpView"),
    # DATA
    path('export/', views.ExportView.as_view(), name="ExportView"),
    path('import/', views.ImportView, name='ImportView'),
]
