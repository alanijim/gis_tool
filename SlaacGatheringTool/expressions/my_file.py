"""
Define new functions using @qgsfunction. feature and parent must always be the
last args. Use args=-1 to pass a list of values as arguments
"""

from qgis.core import *
from qgis.gui import *

@qgsfunction(args='auto', group='Custom')
def area_format(value1, feature, parent):
	value = feature.geometry().area()
	trigger=100
	unit = 'm2'
	if(value > trigger):
		value = value / 10000
		value = round(value,2)
		unit = 'ha'
	else:
		value = round(value,2)
	return "{:,} {}".format(value,unit)
