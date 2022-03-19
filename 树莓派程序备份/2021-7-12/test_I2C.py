import smbus
from time import sleep

bus=smbus.SMBus(1)

add = 0x49

def read_ch1():
    bus.write_byte_data(add,0x00,0xc0)
    a = bus.read_byte_data(add,0x02)
    b = bus.read_byte_data(add,0x03)
    val = (a<<4 | b>>4)
    V=val*(3.3/2**12)
    print(V)
    
read_ch1()