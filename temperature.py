import usb.core
import usb.util
import time
from datetime import datetime
from influxdb import InfluxDBClient
import socket
client = InfluxDBClient('hostname',8086,'el-usb-rt','password','el-usb-rt', timeout=None)

current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
hostname = socket.gethostname()
# find our device
device = usb.core.find(idVendor=0x1781, idProduct=0x0ec4)
reattach = False
if device.is_kernel_driver_active(0):
 reattach = True
 device.detach_kernel_driver(0)
device.set_configuration()
# first endpoint
endpoint = device[0][(0,0)][0]
 # read a data packet
data = None
json_body = None

def main():
    while True:
        try:
            data = device.read(endpoint.bEndpointAddress,
                               endpoint.wMaxPacketSize)
#	    humidity = 0
#            temperature = 0
            #print data
            if data[0] == 2:
             humidity = (data[1] / 2)
            if data[0] == 3:
             temperature = (data[1] * 0.1) +2
            try:
             temperature = round(temperature,2)
	     humidity = round(humidity,2)
            except:
             continue
            else:
             break
        except usb.core.USBError as e:
            data = None
            if e.args == ('Operation timed out',):
                continue

    json_body = [
    {
        "measurement": "el-usb-rt",
        "tags": {
            "host": hostname,
        },
       "time": current_time,
       "fields": {
           "temperature": temperature,
           "humidity": humidity
       }
      }
     ]
    print json_body
    client.write_points(json_body)

while True:
 current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
 main()
 time.sleep(10)
