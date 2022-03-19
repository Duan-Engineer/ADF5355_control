import RPi.GPIO as GPIO
from time import sleep
R=[0x201540,0x1,0x12,0x3,0x36008B84,0x800025,0x35406076,0x120000E7,0x102D0428,
   0x5047CC9,0xC0067a,0x61300B,0x1041C]

salveSel=24
mosi=19
clk=23
ce=7
def writeRigister(R):
    GPIO.output(salveSel,GPIO.LOW)
    sleep(0.001)#ms
    a=range(32)
    for i in reversed(a):
        GPIO.output(mosi,(R>>i)&0x01)
        GPIO.output(clk,GPIO.HIGH)
        sleep(1/1000)
        GPIO.output(clk,GPIO.LOW)
        sleep(1/1000)
    GPIO.output(salveSel,GPIO.HIGH)
    sleep(0.1)

def writeRigister13(R):
    b=range(13)
    for i in reversed(b):
        writeRigister(R[i])
        print ("write R"+str(i))
        #sleep(0.2)
        
def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(salveSel,GPIO.OUT)
    GPIO.setup(mosi,GPIO.OUT)
    GPIO.setup(clk,GPIO.OUT)
    GPIO.setup(ce,GPIO.OUT)
    
    GPIO.output(ce,GPIO.HIGH)
    GPIO.output(salveSel,GPIO.HIGH)
    GPIO.output(clk,GPIO.LOW)
    GPIO.output(mosi,GPIO.HIGH)
    sleep(1)
print("init GPIO")
init_GPIO()
print("write rigister!")
writeRigister13(R)
print ("OK")
    