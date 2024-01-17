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

from django.db import models
import pandas as pd
from datetime import datetime
import pytz
import math
from django.utils import timezone
from django.contrib.auth.models import User
# Create your models here.
import csv
from io import TextIOWrapper


DAYS_OF_WEEK = (
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
)

class Patient(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name="owner")
    connected = models.ManyToManyField(User, related_name="connected_users")
    dob = models.DateField('DOB')
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    basal_dose = models.IntegerField(default=0)
  
    def getDose(self):
        weekday = datetime.today().weekday()
        weekday_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][weekday]
        
        Doses = self.patient.all().filter(**{weekday_name: True})
        #Doses = self.Dose_set.filter(**{weekday_name: True})
        #Doses = self.Dose_set.filter(days = weekday)
        if len(Doses) >= 1: 
            now = datetime.now().time()
            
            for Dose in Doses:
               # days = [ i for i in Dose.days]              
                #raise Exception("day: {}".format(days))
                #raise Exception('{}-{}'.format(start, end))
                start = Dose.start
                end = Dose.end
                # if end == '00:00:00':
                    # end = '24:00:00'
                # raise Exception('{}-{}'.format(start, end))
                if now > start and now < end and Dose.active:
                    
                    return({'label' : Dose.label,
                                  'carb_ratio': Dose.carb_ratio,
                                  'correction_start': Dose.correction_start,
                                  'correction_step': Dose.correction_step,
                                  'basal_dose': self.basal_dose})
        return ({  'label': 'base',
                          'carb_ratio': 0,
                          'correction_start': 0,
                          'correction_step': 0,
                          'basal_dose': self.basal_dose})
    
    def getLogs(self):
      ''' Return an array of all logs associated with patient
          arranged by date, newest first
      '''
      logs = self.log_set.order_by('-date')
      non_steps = logs#[ log for log in filter(lambda x:  x.steps==None, logs )]
      return(non_steps[:40])
      
    def __str__(self):
        # self.graph = self.getGraphData()
        return("{} {} ({})".format(self.first_name, self.last_name, self.id))
    
    def lastDoseRelTime(self):
        current =  pd.Timestamp.today().tz_localize('America/Los_Angeles')
        logs = self.log_set.order_by('-date')
        for log in logs:
            if log.insulin:
                logtime = pd.to_datetime(log.date).tz_convert('America/Los_Angeles')
                delta = current - logtime
                if delta.days > 0:
                    return("More than a day")
                else:
                    hours = round(delta.seconds/(60*60))
                    minutes = math.floor((delta.seconds/60)%60)
                    return("{} hours {} min ago".format(hours, minutes))

class Dose(models.Model):
    active = models.BooleanField(default=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="patient")
    label = models.CharField(max_length=40)
    start = models.TimeField(null=True)
    end = models.TimeField(null=True)
    carb_ratio = models.IntegerField(default=0)
    correction_start = models.IntegerField(default=0)
    correction_step = models.IntegerField(default=0)
    
    Monday = models.BooleanField(default=False, null=True)
    Tuesday = models.BooleanField(default=False, null=True)
    Wednesday = models.BooleanField(default=False, null=True)
    Thursday = models.BooleanField(default=False, null=True)
    Friday = models.BooleanField(default=False, null=True)
    Saturday = models.BooleanField(default=False, null=True)
    Sunday = models.BooleanField(default=False, null=True)

    def __str__(self):
        return("Patient: {} {}, window: {}".format(self.patient.first_name, self.patient.last_name, self.label))

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_enabled = models.BooleanField('Enable Two Factor Auth', default=True)
    verified = models.BooleanField(default=False)
    cell_number = models.CharField(max_length=20, null=True, blank=True)
    
    def __str__(self):
        return("{}".format(self.user.username))

class Log(models.Model):
    DIRECTION_CHOICES = [
        ('fast_up', 'Fast Up'),
        ('up', 'Up'),
        ('slow_up', 'Slow Up'),
        ('steady', 'Steady'),
        ('slow_down', 'Slow Down'),
        ('down', 'Down'),
        ('fast_down', 'Fast Down'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField('Timestamp')
    notes = models.CharField(max_length=500, null=True, blank=True)
    insulin = models.FloatField(blank=True, null=True)
    carbs = models.FloatField(blank=True, null=True)
    bloodsugar = models.FloatField(blank=True, null=True)
    basalcheck = models.BooleanField(default=False)
    basal = models.FloatField(blank=True, null=True)
    steps = models.FloatField(blank=True, null=True)
    token_used = models.CharField(max_length=50, null=True, blank=True)
    direction = models.CharField(max_length=20, choices=DIRECTION_CHOICES, null=True, blank=True)
    
    class Meta:
            # This constraint is for the cron job that updates records
            # from fitbit
            unique_together = ('steps', 'date')
    
    def getJSDateTime(self):
        '''
            retun the datetime nicely formated for javascripts new Date
            object.
        '''
        # Get values from datetime object on log
        date = {'hour': self.date.hour,
            'minute': self.date.minute,
            'day': self.date.day,
            'month': self.date.month-1,
            'year': self.date.year,
            'tzname': self.date.tzname(),
            'timestamp': self.date.timestamp()*1000}
        return date
        
        
    def setDateFromForm(self, date, time):
        '''
            Set the date attribute of this object from 
            date and time strings from webform
            date: yy-mm-dd    time: hh:mm:ss (24 hrs)
        '''
        if len(date) < 8 or len(time) < 8:
            raise Exception
        year, month, day = map(int, date.split('-'))
        hour, minute, second = map(int, time.split(':'))
        date = datetime(year, month, day,
                                      hour, minute, second,
                                      tzinfo=pytz.UTC)
        self.date = date
        return date
        

    def __str__(self):
        ''' Format the date for the stats list '''
        # Get values from datetime object on log
        hour = self.date.hour
        minute = self.date.minute
        day = self.date.toordinal()
        year = self.date.year
        
        # Get values for today
        now = datetime.now()
        today = now.toordinal()
        this_hour = now.hour
        this_minute = now.minute

        # format day compontentordinal
        #if(day == today):
           # day = "Today"

        # Format month component
        months = ['Jan.', 'Feb.', 'Mar.', 'Apr.',  'May', 
                  'Jun.', 'Jul.', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.']
        month = months[self.date.month-1]
        month_day = '{} {}'.format(month, self.date.day)
        
        # format hour components
        ampm = ''
        if(hour > 12):
            hour = str(hour - 12 )
            ampm = "pm"
        elif(hour == 0):
            hour = str(12)
            ampm = "am"
        else:
            hour = str(hour)
            ampm = "am"
        
        # Format minute component
        if(minute < 10):
            minute = '0' + str(minute)
        text = "{}, {} at {}:{} {}".format(month_day, year, hour, minute, ampm)
        return(text)
    
    @classmethod
    def create_from_csv_row(cls, row, patient, user):
        
        # First double check that the user is the same
        csv_patient_id = int(row.get('patient_id'))
        patient_id = int(patient.id)
        
        if csv_patient_id == patient_id:
            date_str = row.get('date', '')
            date_obj = None
            try:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
            except:
                date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            
            field_mapping = {
                'date': row.get('date', ''),
                'notes': row.get('notes', ''),
                'insulin': row.get('insulin', ''),
                'carbs': row.get('carbs', ''),
                'bloodsugar': row.get('bloodsugar', ''),
                'basalcheck': row.get('basalcheck', ''),
                'basal': row.get('basal', ''),
                'steps': row.get('steps', ''),
                'token_used': row.get('token_used', ''),
                'direction': row.get('direction', ''),
            }

            # Replace empty strings with None
            for field, value in field_mapping.items():
                if value == '':
                    field_mapping[field] = None
                    
            #date_obj = date_obj.replace(tzinfo=pytz.UTC)
            # try:
            log = cls(
                patient=patient,
                user=user,
                date=date_obj,  
                notes=field_mapping['notes'],
                insulin=field_mapping['insulin'],
                carbs=field_mapping['carbs'],
                bloodsugar=field_mapping['bloodsugar'],
                basalcheck=field_mapping['basalcheck'],
                basal=field_mapping['basal'],
                steps=field_mapping['steps'],
                token_used=field_mapping['token_used'],
                direction=field_mapping['direction'],
            )
            log.save()
            return log
            # except:
                # return None
        else:
            return None

class ExpressToken(models.Model):
    ''' Holds data for the express access token which lets a user
        bypass logging in for limited access to a patient.
        Note: only the user that created the patient may create an 
        express token.
    '''
    created = models.DateTimeField(auto_now_add = True)
    last_modified = models.DateTimeField(auto_now = True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    label = models.CharField(max_length=40)
    token = models.CharField(max_length=40, unique=True)
    qr_img = models.CharField(max_length=5000, null=True, blank=True)
    qr_img_code = models.CharField(max_length=5000, null=True, blank=True)
    active =  models.BooleanField(default=True)
