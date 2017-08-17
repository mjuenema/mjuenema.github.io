"""
Example GPS location tracker application for Pycom SiPy.

(c) Markus Juenemann, 2017

After reset the script performs the following operations.

1) Turn LED on.
2) Set GPIO pin P8 to "high" to wake connected Trimble Copernicus II GPS receiver
   from standby mode.
3) Try to read an NMEA GPGGA sentence from GPS and extract latitude and longitude.
4) Set GPIO pin P8 to "low" to put GPS into standby mode but only if we have
   a valid fix.
5) Read previous latitude and longitude values from '/flash/state.json'.
6) Either encode current latitude and longitude in binary, encrypt and send
   as Sigfox message, or send a single bit=1 message if the GPS coordinates
   have not changed, or send a single bit=0 message if the GPS coordinates
   are invalid.
7) Update '/flash/state.json'.
8) Turn LED off.
9) Put micro-controller into deep sleep for 15 minutes after which it will reset.

Hardware:

* Pycom Sipy micro-controller with Sigfox (https://www.pycom.io/product/sipy/)
* Sparkfun Trimble Copernicus II GPS receiver (https://www.sparkfun.com/products/11858)
  The PyTrack Expansion Board would have been an easier option here but I did not
  have one available.

Software:

* speckcipher (https://github.com/inmcm/Simon_Speck_Ciphers/tree/master/Python)

Security:

Even though the GPS coordinates in the Sigfox message are encrypted any
unauthorised person receiving the message can still detect that the GPS
has (a) not moved when a single bit=1 was sent or (b) the device GPS is
at the same location as sometime before when the encrypted data is identical
to a previous message. This is a limitation of the ECB block cipher mode
(https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation). A solution to (b)
would be to encrypt the GPS coordinates padded with 32 random bits using up the
maximum size of 96 bits of a Sigfox message. The legitimate receiver would
simple ignore the trailing 32 bits.

Notes:

The GPS should be left in active mode for 15 minutes every one to four weeks
so it can receive a full almanac (http://www.insidegnss.com/node/923). This logic
is currently not implemented here.

"""

from pycom import heartbeat, rgbled
import ujson
import ustruct
import ure
import ubinascii
import socket
import time
from machine import Pin, UART, deepsleep
from network import Sigfox
from speckcipher import SpeckCipher

GPS_STANDBY_PIN = 'P8'
GPS_TX_PIN = 'P3'
GPS_RX_PIN = 'P4'
GPS_BAUD = 4800

STATE_FILE = '/flash/state.json'

SIGFOX_RCZ = Sigfox.RCZ4    # Australia!!!

CIPHER_KEY = 0x37c8b9525d442bcfc212d2e0b37ca25c


# 1) Turn LED on and heartbeat off.
#
heartbeat(False)
rgbled(0x999999)


# 2) Wake Trimble Copernicus II GPS from standby
#
gps_standby_pin = Pin(GPS_STANDBY_PIN)
gps_standby_pin(1)
time.sleep(5)


# 3) Try to read GGA sentence from GPS
#
gps_uart = UART(1, baudrate=GPS_BAUD, timeout_chars=1000, pins=(GPS_TX_PIN, GPS_RX_PIN))

latitude = 0.0
longitude = 0.0

# Try five times to read a GGA sentence.
for n in range(0,5):
    gps_line = gps_uart.readline()
    print(gps_line)
    if gps_line and gps_line.startswith('$GPGGA'):

        # Parse GGA NMEA string
        gps_fields = gps_line.decode('ascii').split(',')
        print(gps_fields)
        gps_latitude = gps_fields[2]
        gps_latitude_dir = gps_fields[3]
        gps_longitude = gps_fields[4]
        gps_longitude_dir = gps_fields[5]
        gps_quality = gps_fields[6]

        if gps_quality != '0':
            # Convert latitude/longitude from brain-dead NMEA format to decimal.
            m = ure.match('(\d+)(\d\d)\.(\d+)', gps_latitude)
            latitude = int(m.group(1)) + float('0.' + m.group(2) + m.group(3))*100/60
            if gps_latitude_dir == 'S':
                latitude = -latitude
            print(latitude)

            m = ure.match('(\d+)(\d\d)\.(\d+)', gps_longitude)
            longitude = int(m.group(1)) + float('0.' + m.group(2) + m.group(3))*100/60
            if gps_longitude_dir == 'W':
                longitude = -longitude
            print(longitude)

            break

gps_uart.deinit()


# 4) Put Trimble Copernicus II GPS into standby but only if we have a 
#    valid latitude and longitude.
#
if latitude and longitude:
    gps_standby_pin(0)


# 5) Read previous latitude and longitude values
#
previous_latitude = 0.0
previous_longitude = 0.0

try:
    with open(STATE_FILE, 'r') as fp:
        try:
            state = ujson.load(fp)
            print(state)
            previous_latitude = state['latitude']
            previous_longitude = state['longitude']
        except (ValueError, KeyError):
            pass
except OSError:
    pass


# 6) Send Sigfox message
#
from network import Sigfox
import socket

sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ4)
sock = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
sock.setblocking(True)
sock.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

# a) Invalid GPS data, send bit=0
#
if latitude == 0.0 or longitude == 0.0:
    sock.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, False)
    print(sock.send(''))

# b) Location did not change significantly (4 decimal digits equal approx 10 metres)
#
elif (abs(latitude-previous_latitude) < 0.0001 and
      abs(longitude-previous_longitude) < 0.0001):
    sock.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, True)
    print(sock.send(''))

# c) Encode coordinates as two 32 bit floats, encrypt and send.
#    This Speck cipher implementation only operates on integers, thus
#    the conversions.
#
else:
    packed = ustruct.pack('>ff', latitude, longitude)
    cipher = SpeckCipher(key=CIPHER_KEY, key_size=128, block_size=64)
    message = cipher.encrypt(int.from_bytes(packed, 'big'))
    print(message)
    print(sock.send(message.to_bytes(8, 'big')))

sock.close()


# 7) Update '/flash/state.json'.
#
with open(STATE_FILE, 'w') as fp:
    state = ujson.dumps({'latitude': latitude, 'longitude': longitude})
    fp.write(state)


# 8) Turn LED off
#
rgbled(0x000000)


# 9) Put micro-controller into deep sleep for 15 minutes
#    after which it will reset.
#
##deepsleep(1000*60*15)
