#!/usr/bin/python3
import sys
import os
import time
import pytz
import subprocess
import time
import board
import csv


"""
Libraries of the sensors
"""
from DFRobot_MultiGasSensor import *
from  DFRobot_MICS import *
from DFRobot_SHT20 import *
from DFRobot_ENS160 import *
import mysql.connector
from datetime import datetime
import time
from gpiozero import CPUTemperature

# def get_RSSI():
#     result = subprocess.run(['iwconfig', 'wlan0'], capture_output=True, text=True)
#     output_lines = result.stdout.split('\n')
#     for line in output_lines:
#         if 'Quality' in line:
#             rssi_value = line.split('Signal level=')[-1].split(' ')[0]
#             print(f"RSSI Value: {rssi_value}")
#     return rssi_value


# Establish connection to MySQL
dataBase = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="iLoveTunnels69!",
    database="tunnel"
)

# Create a cursor object to execute SQL queries
cursor = dataBase.cursor()

# Define the SQL query to insert data into the table
# insert_query = """
# INSERT INTO tunnel_gas (created_at, column1, column2,column3, column4, column6,column7,column8,column9) VALUES (%s, %s, %s,%s,%s, %s,%s,%s,%s)
# """

insert_query = """
INSERT INTO tunnel_gas (created_at,column1, column3,column6,column8,column9,column10) VALUES (%s,%s,%s,%s,%s,%s,%s)
"""


I2C_1       = 0x01               # I2C_1 Use i2c1 interface (or i2c0 with configuring Raspberry Pi) to drive sensor

#Addresses of sensors
# CO_address = 0x77
O2_address = 0x77
mics_address = 0x76
SHT20_address = 0x40
ENS160_address = 0x53
H2S_address = 0x75
CALIBRATION_TIME = 0x03

# initializing the sensor variables
# CO = DFRobot_MultiGasSensor_I2C(I2C_1 ,CO_address)
O2 = DFRobot_MultiGasSensor_I2C(I2C_1,O2_address)
mics = DFRobot_MICS_I2C(I2C_1,mics_address)
SHT20 = DFRobot_SHT20(i2c_addr = SHT20_address,bus = 1)
H2S = DFRobot_MultiGasSensor_I2C(I2C_1 ,H2S_address)
ENS160 = DFRobot_ENS160_I2C(i2c_addr = ENS160_address, bus = 1)

current_time = time.strftime('%Y-%m-%d_%H-%M-%S')
filename = f"data_{current_time}.csv"
        
def setup():
        #CO and O2 multigas sensor setup
      #Mode of obtaining data: the main controller needs to request the sensor for data
    while (False == O2.change_acquire_mode(O2.INITIATIVE) and (False == H2S.change_acquire_mode(H2S.INITIATIVE)) ):
        print("wait acquire mode change!")
        time.sleep(1)
    print("change acquire mode success!")
    O2.set_temp_compensation(O2.ON)
    
#     CO.set_temp_compensation(CO.ON)
    H2S.set_temp_compensation(H2S.ON)

    
    
    #mics setup
    '''
    if mics.get_power_mode() == SLEEP_MODE:
        mics.wakeup_mode()
        print("wake up sensor success")
    else:
        print("the sensor is wake up mode")
    
    '''
    '''
    Do not touch the sensor probe when preheating the sensor.
    Place the sensor in clean air.
    The default calibration time is 3 minutes.
    
    
    mics.warm_up_time(CALIBRATION_TIME)
    time.sleep(1)
    '''
#     SHT20.check_SHT20
    
    #ENS160 setup
    while (ENS160.begin() == False):
        print ('Please check that the device is properly connected')
        time.sleep(3)
        print("sensor begin successfully!!!")

    ENS160.set_PWR_mode(ENS160_STANDARD_MODE)
    ENS160.set_temp_and_hum(ambient_temp=25.00, relative_humidity=50.00)
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["Timestamp\t", "O2_con(%)\t", "Temperature(F)\t","Methane(%)\t","CO2(ppm)\t","CPU_temp\t", "TVOC(ppb)\t","H2S(ppm)\n"])

    
  
def loop():
    
  start_time = time.time()
  # Gastype is set while reading the gas level. Must first perform a read before
  # attempting to use it.
  O2_con = O2.read_gas_concentration()
  print ("Ambient "+ O2.gastype + " concentration: %.2f " % O2_con + O2.gasunits + " temp: %.1fC" % O2.temp)
#   CO_con = CO.read_gas_concentration()
#   print ("Ambient "+ CO.gastype + " concentration: %.2f " % CO_con + CO.gasunits + " temp: %.1fC" % CO.temp)
  H2S_con = H2S.read_gas_concentration()
  print ("Ambient "+ H2S.gastype + " concentration: %.2f " % H2S_con + H2S.gasunits + " temp: %.1fC" % H2S.temp)
  

  '''
    Type of detection gas for the MICS module
    CO       = 0x01  (Carbon Monoxide)
    CH4      = 0x02  (Methane)
    C2H5OH   = 0x03  (Ethanol)
    H2       = 0x06  (Hydrogen)
    NH3      = 0x08  (Ammonia)
    NO2      = 0x0A  (Nitrogen Dioxide)
  '''
  
  ###MICS reading
  '''
  mics_con = mics.get_gas_ppm(0x02)
  print("gas concentration is %.1f"%mics_con)
  '''
  #SHT20 reading
   #humidity = SHT20.read_humidity
  temp = O2.temp
#   print("Humidity: %.1f %%" %(humidity))
#   print("Temperature : %.1f C" %(temp))
  '''
  
  
    ENS160 reading
    # Get CO2 equivalent concentration calculated according to the detected data of VOCs and hydrogen (eCO2 – Equivalent CO2)
    # Return value range: 400–65000, unit: ppm
    # Five levels: Excellent(400 - 600), Good(600 - 800), Moderate(800 - 1000), 
    #               Poor(1000 - 1500), Unhealthy(> 1500)
    '''
  """
    FIND VOC
    """
  CO2_con = ENS160.get_ECO2_ppm
  VOC_con = ENS160.get_TVOC_ppb
  
  print("Carbon dioxide equivalent concentration : %u ppm" %(CO2_con))
  print("VOC concentration: %u ppb" %(VOC_con))
  cpu_temp = CPUTemperature()

  temperature_value = cpu_temp.temperature
  # Convert the temperature value to a float
  CPU_temp = float(temperature_value)

  
  # Convert local time to UTC
  utc_time = datetime.now().astimezone(pytz.utc)
  # Format the UTC time as a string
  
  utc_time_str = utc_time.strftime('%Y-%m-%d %H:%M:%S')
  # Now you can use utc_time_str in your data tuple
#   rssi = get_RSSI()
  data = [(utc_time_str,O2_con,temp,CO2_con,CPU_temp,VOC_con,H2S_con)]
  print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
  # Replace with your actual data
  # Execute the SQL query to insert data into the table
  cursor.executemany(insert_query, data)
  # Commit the transaction
  dataBase.commit()
  
  # Write data to CSV file
  with open(filename, 'a', newline='') as csvfile:
      csvwriter = csv.writer(csvfile)
      # Write data row
      csvwriter.writerow([str(utc_time_str)+"\t",str(O2_con)+"\t",str(temp)+"\t",str(CO2_con)+"\t",str(CPU_temp)+"\t",str(VOC_con)+"\t",str(H2S_con)])
  # Close the cursor and database connection
  end_time = time.time()

  
  
  time.sleep(5-(end_time-start_time))
 
if __name__ == "__main__":
    setup()
    try:
        while True:
            loop()
    except KeyboardInterrupt:
        cursor.close()
        dataBase.close()

