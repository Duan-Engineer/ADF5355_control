/*
 * nsrt_lo_switch.c
 * 切换命令格式：pos:n(n取1-8）
 * 查询位置命令：query?
 * 查询位置后返回：pos:n(n为1-8，若为9则可能没有连接微波开关
 * 所有命令以\n结尾,即EOF=\n
 * Created: 2020/9/21 13:50:44
 * Author : YAN HAO
 */ 

//熔丝位设置启动时间延时0ms
//#define F_CPU 11059200UL
#define F_CPU 12000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>
#include <math.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <avr/eeprom.h>
#include <avr/wdt.h>


//微波开关控制端口 PORTC
#define SW_DRV_PORT	PORTC
#define SW_DRV_DDR	DDRC
#define SW_DRV_PIN	PINC

//微波开关信号返回端口 PORTB
#define SW_QUE_PORT PORTB
#define SW_QUE_DDR	DDRB
#define SW_QUE_PIN	PINB

/**************************************
	typedef=>
		ANM:Asynchronous Normal mode
		ADSM:Asynchronous Double Speed mode
		SMM:Synchronous Master mode
**************************************/
typedef enum {ANM,ADSM,SMM}USARTModeType;

#define BAUD_RATE 9600



unsigned char rx_count = 0;
unsigned char rx_buffer[256];
unsigned char tx_buffer[256];
unsigned char cmd[8] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};
unsigned char retunrValue[8] = {0x7F, 0xBF, 0xDF, 0xEF, 0xF7, 0xFB, 0xFD, 0xFE};
unsigned char swPosition = 90;
unsigned char dst[3][20];
unsigned char dstConut = 0;
unsigned char readCompleteFlage = 0;
	

/*********************************************************************************************
函  数  名：void usart_init(unsigned char channel, unsigned char mode, unsigned int baudrate)
描      述：串口初始化子程序
被调用函数：Nothing
输 入参 数：channel是有多个串口的话进行串口选择0-1
			MODE是串口工作模式，0为一般模式；1为异步双速模式；2为同步主模式
			BAUD是波特率值
输 出参 数：无
返  回  值：无
其      它：无
*********************************************************************************************/
void UsartInit(unsigned char channel, USARTModeType MODE, unsigned int BAUD)
{
	if( channel == 0 )
	{
		UCSR0A = 0x00;	
		if( MODE == ANM )
		{
			UBRR0 = F_CPU/16/BAUD-1;
		}
		else if( MODE == ADSM )
		{
			UBRR0 = F_CPU/8/BAUD-1;
		}
		else if( MODE == SMM )
		{
			UBRR0 = F_CPU/2/BAUD-1;
		}
		else
		{
			UBRR0 = F_CPU/16/BAUD-1;
		}
		//USART0 Control and Status Register C – UCSR0C
		//同步操作
		UCSR0C |= (0<<UMSEL0);
		//无奇偶冲效验		
		UCSR0C |= (0<<UPM0);
		//1位停止位			
		UCSR0C |= (0<<USBS0);
		//8位数据位			
		UCSR0C |=(3<<UCSZ0);
		//允许发送、接收			
		UCSR0B = (1<<RXEN0) | (1<<TXEN0);
		//接收中断使能
		UCSR0B |= (1<<RXEN0);
		//接收结束中断使能
		UCSR0B |= (1<<RXCIE0);	
	
	}
	if( channel == 1 )
	{
		UCSR1A = 0x00;
		if( MODE == ANM )
		{
			UBRR1 = F_CPU/16/BAUD-1;
		}
		else if( MODE == ADSM )
		{
			UBRR1 = F_CPU/8/BAUD-1;
		}
		else if( MODE == SMM )
		{
			UBRR1 = F_CPU/2/BAUD-1;
		}
		else
		{
			UBRR1 = F_CPU/16/BAUD-1;
		}	
		//波特率9600bps
		//UBRR1H = 0;
		//UBRR1L = 77;
		//UBRR1 = 77;
		//USART0 Control and Status Register C – UCSR0C
		//同步操作
		UCSR1C |= (0<<UMSEL1);
		//无奇偶冲效验		
		UCSR1C |= (0<<UPM1);
		//1位停止位			
		UCSR1C |= (0<<USBS1);
		//8位数据位			
		UCSR1C |=(3<<UCSZ1);
		//允许发送、接收			
		UCSR1B = (1<<RXEN1) | (1<<TXEN1);
		//接收中断使能
		UCSR1B |= (1<<RXEN1);
		//接收结束中断使能
		UCSR1B |= (1<<RXCIE1);	
	}
	
}

/****************************
	串口1字符发送程序
****************************/
void PutChar(unsigned char c)
{
	while ( ! ( UCSR1A & (1<<UDRE1)));
	UDR1 = c;
}

/****************************
	串口0字符发送程序
****************************/
void PutChar0(unsigned char c)
{
	while ( ! ( UCSR0A & (1<<UDRE0)));
	UDR0 = c;
}

/*******************************
	串口1字符串发送程序
*******************************/
void PutString(unsigned char *s)
{
	while(*s)
	{
		PutChar(*s);
		s++;
	}
}

/*******************************
	串口0字符串发送程序
*******************************/
void PutString0(unsigned char *s)
{
	while(*s)
	{
		PutChar0(*s);
		s++;
	}
}


int split(char dst[][20], char* str, const char* spl)
{
	int n = 0;
	char *result = NULL;
	result = strtok(str, spl);
	while( result != NULL )
	{
		strcpy(dst[n++], result);
		result = strtok(NULL, spl);
	}
	return n;
}

long long  RFout=6700123456;
long double  F_pfd=10000000.0;
unsigned long INTR,FRAC1R,FRAC2R;
int RF_Divider,RF_Select=0,X2,RFB;
double MOD1=16777216.0;
double MOD2=16383.0;//max 16383
uint32_t R[13]={0X201540,0X1,0X12,0X3,0X36008B84,0X800025,
				0X35406076,0X120000E7,0X102D0428,0X5047CC9,
				0XC0067A,0X61300B,0X1041C}; //参考10MHZ，输出850MHZ，4分频

void myprintf(char *str,...)
{
	char buf[128];
	unsigned char i = 0;
	va_list ptr;
	va_start(ptr,str);
	vsprintf(buf,str,ptr);
	while(buf[i])
	{
		PutChar(buf[i]);
		i++;
	}
}

//==========ADF5355=================
void freq_sel(double  RFOUT)
{
	if((53125<=RFOUT)&&(RFOUT<106250))   {RF_Divider=64;RF_Select=6;}  // RFOUT = Frequence de sortie en KHz
	if((106250<=RFOUT)&&(RFOUT<212500))  {RF_Divider=32;RF_Select=5;}
	if((212500<=RFOUT)&&(RFOUT<425000))  {RF_Divider=16;RF_Select=4;}
	if((425000<=RFOUT)&&(RFOUT<850000))  {RF_Divider=8;RF_Select=3;}
	if((850000<=RFOUT)&&(RFOUT<1700000)) {RF_Divider=4;RF_Select=2;}
	if((1700000<=RFOUT)&&(RFOUT<3400000)){RF_Divider=2;RF_Select=1;}
	if((3400000<=RFOUT)&&(RFOUT<6800000)){RF_Divider=1;RF_Select=0;}
	//if((6800000<=RFOUT)&&(RFOUT<=13600000)){RF_Divider=1;RF_Select=0;X2=1;RFB=0;} // et mettre la sortie X2
}

void calc()
{
	
	//RFB=1;X2=0; // RFB off
	freq_sel(RFout/1000);
	myprintf("freqences select success !\r\n");
	myprintf("RF_Select=%X\r\n",RF_Select);
	myprintf("===========calc RFout=================\r\n");
	//myprintf("%15s%15s%15s%15s%15s\r\n","F_voc","INT","FRAC1","FRAC2","RFOUT_CLC");
	//myprintf("RFOUT=%lld KHz \r\n",RFout);
	//myprintf("RFOUT1=%164u KHz \r\n",425000123);
	long double Fvco=RFout*RF_Divider;
	//myprintf("Fvco=%Ld KHz\r\n",Fvco);
	INTR =Fvco/F_pfd;
	myprintf("INTR=%d\r\n",INTR);
	long double FRAC = (Fvco-INTR*F_pfd)/F_pfd;
	//myprintf("FRAC=%Lf\r\n",FRAC);
	FRAC1R=((Fvco-INTR*F_pfd)/F_pfd)*MOD1;
	myprintf("FRAC1R=%ld\r\n",FRAC1R);
	double remain1= FRAC1R/MOD1;
	double remain2=(FRAC-remain1);
	FRAC2R=remain2*MOD1*MOD2;
	myprintf("FRAC2R=%ld\r\n",FRAC2R);
	double RFout_c=(INTR+(FRAC1R+FRAC2R/MOD2)/MOD1)*F_pfd;
	//myprintf("RFOUT=%.6f\r\n",RFout_c);
	//myprintf("%4.7f%15d%15d%15d    %8.6f\r\n",Fvco,INTR,FRAC1R,FRAC2R,RFout_c);
	//myprintf("b=%d",FRAC1R);
	
}
void myprintlong(long long tempj)
{
	PutChar( tempj/100000000 + 0x30);
	PutChar( tempj/10000000%10 + 0x30);
	PutChar( tempj/1000000%10 + 0x30);
	PutChar( tempj/100000%10 + 0x30);
	PutChar( tempj/10000%10 + 0x30);
	PutChar( tempj/1000%10 + 0x30);
	PutChar( tempj/100%10 + 0x30);
	PutChar( tempj/10%10 + 0x30);
	PutChar( tempj%10 + 0x30);
}
int main (void)
{
	/* Insert system clock initialization code here (sysclk_init()).*/
	
	//UsartInit(0, ANM, 9600);
	
	UsartInit(1, ANM, BAUD_RATE);
	PutString("Serial1 init OK!\n");
	calc();
	//freq_sel(RFOUT);
	//myprintf("RF=%d",RF_Select);
	//PutChar(RF_Select%10+0x30);
	
	/*while(1)
	{
		if( readCompleteFlage == '1')
		{
			//PutChar(rx_count);
			PutString("recv!\n");
			
			readCompleteFlage = '0';
			rx_count = 0;
		}	
	}*/
	
	
	
	
	//GPIO INIT
	/*SW_DRV_DDR = 0XFF;
	SW_DRV_PORT = 0X00;
	SW_QUE_DDR = 0X00;
	SW_QUE_PORT = 0X00;*/
	
	
	
	/*long double j1 = 123.6543226;
	long double j2 = 112.2469886;
	unsigned long tempj = 0;
	char jj1[12] ;
	memset(jj1, '\0', 12);
	printf("%f",jj);
	PutString("Current position is will\n");
	tempj = j1*1000000+5;
	//tempj = 2147483647;
	PutChar( tempj/100000000 + 0x30);
	PutChar( tempj/10000000%10 + 0x30);
	PutChar( tempj/1000000%10 + 0x30);
	PutChar( tempj/100000%10 + 0x30);
	PutChar( tempj/10000%10 + 0x30);
	PutChar( tempj/1000%10 + 0x30);
	PutChar( tempj/100%10 + 0x30);
	PutChar( tempj/10%10 + 0x30);
	PutChar( tempj%10 + 0x30);
	
	PutChar('a');
	
	
	tempj = j2*1000000;

	PutChar( tempj/100000000 + 0x30);
	PutChar( tempj/10000000%10 + 0x30);
	PutChar( tempj/1000000%10 + 0x30);
	PutChar( tempj/100000%10 + 0x30);
	PutChar( tempj/10000%10 + 0x30);
	PutChar( tempj/1000%10 + 0x30);
	PutChar( tempj/100%10 + 0x30);
	PutChar( tempj/10%10 + 0x30);
	PutChar( tempj%10 + 0x30);
	PutChar('b');*/
	
	
	
	
	
	sei();
	/*float temp_f;
	unsigned char temp_s[10];*/
	
	//memset(dst, '\0', sizeof(dst) );

	while(1)
	{
		_delay_ms(10);
	
		//查询微波开关位置
		/*switch (SW_QUE_PIN)
		{
			case 0x7F:
				swPosition = '1';
				break;
			case 0xBF:
				swPosition = '2';
				break;
			case 0XDF:
				swPosition = '3';
				break;
			case 0XEF:
				swPosition = '4';
				break;
			case 0XF7:
				swPosition = '5';
				break;
			case 0XFB:
				swPosition = '6';
				break;
			case 0XFD:
				swPosition = '7';
				break;
			case 0XFE:
				swPosition = '8';
				break;
			default:
				swPosition = '9';//no position
				break;
		}*/
		if( readCompleteFlage == '1')
		{
			cli();
			//dstConut = split(dst, rx_buffer, ":");
			//PutString("recv ok1!\n");
			//微波开关切换
			/*if( strncmp( strlwr(dst[0]), "pos", 3 ) == 0 )
			{
				//切换位置在[1-8]之间,与微波开关8个位置对应
				if( dst[1][0] >= '1' && dst[1][0] <= '8' )
				{
					//当前位置不是要切换的位置才进行切换
					if( dst[1][0] != swPosition)
					{
						SW_DRV_PORT = cmd[dst[1][0]-0x30-1];
						_delay_ms(10);
					}
					else
					{
						PutString("Current position is will\n");
					}
				}	
			}
			else if( strncmp( strlwr(dst[0]), "query?", 6 ) == 0 )
			{
				char temp[10];
				memset(temp, '\0', sizeof(temp));
				sprintf(temp,"%s:%c\n","pos",swPosition);
				PutString(temp);	
			}*/
			//memset(dst, '\0', sizeof(dst) );
			readCompleteFlage = 0;
			sei();
		}	
	}
}

/***********************
	串口1接收中断程序
	接收主机命令
***********************/
ISR(USART1_RX_vect)
{
	rx_buffer[rx_count++] = UDR1;
	//PutChar(UDR1);
	//PutString("recv!\n");
	readCompleteFlage = '1';
	/*if( rx_buffer[rx_count-1] == 0x0a )
	{
		rx_buffer[rx_count] = '\0';
		rx_count = 0;
		readCompleteFlage = '1';	
	}*/
}	
