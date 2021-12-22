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

'''
    GAMEPLAN: All time is kept as Python datetime objects until
    rendered into chart in this class. That should keep things 
    consistant
'''

from django.utils import timezone
from datetime import datetime, timedelta

def ordinal(time):
  diff = time - timezone.now()
  total_minutes = diff.total_seconds() / 60
  return(total_minutes)

class Chart(object):
    height = 500
    width = 800
    chartWidth = 4*60
    chart = '''<svg class="p-0 m-0" style="width: 100%;overflow: hidden" xmlns="http://www.w3.org/2000/svg"
                         width="800px" height="500px"
                         viewBox="0 0 800 500">
                    <path id="background" fill="white" stroke="none" 
                            d="M 0,0 800,0 800,500 0,500 Z"/>
                            
                     <path id="low" fill="red" stroke="none" 
                            d="M 0,500 800,500 800,420 0,420 Z"/>

                     <path id="high" fill="yellow" stroke="none" 
                            d="M 0,0 800,0 800,200 0,200 Z"/>
                     '''
                            
    def convertX(self, val):
        '''This is where the datetime object is converted to a 
            real number and mapped to the X range of the chart.'''
        x = ordinal(val) # Gives age in min relative to present
        x = (x / self.chartWidth)*self.width
        x = int(x)
        x = self.width + x
        return(x)        

        
    def convertY(self, val):
        ''' Y value is converted to y pixel coordinate on chart'''
        y = self.height - val
        y = int(y)
        return(y)
        
    def addLine(self, data, size=3, color='black'):
        line_template = '''<path id="line" fill="none" stroke="{}" stroke-width="{}"  d="M {} " />\n'''
        line_points = ''
        for x, y in data:
            x = self.convertX(x)
            y = self.convertY(y)
            line_points += " {},{} ".format(x,y)
        new_line = line_template.format(size, line_points)
        self.chart += new_line
    
    def addPoints(self, data_array, size=4, color='red'):
        point_template = '''<circle id="point{}" cx="{}" cy="{}" r="{}" stroke="none" stroke-width="3" fill="{}" />\n'''
        counter = 0
        for x, y in data_array:
            x = self.convertX(x)
            y = self.convertY(y)
            new_point = point_template.format(counter, x, y, size, color)
            self.chart += new_point
            counter += 1

    
    def svg(self):
        
        self.chart += "</svg>"
        
        return self.chart
