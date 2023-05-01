from flask import Flask, render_template, request, redirect , jsonify
from flask_mysqldb  import MySQL
import plotly.graph_objs as go
from datetime import datetime , timedelta , time
import array
import logging
import numpy as np
app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '46045'
app.config['MYSQL_DB'] = 'CBBMS_DB'
mysql = MySQL(app)
logging.basicConfig(filename='example.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')

@app.route('/')
def home():
	return render_template('index.html',chart=chart())

def battery_status():
	cur = mysql.connection.cursor()
	cur.execute('''SELECT current FROM modules_current ORDER BY ID DESC LIMIT 1 ''')
	data = cur.fetchone()
	cur.close()
	if data[0] > 0 :
		return "Discharging"
	else:
		return "Charging"

def current_capacity():
	return round((10050*get_state_of_charge())/1000,2)

def rated_capacity ():
	return 10.05

def state_of_charge():
	return round(get_state_of_charge()*100,2)

def state_of_health():
	cur = mysql.connection.cursor()
	cur.execute('''SELECT SOH  FROM modules_state_of_health  ORDER BY ID DESC LIMIT 1 ''')
	data = cur.fetchone()
	cur.close()
	return round(data[0]*100,2)

def distance_to_reach():
	return round((current_capacity()*24*4.8)/1000,2)

def get_state_of_charge():
	cur = mysql.connection.cursor()
	cur.execute('''SELECT SOC  FROM modules_state_of_charge  ORDER BY ID DESC LIMIT 1 ''')
	data = cur.fetchone()
	cur.close()
	return data[0]

def is_current_sensor_defect():
	cur = mysql.connection.cursor()
	cur.execute('''SELECT current_sensor_error FROM error_codes  ORDER BY ID DESC LIMIT 1 ''')
	data = cur.fetchone()
	cur.close()
	if data[0] == 1:
		return True
	else:
		return False
def is_voltage_sensor_defect():
	cur = mysql.connection.cursor()
	cur.execute('''SELECT voltage_sensor_error FROM error_codes  ORDER BY ID DESC LIMIT 1 ''')
	data = cur.fetchone()
	cur.close()
	if data[0] in [3,4,5,6,7]:
		return True
	else:
		return False

def is_heat_system_defect():
        cur = mysql.connection.cursor()
        cur.execute('''SELECT heat_sys_error FROM error_codes  ORDER BY ID DESC LIMIT 1 ''')
        data = cur.fetchone()
        cur.close()
        if data[0] == 9:
                return True
        else:
                return False

def is_cool_system_defect():
        cur = mysql.connection.cursor()
        cur.execute('''SELECT cool_sys_error FROM error_codes  ORDER BY ID DESC LIMIT 1 ''')
        data = cur.fetchone()
        cur.close()
        if data[0] == 11:
                return True
        else:
                return False

def is_cell_defect():
        cur = mysql.connection.cursor()
        cur.execute('''SELECT cell_error FROM error_codes  ORDER BY ID DESC LIMIT 1 ''')
        data = cur.fetchone()
        cur.close()
        if data[0] in [13,14,15,16,17,18,19]:
                return True
        else:
                return False

def chart():
	cur = mysql.connection.cursor()
	#get the data that was retrieved the last day recorded in the table 
	cur.execute('''SELECT SOC from modules_state_of_charge WHERE timestamp >  \
	(select timestamp from modules_state_of_charge order by timestamp DESC LIMIT 1) - INTERVAL 48 HOUR ''')
	data= cur.fetchall()
	soc=list(data)
	cur.execute('''SELECT TIME(timestamp) from modules_state_of_charge WHERE timestamp >  \
	(select timestamp from modules_state_of_charge order by timestamp DESC LIMIT 1) - INTERVAL 48 HOUR ''')
	data = cur.fetchall() 
	# Convert the tuple to an array of datetime objects
	timeStr=[]
	for row in data:
		logging.info("times : "+str(row[0]))
		
		delta=row[0]		
		timeStr.append(str(delta))	
	
	
 
	cur.close()
	x = [ 00.00, 1.00, 2.00, 3.00, 4.00, 5.00, 6.00, 7.00, 8.00, 9.00, 10.00, 11.00, 12.00, 13.00, 14.00, 15.00, 16.00, 17.00, 18.00, 19.00, 20.00, 21.00, 22.00, 23.00]
	y = [39, 55, 70, 86, 99, 100, 100, 80,70,70, 70, 70, 69, 69, 80, 90, 100, 79, 48, 15, 30, 46, 61, 78 ]
	y_modified = [val + 10 for val in y]
	# Create the chart using Plotly
	trace = go.Scatter(x=x, y=y)
	data = [trace]
	layout = go.Layout(xaxis={'title':'time (h)'} , yaxis={'title':'State Of Charge (%)'})
	fig = go.Figure(data=data, layout=layout)
	chart = fig.to_html(full_html=False)
	return chart
def convertTuple(tup):
	# initialize an empty string
	str = ''
	for item in tup:
		str = str + item
	return str
@app.route('/get_value')
def read_database():
	batteryStatus = battery_status()
	currentCapacity = current_capacity()
	ratedCapacity = rated_capacity() 
	soc = state_of_charge()
	soh = state_of_health()
	distanceToReach = distance_to_reach()
	isCurrentSensorDefect = is_current_sensor_defect()
	isVoltageSensorDefect = is_voltage_sensor_defect()
	isHeatSysDefect = is_heat_system_defect()
	isCoolSysDefect = is_cool_system_defect()
	isCellDefect = is_cell_defect()
	return jsonify({'BatteryStatus': batteryStatus , 'CurrentCapacity': currentCapacity , 'RatedCapacity': ratedCapacity ,'SOC':soc , 'SOH':soh , 'DistanceToReach': distanceToReach 
		, 'IsCurrentSensorDefect':isCurrentSensorDefect , 'IsVoltageSensorDefect':isVoltageSensorDefect , 'IsHeatSysDefect':isHeatSysDefect , 'IsCoolSysDefect':isCoolSysDefect, 
		'IsCellDefect':isCellDefect})

if __name__ == "__main__":
    app.run(debug=True , host="0.0.0.0" ,port=5555)
