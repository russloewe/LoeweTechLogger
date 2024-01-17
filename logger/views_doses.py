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
import string
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from .models import Dose
from .forms import DoseForm
from .views import SiteView, GenericPatientItem, PatientItemListCreateView

    
#DOSE CARD VIEWS
class DoseListView(PatientItemListCreateView):
    model = Dose
    form = DoseForm
    order_by = 'id'
    list_url_name = 'logger:DoseListView'

class DoseCreateView(GenericPatientItem,  CreateView):
    model = Dose
    fields = '__all__'
    list_url_name = 'logger:DoseListView'
    template_name_suffix = '_new'

class DoseDeleteView(GenericPatientItem,  DeleteView):
    model = Dose
    list_url_name = 'logger:DoseListView'
    
        
class DoseUpdateView(GenericPatientItem, UpdateView):
    model = Dose
    list_url_name = 'logger:DoseListView'
    
        
class DoseUpdateView(GenericPatientItem, UpdateView):
    model = Dose
    fields = ['label', 'start', 'end', 'carb_ratio', 'correction_start', 'correction_step', 'active', 
                  'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    list_url_name = 'logger:DoseListView'
    template_name_suffix = '_update'
    
