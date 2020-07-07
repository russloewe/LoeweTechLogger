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
from datetime import datetime
import pytz
from django.utils import timezone
from django.contrib.auth.models import User
from .plots import ordinal
# Create your models here.

class PendingUser(models.Model):
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    email = models.CharField(max_length=100)

    
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    patients = models.TextField(default='')
    
    def getPatients(self):
      ''' Return array of patient objects'''
      patients = self.getPatientIds()
      pat_out = []
      for patientid in patients:
        pat_out.append(Patient.objects.get(id = patientid))
      return(pat_out)
      
    def getPatientIds(self):
        '''Return array of patient objects'''
        if len(self.patients) > 0:
            patients = self.patients.split(';')
            test = lambda x : False if x == ' ' or x == '' else True
            patients = [p for p in map(int, filter(test, patients))]
            return(patients)
        else:
            return([])
            
    def addPatient(self, patientObj):
        '''Add patient to user profile
            returns false if user already in profile'''
        patients = self.patients.split(';')
        if patientObj.id not in patients:
            patients.append(str(patientObj.id))
            self.patients = ';'.join(patients)
        else:
            return(False)
            
    def removePatient(self, p):
        ''' removes patient
            Be sure to call '''
        patients = self.patients.split(';')
        patients.remove(str(p.id))
        self.patients = ';'.join(patients)
        
        

    def __str__(self):
        return("{}".format(self.user))
    
class Patient(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    dob = models.DateField('DOB')
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=40)
    carb_ratio = models.IntegerField(default=0)
    correction_start = models.IntegerField(default=0)
    correction_step = models.IntegerField(default=0)
    basal_dose = models.IntegerField(default=0)
    

    def as_dict(self):
      ''' Return a dict for passing to a Form'''
      return({'dob': self.dob,
              'first_name': self.first_name,
              'last_name': self.last_name,
              'carb_ratio': self.carb_ratio,
              'correction_start': self.correction_start,
              'correction_step': self.correction_step,
              'basal_dose': self.basal_dose})
    
    def logstodict(self, cutoff=-6*60):
      ''' return logs as list of tuples (time, val) where 
          time is in minutes relative to present
      '''
      
      logs = self.getLogs()
      bloodsugar = []
      insulin = []
      basal = []
      
      for log in logs:
        age = ordinal(log.date)
        if age > cutoff:
          if log.bloodsugar:
            bloodsugar.append((age, log.bloodsugar))
          if log.insulin:
            insulin.append((age, log.insulin))

      return({'bloodsugar': bloodsugar,
              'insulin' : insulin,
 })
        
    
    def getBG(self):
      '''return bloodsugar logs as data series'''
      logs = self.log_set.order_by('date')
      if logs == None or len(logs) < 1:
        return(None)
      data = []
      for log in logs:
        if(log.bloodsugar) and (log.bloodsugar > 0):
          data.append((log.date, log.bloodsugar))
      return(data)
    
    def getLogs(self):
      ''' Return an array of all logs associated with patient
          arranged by date, newest first
      '''
      logs = self.log_set.order_by('-date')
      return(logs)
      
    def getLogsRev(self):
        logs = self.log_set.order_by('date')
        
    def __str__(self):
        return("{} {} ({})".format(self.first_name, self.last_name, self.id))

    def lastCarbs(self):
        ''' Return min since last carbs '''
        logs = self.getLogs()
        for log in logs:
          if log.carbs > 0:
            return log
        return None
    
    def lastInsulin(self):
        ''' Return the last fast acting insulin log '''
        logs = self.getLogs()
        for log in logs:
          if log.insulin:
            self.lastInsulin = log
            return log
        return None
        
    def lastBasal(self):
        ''' Return last basal insulin log '''
        logs = self.getLogs()
        for log in logs:
          if log.basal:
            self.lastBasal = log
            return log
        return None
        
    def lastBloodsugar(self):
        ''' Return last log with bloodsugar '''
        logs = self.getLogs()
        for log in logs:
          if log.bloodsugar:
            self.lastBloodsugar = log
            return log
        return None
        
class Log(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, default=2)
    date = models.DateTimeField('timestamp')
    insulin = models.FloatField(default=0, null=True)
    carbs = models.FloatField(default=0, null=True)
    bloodsugar = models.FloatField(default=0, null=True)
    basalcheck = models.BooleanField(default=False)
    basal = models.FloatField(default=0, null=True)
    steps = models.FloatField(default=0, null=True)
    
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

        # format day compontent
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