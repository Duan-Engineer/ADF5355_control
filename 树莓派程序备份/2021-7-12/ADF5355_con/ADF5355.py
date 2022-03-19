
#Author:duan
#date:2021-4-7

#version:V1.0
#ADF5355 hardware pin
#    signal   Raspberrypi(BOARD)  EV-ADF5355 Board

#    MOSI          19               TP4
#    MISO          21               MUXOUT(not must)
#   SCK           23               TP3
#    CE            24               TP5
#    LE             7               TP6
#    GND            9               GND
#they must common Grand.
import spidev
from time import sleep
import RPi.GPIO as GPIO

# the simple calss use
class ADF5355:
    Rigisters=[]
    __salveSel=24
    __mosi=19
    __clk=23
    __ce=7
    
    
    def __init__(self,Rigister13,F_pfd,MOD2):
        self.Rigisters = Rigister13
        self.F_pfd=F_pfd
        self.MOD2 =MOD2
        self.MOD1=2**24
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.__salveSel,GPIO.OUT)
        GPIO.setup(self.__mosi,GPIO.OUT)
        GPIO.setup(self.__clk,GPIO.OUT)
        GPIO.setup(self.__ce,GPIO.OUT)
    
        GPIO.output(self.__ce,GPIO.HIGH)
        GPIO.output(self.__salveSel,GPIO.HIGH)
        GPIO.output(self.__clk,GPIO.LOW)
        GPIO.output(self.__mosi,GPIO.HIGH)
    #select freq divider
    def write4bytes(self,data):
        GPIO.output(self.__salveSel,GPIO.LOW)
        a=range(32)
        for i in reversed(a):
            GPIO.output(self.__mosi,(data>>i)&0x01)
            GPIO.output(self.__clk,GPIO.HIGH)
            GPIO.output(self.__clk,GPIO.LOW)
        GPIO.output(self.__salveSel,GPIO.HIGH)
        
    def writeRigister32(self):
        b=range(13)
        for i in reversed(b):
            self.write4bytes(self.Rigisters[i])
            print ("write R"+str(i))
        
    #def initADF5355(self):
        #self.writeRigister32()
           
    def freq_sel(self,freq):
        'Select freq(KHz)'
        if(53125<=freq<106250):
            self.RF_Div,self.RF_Sel = 64,6
        if(106250<=freq<212500):
            self.RF_Div,self.RF_Sel = 32,5
        if(212500<=freq<42500):
            self.RF_Div,self.RF_Sel = 16,4
        if(425000<=freq<850000):
            self.RF_Div,self.RF_Sel = 8,3
        if(850000<=freq<1700000):
            self.RF_Div,self.RF_Sel = 4,2
        if(1700000<=freq<3400000):
           self.RF_Div,self.RF_Sel = 2,1
        if(3400000<=freq<6800000):
           self.RF_Div,self.RF_Sel =1,0
        print(self.RF_Div,self.RF_Sel)
        
    def freq_set(self,freq):
        print("Freq Select!")
        self.freq_sel(freq)
        self.F_vco = freq*self.RF_Div
        print ("F_vco=",self.F_vco)
        self.INTR = int(self.F_vco/self.F_pfd)
        print ("INTR=",self.INTR)
        self.FRAC=(self.F_vco-self.INTR*self.F_pfd)/self.F_pfd
        print ("FRAC=",self.FRAC)
        self.FRAC1R = int(self.FRAC*self.MOD1)
        print ("FRAC1R=",self.FRAC1R)
        self.FRAC2R = int(((self.FRAC-self.FRAC1R/self.MOD1)*self.MOD1)*self.MOD2)
        print ("FRAC2R=",self.FRAC2R)
        #return (INTR,FRAC1R,FRAC2R)
        self.RFout=(self.INTR+(self.FRAC1R+self.FRAC2R/self.MOD2)/self.MOD1)*self.F_pfd
        print("RFcalc=",self.RFout/self.RF_Div,"KHz")
        
    def updateRigisters(self):
        self.Rigisters[0]= 0X00200000 | (self.INTR<<4);
        self.Rigisters[1]= 0X1 | (self.FRAC1R<<4);
        self.Rigisters[2]= 0X2 | (self.MOD2<<4)|(self.FRAC2R<<17);
        self.Rigisters[6]= 0X35006076|(self.RF_Sel<<21);

#end ADF5355 class
        
class register13:

    def __init__(self):

        self.register=[0,1,2,3,4,0x00800025,6,7,0x102D0428,9,10,0x0061300B,12]
    # init 13 register
    def init_register13(self,register13):
        '''
        :param register13: 13个寄存器的初值。必须是一个list类型[num=13]
        '''
        try:
            if(len(register13)==13):
                for i in range(13):
                    self.register[i]=register13[i]
            else:
                print('Error::register13 length must is 13!!')
        except:
            self.register=register
        
    def set_register0(self,*args,**kwargs):
        '''
        set VCO autocal, perscaler and INT
        :param autocal: 自动校准，
                            0 = disabled 
                            1 = enabled
        :param perscal: 预分频值
                        0=4/5 INT_min=23  INT_max=32767 允许最大频率到 7GHz
                        1=8/9 INT_min-75  INT_max=65535
        :param INT:16-bit INT value [23-65535]
        '''
        try:
            if(kwargs['autocal'] in [0,1]):
                self.autocal = kwargs['autocal']
            else:
                print("Error::autocal must in [1,0]")          
        except KeyError:
            self.perscal = 1  # 8/9
        try:
            self.perscal = kwargs['perscal']
        except KeyError:
            self.perscal = 0  # 4/5
        try:
            self.INT=kwargs['INT']
        except KeyError:
            self.INT = 23 
        if(self.perscal==0 and not(23<=self.INT<=32767)) or (self.perscal==1 and self.INT<75):
            print("Error:perscal value is 0 INT_min=23,else 1 INT_min=75;INT_max=65535")
        else:
            self.register[0] = 0x0|(self.autocal<<21)|(self.perscal<<20)|(self.INT<<4)
            print("register0 = 0x%X\r\n"%self.register[0])
              
            
    def set_register1(self,*args,**kwargs):
        '''
        set  FRAC1
        :param FRAC1: 24-Bit FRAC1 value [0-16777216] 
        '''
        try:
            if(0<=kwargs['FRAC1']<=16777216):
                self.FRAC1 = kwargs['FRAC1']
            else:
                print("Error::FRAC1 over range")          
        except KeyError:
            self.FRAC1 = 16777216
        
        self.register[1]= (self.FRAC1<<4)|0x1
        print("register1 = 0x%X\r\n"%self.register[1])
    
    def set_register2(self,*args,**kwargs):
        '''
        set FRAC2 and MOD2
        :param FRAC2:14-bit auxiliary  fractional value [0-16383]
        :param MOD2:14-bit auxiliary modulus value  [0-16383]
        '''
        try:
            if(0<=kwargs['FRAC2']<=16383):
                self.FRAC2 = kwargs['FRAC2']
            else:
                print("Error::FRAC2 over range!")
        except KeyError:
            self.FRAC2 = 16777216
        try:
            if(2<=kwargs['MOD2']<=16383):
                self.MOD2=kwargs['MOD2']
            else:
                print("Error::MOD2 over range")
        except KeyError:
            self.MOD2 = 16777216
            
        self.register[2]=(self.FRAC2<<17)|(self.MOD2<<4)|0x02
        print("register2 = %0X"%self.register[2])
        
    def set_register3(self,*args,**kwargs):
        '''
        set SD load reset,phase,phase adjust and phase value
        :param SD1: SD load reset
                    0 = ON register0 update
                    1 = disabled
        :param PHR1:相位同步
                    0 = disabled
                    1 = enable
        :param PHA1:相位调整
                    0 = disabled
                    1 = enabled
        :param PHASE:相位值 [0-16777216] 输出相位= (PHASE/16777216) X 360 degree
        '''
        try:
            if(kwargs['SD1'] in [0,1]):
                self.SD1=kwargs['SD1']
            else:
                print ("Error:: SD1 value error")
        except KeyError:
            self.SD1 = 1
                
        try:
            if(kwargs['PHR1'] in [0,1]):
                self.PHR1=kwargs['PHR1']
            else:
                print ("Error:: PHR1 value error")
        except KeyError:
            self.PHR1 = 1
                
        try:
            if(kwargs['PHA1'] in [0,1]):
                self.PHA1=kwargs['PHA1']
            else:
                print ("Error:: PHA1 value error")
        except KeyError:
            self.PHA1 = 1
        try:
            if(0<=kwargs['PHASE']<=16777216):
                self.PHASE=kwargs['kwargs']
            else:
                print("Error::PHASE Over range")
        except KeyError:
            self.PHASE=0
                
        self.register[3] = (self.SD1<<30)|(self.PHR1<<29)|(self.PHA1<<28)|(self.PHASE<<4)|0X3
        print("reguster3 = %X"%self.register[3])
        
    def set_register4(self,*args,**kwargs):
        '''
        :param MUXOUT:OUTPUT 片上多路复用器。当频率改变，当改变频率，即写入寄存器0时，MUXOUT不能设置为N分频输出或R分频输出。如果需要，在锁定到新频率后启用这些功能。
                     | 0 | Three_state output |
                     | 1 | DVdd               |
                     | 2 | DGND               |
                     | 3 | R DIVIDER OUTPUT   |
                     | 4 | N DIVIDER OUTPUT   |
                     | 5 | ANALOG LOCK DETECT |
                     | 6 | DIGITAL LOCK DETECT|
                     | 7 | RESERVED           |
        :param RD : 参考倍频器 [ 0 = disabled  1 = enabled ] 设置RD2位(DB26位)为0，将参考频率信号直接送入10位R计数器，使倍频器失效。
                    将该位设置为1将参考频率乘以2，然后将其送入10位的R计数器。当倍频器被禁用时，REF_in的下降沿是PFD的有效边沿输入到分数合成器。
                    当倍频器使能后，参考频率的上升沿和下降沿都可以作为PFD的有效边沿。
        :param RD2 : 设置RD2位为1插入一个除以2，在R计数器和PFD之间切换触发器，扩展最大参考频率输入速率。该功能在PFD输入端提供50%占空比信号。
                     [ 0 = disabled 1 = enabled ]
        :param R_Counter : R/REF_in 产生PFD的参考时钟。 [0-1023]
        :param double_buf : 使能或禁用寄存器6中的RF分频选择位(bits [DB23:DB21])的双缓冲。  [0 = disabled 1 = enabled]               
        :param ICP:充电泵电流设定 (mA) 5R1k
                    | 0 = 0.31 || 1 = 0.63 || 2 = 0.94 || 3 = 1.25 |
                    | 4 = 1.56 || 5 = 1.88 || 6 = 2.19 || 7 = 2.50 |
                    | 8 = 2.81 || 9 = 3.13 ||10 = 3.44 ||11 = 3.75 |
                    |12 = 4.06 ||13 = 4.38 ||14 = 4.69 ||15 = 5.00 |
        :param REFIN :ADF5355允许使用差分或单端参考源.为了获得最佳的整数边界脉冲性能，建议对高达250mhz的所有参考信号使用单端设置(即使使用差分参考信号)。
                     参考频率在250mhz以上时使用差分设置。[ 0 = SINGLE 1 = DIFF ] 
        :param level:为了协助逻辑兼容，MUXOUT可编程到两个逻辑级别。  [ 0 = 1.8V  1 = 3.3v ]
        :param PDP:相位检波器极性.
                    当使用无源环滤波器或非反相有源环滤波器时，设置1(postive).
                    如果使用具有反相特性的有源滤波器，则将此位设为0(negative)。[ 0 = NEGATIVE1 = POSITIVE ]           
        :param power_down:可编程关机模式。设置为1表示下电。设置为0可以使合成器正常运行。在软件或硬件断电模式下，ADF5355保留其寄存器中的所有信息。
                         只有当电源电压被移去时，寄存器内容才会丢失。 [ 0 = disable 1 = enabled] 
                         当断电激活，以下事件发生:
                            1.合成器计数器被迫满足其负载状态条件。   2.VCO掉电。
                            3.电荷泵被迫进入三态模式                4.数字锁检测电路复位。
                            5.RF_outA+/RF_outA-和RF_outB 输出关闭。6.输入寄存器保持活动状态，并能够加载和锁定数据。   
        :param cp_three_state :设置 1 使电荷泵进入三态模式。设置 0 普通操作。
        :param counter_reset:重置ADF5355的R计数器、N计数器和VCO带选择。[1=enabled reset 0=disabled normal] 当改变频率时，还需要切换计数器复位。
        '''
        try:
            if(kwargs['MUXOUT'] in range(8)):
                self.MUXOUT = kwargs['MUXOUT']
            else:
                print("Error::MUXOUT over range!")
        except KeyError:
            self.MUXOUT = 7

        try:
            if(kwargs['RD'] in range(2)):
                self.RD = kwargs['RD'] 
            else:
                print('Error::RD over range!')
        except KeyError:
            self.RD = 1

        try:
            if(kwargs['RD2'] in range(2)):
                self.RD2 = kwargs['RD2'] 
            else:
                print('Error::RD2 over range!')
        except KeyError:
            self.RD2 = 1

        try:
            if(kwargs['R_Counter'] in range(1024)):
                self.R_Counter = kwargs['R_Counter'] 
            else:
                print('Error::R_Counter over range!')
        except KeyError:
            self.R_Counter = 0

        try:
            if(kwargs['double_buf'] in range(2)):
                self.double_buf = kwargs['double_buf'] 
            else:
                print('Error::double_buf over range!')
        except KeyError:
            self.double_buf = 1

        try:
            if(kwargs['ICP'] in range(16)):
                self.ICP=kwargs['ICP']
            else:
                print('Error:: ICP over range!')
        except KeyError:
            self.ICP = 2

        try:
            if(kwargs['REFin'] in range(2)):
                self.REFin=kwargs['REFin']
            else:
                print('Error::REFin over range!')
        except KeyError:
            self.REFin = 0

        try:
            if(kwargs['level'] in range(2)):
                self.level=kwargs['level']
            else:
                print('Error::level over range!')  
        except:
            self.level=1

        try:
            if(kwargs['PDP'] in range(2)):
                self.PDP=kwargs['PDP']
            else:
                print('Error::PDP over range!')
        except KeyError:
            self.PDP = 1

        try:
            if(kwargs['power_down'] in range(2)):
                self.power_down = kwargs['power_down']
            else:
                print('Error::power_down over range!')
        except:
            self.power_down = 1

        try:
            if(kwargs['cp_three_state'] in range(2)):
                self.cp_three_state = kwargs['cp_three_state']
            else:
                print('Error::cp_three_state over range!')
        except:
            self.cp_three_state = 1

        try:
            if(kwargs['counter_reset'] in range(2)):
                self.counter_reset = kwargs['counter_reset']
            else:
                print('Error::counter_reset over range!')
        except:
            self.counter_reset = 0
        
        self.register[4] = (self.MUXOUT<<27)|(self.RD<<26)|(self.RD2<<25)|(self.R_Counter<<15)|(self.double_buf<<14)|(self.ICP<<10)|(self.REFin<<9)|\
                            (self.level<<8)|(self.PDP<<7)|(self.power_down<<6)|(self.cp_three_state<<5)|(self.counter_reset<<4)|0x04
        print("reguster4 = %X"%self.register[4])

    def set_register5(self):
        '''
        必须设置为默认值0x00800025
        '''
        self.register[5]=0x00800025
        print("register5 = %X"%self.register[5])
    
    def set_register6(self,*args,**kwargs):
        '''
        :param gated_bleed:放流可以用来改善相位噪声和激振;：但是，由于对锁定时间的潜在影响,
                            如果设置为1，确保流血电流没有打开，直到数字锁检测断言逻辑高;
                            注意，此功能需要启用数字锁检测.[1=disabled 0=enabled]
        :param negative_bleed:对于大多数：fractional-N应用程序，推荐使用恒定负流，因为它可以改善电荷泵的线性度，
                            比关闭它更低的噪声和虚假信号。[1=enabled 0=disabled]
                            在整数- n模式下，即FRAC1 = FRAC2 = 0，或者fPFD大于100 MHz。
        :param feedback_sel:输出选择反馈VCO到N计数器.
                            1=信号来自VCO，0=信号是从输出分频器的输出中获取的
                            分配器可覆盖宽频带(3.4 GHz至6.8 GHz)。
                            当分频器启用并且反馈信号从输出端取下时，两个单独配置的锁相环的射频输出信号是同步的。
                            在一些需要信号的正干扰以增加功率的应用中，分反馈是有用的。
        :param divider_sel:选择射频输出分频器的值.[1,2,4,8,16,32,64]
                          当寄存器4的DB14位双缓冲位启用时，写入寄存器0缓冲。
        :param cp_bleed_current:充电泵排气电流.控制添加到充电泵输出的排气电流的水平。这个电流优化了来自器件的相位噪声和杂散电平。
                                测试表明，最佳泄放集如下:
                                4/N < I_bleed/I_cp < 10/N 
                                (N为VCO到PFD的反馈计数器的值。I_bleed施加在充电泵上的恒定负排放值,
                                I_cp充电泵电流设定值,register4 ICP)
                                1=3.75uA
                                2=7.50uA 
        :param mute_till_lock:[0 = mute disabled  1 = mute enabled]
                            置1 由数字锁定检测电路确定，到射频输出级的电源电流被关闭，直到设备达到锁定。
        :param RF_out_B_enable:[0 = 辅助高频射频输出使能 1 = 辅助射频输出关闭]
        :param RF_out_A_enable:[0 = 初级射频输出关闭 1 = 初级射频输出是能]
        :param output_power:设置初级射频输出的功率级别(dBm)。
                            | 0 | -4dBm |
                            | 1 | -1dBm |
                            | 2 | +2dBm |
                            | 3 | +5dBm |
        '''
        try:
            if(kwargs['gated_bleed'] in range(2)):
                self.gated_bleed = kwargs['gated_bleed']
            else:
                print('Error::gate_bleed must in [0,1]!')

        except KeyError:
            self.gated_bleed = 0
        
        try:
            if(kwargs['negative_bleed'] in range(2)):
                self.negative_bleed = kwargs['negative_bleed']
            else:
                print("Error::negative_bleed must in [0,1]")
        except:
            self.negative_bleed = 0

        try:
            if(kwargs['feedback_sel'] in range(2)):
                self.feedback_sel = kwargs['feedback_sel']
            else:
                print('Error::feedback_sel must in [0,1]')
        except KeyError:
            self.feedback_sel = 0

        try:
            if(kwargs['divider_sel'] in [1,2,4,8,16,32,64]):
                self.divider_sel = kwargs['divider_sel']
            else:
                print('Error::divider_sel must in [1,2,4,8,16,32,64')
        except KeyError:
            self.divider_sel = 1

        try:
            if(0<kwargs['cp_bleed_current']<=255):
                self.cp_bleed_current=kwargs['cp_bleed_current']
            else:
                print('Error::cp_bleed_current must [1-255] int value')
        except:
            self.cp_bleed_current = 1
        
        try:
            if(kwargs['mute_till_lock'] in range(2)):
                self.mute_till_lock = kwargs['mute_till_lock']
            else:
                print("Error::mute_till_lock must in [0,1]")
        except:
            self.mute_till_lock = 1
        
        try:
            if(kwargs['RF_out_B_enable'] in range(2)):
                self.RF_out_B_enable = kwargs['RF_out_B_enable']
            else:
                print("Error:: RF_out_B_enable must in [0,1]")
        except KeyError:
            self.RF_out_B_enable = 0
        
        try:
            if(kwargs['RF_out_A_enable']  in range(2)):
                self.RF_out_A_enable = kwargs['RF_out_A_enable']
            else:
                print('Error::RF_out_A_enable must in [0,1]')
        except KeyError:
            self.RF_out_A_enable = 0

        try:
            if(kwargs['output_power'] in range(4)):
                self.output_power = kwargs['output_power']
            else:
                print("Error:: output_power over range!")
        except:
          
            self.output_power = 3 # +5dBm
        
        self.register[6] = (self.gated_bleed<<30)|(self.negative_bleed<<29)|(self.feedback_sel<<24)|(self.divider_sel<<21)|\
                            (self.cp_bleed_current<<13)|(self.mute_till_lock<<11)|(self.RF_out_B_enable<<10)|(self.RF_out_A_enable<<6)\
                                (self.output_power<<4)|0x14000006
        print('register6 = %X'%self.set_register6)


    def set_register7(self,*args,**kwargs):
        '''
        :param LE_sync:设置为1时，确保负载使能(LE)边缘内部与参考输入频率的上升边缘同步。
                    这种同步防止了在基准频率下降边缘同时加载基准和射频分频器的罕见事件，这会导致更长的锁定时间。
                    [0=disabled 1=LE synced to refin]
        :param LDC:fraction - n锁定检测计数.在断言锁检测高之前，设置锁检测电路计数的连续周期数。
                    [0=1024 | 1=2048 | 2=4096| 3=8192]
        :param LOL：loss of lock mode(失锁模式 )[0=disabled 1=enabled]
                    当应用程序是一个固定频率的应用程序，其中的参考(REF_in)可能被删除时，例如一个时钟应用程序，将LOL模式位(位DB7)设置为1
                    标准锁检测电路假设REF_in始终存在;然而，对于计时应用程序来说可能不是这样。要启用此功能，请将DB7设置为1。当使用差分精炼模式时，LOL模式不可靠。
        :param LDP:  分数- N 锁检测精度(lock detect precision) 。 [0=5ns 1=6ns 2=8ns 3=12ns] 如果bleed 电流被使用，使用12ns。
        :param LDM: 锁检测模式（lock detect mode）
                    [0 每个参考周期按分数- n的锁检测精度设置，如分数- n锁检测计数(LDC)部分
                     1 每个参考周期总是2.9ns，它更适合于整数n的应用]    
        '''
        try:
            if(kwargs['LE_sync'] in range(2)):
                self.LE_sync = kwargs['LE_sync']
            else:
                print("Error::LE_sync must is [0,1]")
        except:
            self.LE_sync = kwargs['LE_sync']
        
        try:
            if(kwargs['LDC'] in range(4)):
                self.LDC = kwargs['LDC']
            else:
                print('Error::LDC must in [0,1,2,3]!')
        except KeyError:
            self.LDC = 0
        
        try:
            if(kwargs['LOL'] in range(2)):
                self.LOL = kwargs['LOL']
            else:
                print('Error::LOL must in [0,1]!')
        except KeyError:
            self.LOL = 1

        try:
            if(kwargs['LDP'] in range(4)):
                self.LDP = kwargs['LDP']
            else:
                print('Error::LDP must in [0,1,2,3] ')
        except:
            self.LDP = 0
        
        try:
            if(kwargs['LDM'] in range(2)):
                self.LDM = kwargs['LDM']
            else:
                print('Error:: LDM must in [0.1]')
        except:
            self.LDM = 1

        self.register[7] = (self.LE_sync<<25)|(self.LDC<<8)|(self.LOL<<7)|(self.LDP<<5)|(self.LDM<<4)|0x07

    def set_register8(self):
        '''
        必须设置为默认值0x102D0428
        '''
        self.register[8]=0x102D0428
        print("register8 = %X"%self.register[8])

    def set_register9(self,*args,**kwargs):
        '''
        :param vco_band_div : 设置VCO分带时钟的值。VCO_band_div=ceiling(Fpfd/2400000) [1-255]
        :param timeout:vco带宽选择的超时值。[1-1023]
        :param ALC_wait:自动自动电平校准的超时值。设置用于VCO自动电平校准的定时器值。这个函数结合了PFD频率、timeout变量和ALC_wait变量。
                        ALC_wait>(50us X Fpfd)/timeout [1-31]
        :param SLC_wait:设置合成器锁定超时值.SLC_wait > (20 µs × fPFD)/Timeout [1-31]
        '''
        try:
            if(1<=kwargs['vco_band_div']<=255):
                self.vco_band_div = kwargs['vco_band_div']
            else:
                print('Erro::vco_band_div over range!')
        except KeyError:
            self.vco_band_div = 1
        
        try:
            if(1<=kwargs['timeout']<=1023):
                self.vco_band_div = kwargs['timeout']
            else:
                print('Erro::timeout over range!')
        except KeyError:
            self.timeout = 1

        try:
            if(1<=kwargs['SLC_wait']<=31):
                self.vco_band_div = kwargs['SLC_wait']
            else:
                print('Erro::SLC_wait over range!')
        except KeyError:
            self.SLC_wait = 1 

        try:
            if(1<=kwargs['ALC_wait']<=31):
                self.vco_band_div = kwargs['ALC_wait']
            else:
                print('Erro::ALC_wait over range!')
        except KeyError:
            self.ALC_wait = 1 

        self.register[9]=(self.vco_band_div<<24)|(self.timeout<<14)|(self.ALC_wait<<9)|(self.SLC_wait<<4)|0x09
        print('register9 = %X'%self.register[9])


    def set_register10(self,*args,**kwargs):
        '''
        :param adc_clk_div: ADC_CLK_DIV = Ceiling(((fPFD/100,000) − 2)/4),Ceiling()四舍五入到最近的整数
                            例如： fPFD = 61.44 MHz， ALC_CLK_DIV = 154 ， ADC clock frequency is 99.417 kHz.
                            ADC_CLK_DIV超过255，设置它为255.[1-255]
        :param adc_conversion_en :确保ADC在向寄存器10执行写操作时执行转换。建议使能该模式。
                            [1=enabled 0=disabled]
        :param adc_en:[1=为温度相关的Vtune校准的ADC供电。建议开启该功能。 0=关闭]
        '''
        try:
            if(1<=kwargs['adc_clk_div']<=255):
                self.adc_clk_div = kwargs['adc_clk_div']
            else:
                print('Error::adc_clk_div over range!')
        except KeyError:
            self.adc_clk_div = 1
        
        try:
            if(kwargs['adc_conversion_en'] in range(2)):
                self.adc_conversion_en = kwargs['adc_conversion_en']
            else:
                print('Error::adc_conversion_en over range!')
        except KeyError:
            self.adc_conversion_en = 1
        
        try:
            if(kwargs['adc_en'] in range(2)):
                self.adc_en = kwargs['adc_en']
            else:
                print("Error::adc_en must in [0,1]")
        except:
            self.adc_en = 1
        
        self.register[10] = (self.adc_clk_div<<6)|(self.adc_conversion_en<<5)|(self.adc_en<<4)|0x0a
        print('rigister10 = %X'%self.register[10])
           
    def set_register11(self):
        '''
        必须设置为默认值0x0061300B
        '''
        self.register[11]=0x0061300B
        print("register11 = %X"%self.register[11])
    
    def set_register12(self,*args,**kwargs):
        '''
        :param phase_rcd= 相位重同步时钟分配器(phase resync clock divider) [1-65535]
        '''
        try:
            if(1<=kwargs['phase_rcd']<=65535):
                self.phase_rcd = kwargs['phase_rcd']
            else:
                print('Error::phase_rcd over range!!')  
        except KeyError:
            self.phase_rcd = 1 #normal opration

        self.register[12]=(self.phase_rcd<<16)|0x0C 
        print("register12 = %X"%self.register[12])
