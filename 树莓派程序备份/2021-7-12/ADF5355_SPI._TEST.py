import spidev
import RPi.GPIO as GPIO
from time import sleep
R=[0x201540,0x1,0x12,0x3,0x36008B84,0x800025,0x35406076,0x120000E7,0x102D0428,0x5047CC9,
   0xC0067A,0x61300B,0x1041C]# REF=10MHz,RF_out=850MHz

spi = spidev.SpiDev(0,0)
#spi.max_speed_hz=122000
def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7,GPIO.OUT)
    GPIO.output(7,GPIO.HIGH)
    
def init_ADF5355():
    for i in R:
        t4= i>>24
        t3= i>>16
        t2= i>>8
        t1= i>>0
        #spi.xfer([t4,t3,t2,t1])
        spi.writebytes([t4,t3,t2,t1])
        
        sleep(1)
        print ("R"+str(i))
init_GPIO()
init_ADF5355()
