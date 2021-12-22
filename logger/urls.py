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
from . import views, rest_views



app_name = 'logger'
urlpatterns = [
    # INDEX
    path('', views.index, name='index'), # Landing page for all
    #Rest
    path('api/logs/' , rest_views.LogList.as_view()), 
    # LOGS
    path('log/<int:pk>/', views.LogView.as_view(), name='LogView'),
    path('log/create/<int:pk>/', views.LogCreateView.as_view(), name='LogCreateView'),
    path('log/<int:pk>/update/', views.LogUpdateView.as_view(), name='LogUpdateView'),
    path('log/<int:pk>/delete/', views.LogDeleteView.as_view(), name='LogDeleteView'),
    
    # PATIENTS  
    path('patient/<int:pk>/', views.PatientView.as_view(), name="PatientView"),
    path('patient/<int:pk>/details', views.PatientDetailView.as_view(), name="PatientDetailView"),
    path('patient/<int:pk>/link', views.PatientLinkView.as_view(), name="PatientLinkView"),
    path('patient/<int:pk>/unlink', views.PatientUnlinkView.as_view(), name="PatientUnlinkView"),
    path('patient/<int:pk>/update/', views.PatientUpdateView.as_view(), name="PatientUpdateView"),
    path('patient/<int:pk>/delete', views.PatientDeleteView.as_view(), name="PatientDeleteView"),
    path('patient/create/', views.PatientCreateView.as_view(), name="PatientCreateView"),
    path('patient/list/', views.PatientListView.as_view(), name="PatientListView"),
    
    # USER 
    path('user/login/', views.LoginView.as_view(), name="LoginView"),
    path('user/logout/', views.LogoutView.as_view(), name="LogoutView"),
    path('user/register/', views.RegisterView.as_view(), name="RegisterView"),
    
    # PROFILE    
    path('profile/', views.ProfileView.as_view(), name="ProfileView"),
    path('profile/update/', views.ProfileUpdateView.as_view(), name="ProfileUpdateView"),
    path('profile/update/password', views.ProfileUpdatePasswordView.as_view(), name="ProfileUpdatePasswordView"),
    
    # DATA
    path('export/', views.ExportView.as_view(), name="ExportView"),
    path('import/', views.ImportView, name='ImportView'),
]
