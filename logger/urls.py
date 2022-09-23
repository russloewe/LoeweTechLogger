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
from . import views, rest_views, express_views



app_name = 'logger'
urlpatterns = [
    # INDEX
    path('', views.index, name='index'), # Landing page for all
    
    # GRAPHQL ENDPOINT
    #path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    
    #Rest
    path('api/logs/' , rest_views.LogList.as_view()), 
    path('api/log/<int:pk>', rest_views.LogUpdateView.as_view()),
    path('api/status', rest_views.ServerStatus.as_view()),
    path('api/logs/nosteps' , rest_views.LogListNoSteps.as_view()), 
    path('api/fitbit/redirect', rest_views.FitbitRedirectEndpoint.as_view()),
    
    # LOGS
    path('patient/<int:pk>/logs', views.LogListCreateView .as_view(), name='LogListCreateView'),
    path('log/<int:pk>/', views.LogDetailView.as_view(), name='LogDetailView'),
    path('log/<int:pk>/update/', views.LogUpdateView.as_view(), name='LogUpdateView'),
    path('log/<int:pk>/delete/', views.LogDeleteView.as_view(), name='LogDeleteView'),
    
    # PATIENTS  
   # path('patient/<int:pk>/', views.LogListCreateView.as_view(), name="LogListCreateView"),
    path('patient/<int:pk>/details', views.PatientDetailView.as_view(), name="PatientDetailView"),
    path('patient/<int:pk>/graphs/', views.GraphView.as_view(), name='GraphView'),
    path('patient/<int:pk>/link', views.PatientLinkView.as_view(), name="PatientLinkView"),
    path('patient/<int:pk>/unlink', views.PatientUnlinkView.as_view(), name="PatientUnlinkView"),
    path('patient/<int:pk>/update/', views.PatientUpdateView.as_view(), name="PatientUpdateView"),
    path('patient/<int:pk>/delete', views.PatientDeleteView.as_view(), name="PatientDeleteView"),
    path('patient/create/', views.PatientCreateView.as_view(), name="PatientCreateView"),
    path('patient/list/', views.PatientListView.as_view(), name="PatientListView"),
    
    #DOSE WINDOWS
    path('patient/<int:pk>/dosewindows', views.DoseWindowListCreateView.as_view(), name="DoseWindowListCreateView"),
    path('dosewindow/<int:pk>/delete', views.DoseWindowDeleteView.as_view(), name="DoseWindowDeleteView"),
    path('dosewindow/<int:pk>/update', views.DoseWindowUpdateView.as_view(), name="DoseWindowUpdateView"),
    
    # Express Access --- rename expressaccess/ to expressaccess/login or something
    path('expressaccess/', express_views.ExpressAccessView.as_view(), name="ExpressAccessView"),
    path('expressaccess/add', express_views.ExpressAccessAddView.as_view(), name="ExpressAccessAddView"),
    path('expressaccess/add/confirm', express_views.ExpressAccessAddConfirmView.as_view(), name="ExpressAccessAddConfirmView"),
    
    # OTP
    path('otp/<str:pk>', views.OtpView.as_view(), name="OtpView"),
    
    # USER 
    path('user/login/', views.LoginView.as_view(), name="LoginView"),
    path('user/logout/', views.LogoutView.as_view(), name="LogoutView"),
    path('user/register/', views.RegisterView.as_view(), name="RegisterView"),
    
    # PROFILE    
    path('profile/', views.ProfileView.as_view(), name="ProfileView"),
    path('profile/update/', views.ProfileUpdateView.as_view(), name="ProfileUpdateView"),
    path('profile/update/password', views.ProfileUpdatePasswordView.as_view(), name="ProfileUpdatePasswordView"),
    path('profile/settings', views.ProfileSettingsView.as_view(), name="ProfileSettingsView"),
    path('profile/settings/update', views.ProfileSettingsUpdateView.as_view(), name='ProfileSettingsUpdateView'),
    
    # DATA
    path('export/', views.ExportView.as_view(), name="ExportView"),
    path('import/', views.ImportView, name='ImportView'),
]
