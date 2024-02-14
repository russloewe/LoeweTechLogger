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


app_name = 'home'
urlpatterns = [
    # INDEX
    path('privacy_policy.html',  views.privacy, name='privacy'),
    path('terms_of_service.html',  views.terms, name='terms'),
    path('index.html', views.index, name='index'), 
    path('', views.index, name='index'), 
]
