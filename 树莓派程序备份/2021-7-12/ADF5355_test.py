import spidev
from time import sleep
import RPi.GPIO as GPIO

freq=425123.456 #KHz
#F_pfd=10000.0    #KHz
F_pfd=122880    #KHz
MOD1=2**24
MOD2=16383.0

R=[0x201540,0x1,0x12,0x3,0x36008B84,0x800025,0x35406076,0x120000E7,0x102D0428,0x5047CC9,
   0xC0067a,0x61300B,0x1041C]

spi = spidev.SpiDev(0,0)
#spi.max_speed_hz=max_freq #122KHZ
def init_GPIO():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7,GPIO.OUT)
    GPIO.output(7,1)   

#select freq divider
def freq_sel(freq):
    if(53125<=freq<106250):
        RF_Div,RF_Sel = 64,6
    if(106250<=freq<212500):
       RF_Div,RF_Sel = 32,5
    if(212500<=freq<42500):
       RF_Div,RF_Sel = 16,4
    if(425000<=freq<850000):
       RF_Div,RF_Sel = 8,3
    if(850000<=freq<1700000):
       RF_Div,RF_Sel = 4,2
    if(1700000<=freq<3400000):
       RF_Div,RF_Sel = 2,1
    if(3400000<=freq<6800000):
       RF_Div,RF_Sel =1,0
    return (RF_Div,RF_Sel)
       
def calc(freq):
    print("Freq Select!")
    div,sel=freq_sel(freq)
    F_vco = freq*div
    print ("F_vco=",F_vco)
    INTR = int(F_vco/F_pfd)
    print ("INTR=",INTR)
    FRAC=(F_vco-INTR*F_pfd)/F_pfd
    print ("FRAC=",FRAC)
    FRAC1R = int(FRAC*MOD1)
    print ("FRAC1R=",FRAC1R)
    FRAC2R = int(((FRAC-FRAC1R/MOD1)*MOD1)*MOD2)
    print ("FRAC2R=",FRAC2R)
    return (INTR,FRAC1R,FRAC2R)

    
def init_ADF5355():
    for i in R:
        t4= i>>24
        t3= i>>16
        t2= i>>8
        t1= i>>0
        spi.xfer([t4,t3,t2,t1])
        sleep(0.1)        

init_GPIO()
#init_SPI(0,0,122000)
init_ADF5355()
print ("OK")
#++++++++++++++++++++++++++++++++++
print("please Enter freq(KHz):")
a=input()
INT,FRAC1,FRAC2=calc(float(a))
RFout=(INT+(FRAC1+FRAC2/MOD2)/MOD1)*F_pfd
print("RFcalc=",RFout,"KHz")

