import spidev
from time import sleep
import RPi.GPIO as GPIO
import ADF5355
#F_pfd=10000.0
F_pfd=122880.0
MOD2=16383
freq=425000.123
R=[0x201540,0x1,0x12,0x3,0x36008B84,0x800025,0x35406076,0x120000E7,0x102D0428,0x5047CC9,
   0xC0067A,0x61300B,0x1041C]# REF=10MHz,RF_out=850MHz


if __name__ == '__main__':
    
    a=ADF5355.ADF5355(R,F_pfd,MOD2)
    #for i in a.Rigisters:
        #print ('0x%x'%i)
    #a.initADF5355()
    while True:
        print("please Enter freq(KHz):")
        freq=float(input())   
        #a.freq_sel(freq)
        a.freq_set(freq)
        a.updateRigisters()
        a.writeRigister32()
    
#for i in a.Rigisters:
    #print ('0x%x'%i)
