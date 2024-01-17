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

#from graphene_django.views import GraphQLView
#from myapp.schema import schema

from django.urls import path, include
from . import views, views_express, views_doses, views_patients, views_logs, views_profiles



app_name = 'logger'
urlpatterns = [
    # INDEX
    path('', views.index, name='index'), # Landing page for all
    
    # LOGS
    path('patient/<int:pk>/logs', views_logs.LogListCreateView .as_view(), name='LogListCreateView'),
    path('log/<int:pk>/', views_logs.LogDetailView.as_view(), name='LogDetailView'),
    path('log/<int:pk>/update/', views_logs.LogUpdateView.as_view(), name='LogUpdateView'),
    path('log/<int:pk>/delete/', views_logs.LogDeleteView.as_view(), name='LogDeleteView'),
    path('patient/<int:pk>/export', views_logs.LogExportView.as_view(), name='PatientLogExportView'),
    
    # PATIENTS  
   # path('patient/<int:pk>/', views.LogListCreateView.as_view(), name="LogListCreateView"),
    path('patient/<int:pk>/details', views_patients.PatientDetailView.as_view(), name="PatientDetailView"),
    path('patient/<int:pk>/graphs/', views_patients.GraphView.as_view(), name='GraphView'),
    path('patient/<int:pk>/link', views_patients.PatientLinkView.as_view(), name="PatientLinkView"),
    path('patient/<int:pk>/unlink', views_patients.PatientUnlinkView.as_view(), name="PatientUnlinkView"),
    path('patient/<int:pk>/update/', views_patients.PatientUpdateView.as_view(), name="PatientUpdateView"),
    path('patient/<int:pk>/delete', views_patients.PatientDeleteView.as_view(), name="PatientDeleteView"),
    path('patient/create/', views_patients.PatientCreateView.as_view(), name="PatientCreateView"),
    path('patient/list/', views_patients.PatientListView.as_view(), name="PatientListView"),
    
    #DOSE WINDOWS
    path('patient/<int:pk>/doses', views_doses.DoseListView.as_view(), name="DoseListView"),
    path('Dose/<int:pk>/delete', views_doses.DoseDeleteView.as_view(), name="DoseDeleteView"),
    path('Dose/<int:pk>/update', views_doses.DoseUpdateView.as_view(), name="DoseUpdateView"),
    path('Dose/<int:pk>/create', views_doses.DoseCreateView.as_view(), name="DoseCreateView"),
    
    # Express Access --- rename Express/ to Express/login or something
    path('express/', views_express.ExpressView.as_view(), name="ExpressView"),
    path('express/add',   views_express.ExpressAddView.as_view(), name="ExpressAddView"),
    path('express/add/confirm', views_express.ExpressAddConfirmView.as_view(), name="ExpressAddConfirmView"),

    # USER 
    path('user/login/',    views.LoginView.as_view(),    name="LoginView"),
    path('user/logout/',   views.LogoutView.as_view(),   name="LogoutView"),
    path('user/register/', views.RegisterView.as_view(), name="RegisterView"),
    
    # PROFILE    
    path('profile/',                views_profiles.ProfileView.as_view(),               name="ProfileView"),
    path('profile/update/',         views_profiles.ProfileUpdateView.as_view(),         name="ProfileUpdateView"),
    path('profile/update/password', views_profiles.ProfileUpdatePasswordView.as_view(), name="ProfileUpdatePasswordView"),
    path('profile/settings',        views_profiles.ProfileSettingsView.as_view(),       name="ProfileSettingsView"),
    path('profile/settings/update', views_profiles.ProfileSettingsUpdateView.as_view(), name='ProfileSettingsUpdateView'),
    
    # DATA
    path('export/<int:pk>/export.csv', views.ExportView.as_view(), name="ExportView"),
    path('import/', views.ImportView.as_view(), name='ImportView'),
    path('import/csv/<int:pk>', views.UploadCSV.as_view(), name='upload_csv'),
]
