
#12位 4通道 ADC I2C 接口
import smbus
from math import ceil

class ADS7924:

    def __init__(self,slave_address,ref_voltage):
        '''
        初始换 I2C,寄存器初始值
        '''
        try:
            self.bus = smbus.SMBus(1)
        except :
            print('Error::I2C init error!!!')

        # init address
        self.add = slave_address
        self.A0 = slave_address & 0x01
        self.MODECNTRL_ADD = 0x00 # 模式控制通道选择寄存器地址

        self.INTCNTRL_ADD  = 0X01 # 中断控制寄存器地址
        self.INTCONFIG_ADD = 0x12 # 中断配置寄存器地址
        self.SLPCONFIG_ADD = 0X13 
        self.ACQCONFIG_ADD = 0X14
        self.PWRCONFIG_ADD = 0X15
        self.RESET_ADD = 0X16

        self.DATA0_H_ADD  = 0X02 # 0通道 转换高位数据 寄存器地址
        self.DATA0_L_ADD  = 0X03 # 0通道 转换低位数据 寄存器地址

        self.DATA1_H_ADD  = 0X04 # 1通道 转换高位数据 寄存器地址
        self.DATA1_L_ADD  = 0X05 # 1通道 转换低位数据 寄存器地址

        self.DATA2_H_ADD  = 0X06 # 2通道 转换高位数据 寄存器地址
        self.DATA2_L_ADD  = 0X07 # 2通道 转换低位数据 寄存器地址

        self.DATA3_H_ADD  = 0X08 # 3通道 转换高位数据 寄存器地址
        self.DATA3_L_ADD  = 0X09 # 3通道 转换低位数据 寄存器地址

        self.ULR0_ADD = 0X0A # 通道0比较寄存器的上限阈值 寄存器地址
        self.LLR0_ADD = 0X0B # 通道0比较寄存器的下限阈值 寄存器地址

        self.ULR1_ADD = 0X0C # 通道1比较寄存器的上限阈值 寄存器地址
        self.LLR1_ADD = 0X0D # 通道1比较寄存器的下限阈值 寄存器地址

        self.ULR2_ADD = 0X0E # 通道2比较寄存器的上限阈值 寄存器地址
        self.LLR2_ADD = 0X0F # 通道2比较寄存器的下限阈值 寄存器地址

        self.ULR3_ADD = 0X0C # 通道3比较寄存器的上限阈值 寄存器地址
        self.LLR3_ADD = 0X0B # 通道3比较寄存器的下限阈值 寄存器地址


        self.mode = 0x00 # Idel mode
        self.chan_sel =0x00 # channel 0
        self.MODECNTRL = (self.mode<<2)|self.chan_sel
        self.INTCNTRL = 0x00
        self.voltage = ref_voltage # 参考电压
        self.adc_bit =12  # ADC 位数
        self.INTCONFIG = 0XE0 #  中断配置寄存器 初始值
        self.SLPCONFIG = 0x00 #  休眠配置寄存器 初始值
        self.ACQCONFIG = 0X00 #  采集配置寄存器 初始值
        self.PWRCONFIG = 0X00 #  电源配置寄存器 初始值

        #  软件复位和设备ID寄存器 初始值
        if(self.A0 == 1):
            self.RESET = 0X18
        else:
            self.RESET = 0X19
        self.soft_reset_value =0xaa #对RESET寄存器写入0xAA,将对ADS7924产生一个软件复位

    def setmode_chan_sel(self,mode,chan_sel):
        '''
        设置工作模式，选择转换通道
        :param mode= idle (默认):所有电路关闭;最低电源设置 
                    awake : 所有的电路都醒了，准备转换
                    manual_single:选择输入通道转换一次 
                    manual_scan:所有输入通道转换一次
                    auto_single:单通道连续转换
                    auto_scan:所有通道连续转换
                    auto_single_with_sleep:单通道连续转换，转换之间加入可编程的休眠时间
                    auto_scan_with_sleep:所有通道连续转换，转换之间加入可编程的休眠时间
                    auto_burst_scan_with_sleep:所有的输入通道以一个可编程的睡眠时间最小的延迟转换。
        :param chan_sel: [0,1,2,3] eg. 0= channel 0
        '''
        try:
            if(mode=="idle"):
                self.mode = 0x00
            elif(mode=="awake"):
                self.mode = 0x20
            elif(mode=="manual_single"):
                self.mode = 0x30
            elif(mode=="manual_scan"):
                self.mode = 0x32
            elif(mode=="auto_single"):
                self.mode = 0x31
            elif(mode=="auto_scan"):
                self.mode = 0x33
            elif(mode=="auto_single_with_sleep"):
                self.mode = 0x39
            elif(mode=="auto_scan_with_sleep"):
                self.mode = 0x3B
            elif(mode=="auto_burst_scan_with_sleep"):
                self.mode = 0x3F
            else:
                print('Error::mode  Error!')
        except :
            self.mode = 0x00
        
        try:
            if(chan_sel in range(4)):
                self.chan_sel = chan_sel
            else:
                print('Error::channel select Erro! [0,1,2,3]')
        except:
            self.chan_sel = 0x00
        
        self.MODECNTRL = (self.mode<<2)|self.chan_sel
        self.bus.write_byte_data(self.add,self.MODECNTRL_ADD,self.MODECNTRL)

    def set_interrupt(self,alarm__chan,alram_enable):
        '''
        使能能对应通道报警
        :param alarm__chan:通道选择 [0,1,2,3]
                            例如:选择通道0    alarm_chan=[0]
                                 选择通道1和2 alram_chan=[1,2]
                                 选择所有通道 alarm_chan=[0,1,2,3]
        :param alarm_enable:通道报警使能 [1=enabled 0=disabled(默认)]

        用法：
        1. 1通道报警使能     set_interrupt(alarm__chan=[1],alram_enable=[1])
        2. 2和3通道报警使能  set_interrupt(alarm__chan=[2,3],alram_enable=[1,1])
        3. 所有通道使能      set_interrupt(alarm__chan=[0,1,2,3],alram_enable=[1,1,1,1])                       
        '''
        try:

            if(len(alarm__chan) == len(alram_enable)):
                self.INTCNTRL = 0x00
                for i in range(len(alarm__chan)):
                    self.INTCNTRL |= (alram_enable[i]<<alarm__chan[i])
            else:
                print('Error::length is not same!')
        except:
                self.INTCNTRL = 0x00
        self.bus.write_byte_data(self.add,self.INTCNTRL_ADD,self.INTCNTRL)
    
    def set_interrupt_all(self):
        '''
        所有通道报警使能
        '''
        self.INTCNTRL = 0x0F
        self.bus.write_byte_data(self.add,self.INTCNTRL_ADD,self.INTCNTRL)
    
    def get_alram_status(self,alarm_chan):
        '''
        读取通道的报警状态。
        :param alram_chan:报警通道选择 [0,1,2,3]
        用法：
        1. 1通道报警状态     read_chan_alram_status(alarm__chan=[1])
        2. 2和3通道报警使能  set_interrupt(alarm__chan=[2,3])
        3. 所有通道使能      set_interrupt(alarm__chan=[0,1,2,3])
        '''
        try:
            if(type(alarm_chan) =="<type 'list'>" ):
                alram=[]
                status = self.bus.read_byte_data(self.add,self.INTCNTRL)
                for i in range(len(alarm_chan)):
                   alram.append(bool((status >> 4)|i))
                return alram
            else:
                print('Error::alram_chan must "list" type')
        except:
            print('Error:get_alram_status error')
            return []

    def get_all_alram_status(self,alarm_chan):
        '''
        读取所有通道的状态
        '''
        try:
            status = self.bus.read_byte_data(self.add,self.INTCNTRL)
            for i in range(len(alarm_chan)):
                   alram.append(bool((status >> 4)|i))
            return alram
        except:
            print('Error:get_all_alram_status error')
            return []

    
    def get_chan_0_data(self):
        '''
        读取通道0 AD转化后的数据
        '''
        try:
            data_H = self.bus.read_byte_data(self.add,self.DATA0_H_ADD)
            data_L = self.bus.read_byte_data(self.add,self.DATA0_L_ADD)
            data = ( data_H << 4 | data_L >> 4)
            print('ch0=%X'%data)
            return data
        except:
            print('Eror::Not get data!! ')
            return 0

    def get_chan_1_data(self):
        '''
        读取通道1 AD转化后的数据
        '''
        try:
            data_H = self.bus.read_byte_data(self.add,self.DATA1_H_ADD)
            data_L = self.bus.read_byte_data(self.add,self.DATA1_L_ADD)
            data = ( data_H << 4 | data_L >> 4)
            print('ch1=%X'%data)
            return data
        except:
            print('Eror::Not get data!! ')
            return 0

    def get_chan_2_data(self):
        '''
        读取通道2 AD转化后的数据
        '''
        try:
            data_H = self.bus.read_byte_data(self.add,self.DATA2_H_ADD)
            data_L = self.bus.read_byte_data(self.add,self.DATA2_L_ADD)
            data = ( data_H << 4 | data_L >> 4)
            print('ch2=%X'%data)
            return data
        except:
            print('Eror::Not get data!! ')
            return 0

    def get_chan_3_data(self):
        '''
        读取通道3 AD转化后的数据
        '''
        try:
            data_H = self.bus.read_byte_data(self.add,self.DATA3_H_ADD)
            data_L = self.bus.read_byte_data(self.add,self.DATA3_L_ADD)
            data = ( data_H << 4 | data_L >> 4)
            print('ch3=%X'%data)
            return data
        except:
            print('Eror::Not get data!! ')
            return 0
    
    def calc_voltage(self,adc_data):
        '''
        计算ADC输入电压
        '''
        adc_data_max = 2**self.adc_bit
        try:
            if(0<=adc_data<=(adc_data_max)):
                voltage = adc_data*(self.voltage/adc_data_max)
            print('voltage= %x V'% voltage)
            return voltage
        except:
            print('Eror::calc_voltage error!! ')
            return 0

#通道阈值设定 
#输入通道有单独的上下限寄存器。每个寄存器是8位，其最小有效位权等于AVDD/256。
# 当输入信号超过上限寄存器的值或低于下限寄存器时，比较器跳闸
    def __set_register_valtage(self,register,vatage):
        #设置选定通道的电压阈值
        try:
            LSB = self.voltage/256
            data = ceil(voltage/LSB)
            print('set voltage = %f'% data )
            self.bus.write_byte_data(self.add,chan_sel,data)
        except:
             print('Error:: __set_chan_valtage function Error!!')

    def set_chan_limit(self,chan_sel,threshold,voltage):
        '''
        选定通道阈值设置
        :param chan_sel:通道选择 [0,1,2,3] 
        :param threshold:上下限选择[upper,lower]
        :param voltage:阈值电压 [0-ref_voltage]

        用法：
        设置通道0 上限电压 2.5V set_chan_limit(chan_sel=0,threshold=upper.voltage=2.5)
        '''
        try:
            if (chan_sel == 0 and threadshold == "uppper"):
                register_add = self.ULR0_ADD

            if (chan_sel == 0 and threadshold == "lower"):
                register_add = self.LLR0_ADD

            if (chan_sel == 1 and threadshold == "uppper"):
                register_add = self.ULR1_ADD

            if (chan_sel == 1 and threadshold == "lower"):
                register_add = self.LLR1_ADD

            if (chan_sel == 2 and threadshold == "uppper"):
                register_add = self.ULR2_ADD

            if (chan_sel == 2 and threadshold == "lower"):
                register_add = self.LLR2_ADD

            if (chan_sel == 3 and threadshold == "uppper"):
                register_add = self.ULR3_ADD

            if (chan_sel == 3 and threadshold == "lower"):
                register_add = self.LLR3_ADD

            if( threshold=="upper" and voltage<=self.voltage):
                __set_register_valtage(register_add,voltage)
            elif( threshold=="lower" and voltage>=0):
                __set_register_valtage(register_add,voltage)
            else:
                print('Error:voltage over range!!')
        except:
            print('Error:: set_ch0_upperlimit function Error!!')
    
    def set_interrupt_config(self,alarm_count,intcnfg,intpol,inttrig):
        '''
        INTCONFIG: 中断配置寄存器设置
        :param alarm_count:设置必须超过比较器阈值限制(上限或下限)才能产生警报的次数。[0-7]
        :param intcnfg:INT 输出管脚设置。 0 alarm 1 busy 2 数据准备：一次转换完整
                            [0-7]        3 busy 4,5 无用 6 数据准备：所有转换完整 7 busy
        :param intpol : INT管脚极性 [0 低电平有效 1 高电平有效] 默认0
        :parma inttrig : INT输出管脚发信号 [0 电平触发时使用的静态信号] 默认0
        '''
        try:
            self.INTCONFIG =0x00
            if(alarm_count in range(8)):
                self.ALMCNT = alarm_count
            else:
                self.ALMCNT = 0x07
            if(intcnfg in range(8)):
                self.INTCNFG =  intcnfg
            else:
                self.INTCNFG = 0
            if(intpol in range(2)):
                self.INTPOL = intpol
            else:
                self.INTPOL = 0
            if(inttrig in range(2)):
                self.INTTRIG = inttrig
            else:
                self.INTTRIG = 0
            
            self.INTCONFIG = (self.ALMCNT<<5)|(self.INTCNFG<<2)|(self.INTPOL<<1)|(self.INTTRIG)
            self.bus.write_byte_data(self.add,self.INTCONFIG_ADD,self.INTCONFIG)
        except:
            print('Error::set_interrupt_config Error!')
    
    def set_sleep(self,CONVCTRL,SLPDIV4,SLPMULT8,SLPTIME):
        '''
        SLPCONFIG:睡眠配置寄存器
        休眠设置
        :param CONVCTRL:该位决定转换控制事件后的转换状态;在INTCONFIG寄存器中查看INTCNFG位。
                                0 = 继续转换，独立于控件事件状态(默认)
                                1 = 一旦发生控制事件，转换将立即停止;必须清除事件才能恢复转换
        :param SLPDIV4: 设置了睡眠时钟的速度.0=睡眠时间分割器为“1”(默认) 1=休眠时间分割器为“4”
        :param SLPMULT8: 0 = 休眠时间乘法器为“1” 1 = 休眠时间乘法器为“8”
        :param SLPTIME : 设置休眠时间(默认为2.5ms)。0=2.5ms 1=5ms 2=10ms 3=20ms 4=40ms 
                                         5=80ms 6=160ms 7=320ms 
        '''
        
        try:
            self.SLPCONFIG = 0x00
            if(conversion_control in range(2)):
                self.CONVCTRL = conversion_control
            else:
                print('Error::CONVCTRL over range')
                self.CONVCTRL = 0
            if(SLPDIV4 in range(2)):
                self.SLPDIV4 = SLPDIV4 
            else:
                print('Error::SLPDIV4 over range')
                self.SLPDIV4 = 0 # div =1
            if(SLPMULT8 in range(2)):
                self.SLPMULT8 = SLPMULT8
            else:
                print('Error::SLPDIV4 over range')
                self.SLPMULT8 = 0 # mul=1
            if(SLPTIME in range(8)):
                self.SLPTIME = SLPTIME 
            else:
                print('Error::SLPDIV4 over range')
                self.SLPTIME = 0 # 2.5ms
            
            self.SLPCONFIG = (self.CONVCTRL<<6)|(self.SLPDIV4<<5)|(self.SLPMULT8<<4)|(self.SLPTIME)
            self.bus.write_byte_data(self.add,self.SLPCONFIG_ADD,self.SLPCONFIG)
        except:
            print('Error::set_sleep Error!')
        

    def set_acquire(self,tacq):
        '''
        ACQCONFIG: 获取配置寄存器
        设定了在转换前获取信号的时间
            
        :param tacq:信号采集时间(us) [6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38]
            
        '''
        try:
            self.ACQCONFIG = 0x00
            tcq_int = [6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38]
            if(tacq in tcq_int):
                for i in range(16):
                    if(tacq == tcq_int[i]):
                        ACQTIME =i  # ACQTIME:信号采集时间值 默认0，Tacq=ACQTIME*2us +6us
            else:
                print('Error::tacq over range')
                ACQTIME = 0
            
            self.ACQCONFIG = ACQTIME
            self.bus.write_byte_data(self.add,self.ACQCONFIG_ADD,self.ACQCONFIG)
        except:
            print('Error::set_acquire Error!')
    
    def set_pwerup(self,CALCNTL,PWRCONPOL,PWRCONEN,T_pwr):
        '''
        PWRCONFIG:上电配置寄存器

        :param CALCNTL:校准调节 0=在模式控制寄存器中设置CH3选择CH3输入被路由到MUXOUT引脚。(默认)
                        1= 在模式控制寄存器中设置CH3将MUXOUT引脚连接到ADND
        :param PWRCONPOL: PWRCON引脚极性。 0 =低电平有效（默认）1=高电平有效
        :param PWRCONEN: PWRCON 使能。0=disabled（defaul） 1=enabled
        :param T_pwr:powerup 时间（us).[0,2,4,6,8,10,12,14,...,32]
        PWRUPTIME: 设定power-up时间值。默认=0 T_pwr=PWRUPTIME*2us
        '''
        try:
            self.PWRCONFIG = 0x00
            if(CALCNTL in range(2)):
                self.CALCNTL = CALCNTL
            else:
                print('Error::CALCNTL over range')
                self.CALCNTL = 0

            if(PWRCONPOL in range(2)):
                self.PWRCONPOL = PWRCONPOL
            else:
                print('Error::PWRCONPOL over range')
                self.PWRCONPOL = 0

            if(PWRCONEN in range(2)):
                self.PWRCONEN = PWRCONEN
            else:
                print('Error::PWRCONEN over range')
                self.PWRCONEN = 0

            PWRUPTIME = T_pwr/2
            if(PWRUPTIME in range(2)):
                self.PWRUPTIME = PWRUPTIME
            else:
                print('Error::PWRCONEN over range')
                self.PWRUPTIME = 0
            
            self.PWRCONFIG = (self.CALCNTL<<7)|(self.PWRCONPOL<<6)|(self.PWRCONEN<<5)|(self.PWRUPTIME)
            self.bus.write_byte_data(self.add,self.PWRCONFIG_ADD,PWRUPTIME)
        except:
            print('Error::set_pwerup Error!')

    def get_device_ID(self):
        '''
        RESET:软件复位和设备ID寄存器
        当A0确定设备ID的最后一位(0001100A0)时，读取该寄存器，将返回设备ID。
        '''
        try:
            return self.bus.read_byte_data(self.add,self.RESET_ADD)
        except:
            print('Error::get_device_ID!')
    
    def reset(self):
        '''
        RESET:软件复位和设备ID寄存器
        对该寄存器写入0xAA,将对ADS7924产生一个软件复位
        '''
        try:
            self.bus.write_byte_data(self.add,self.RESET_ADD,self.soft_reset_value)
        except:
            print('Error::reset Error!')

    

            
              






                   
                

            

    
        




