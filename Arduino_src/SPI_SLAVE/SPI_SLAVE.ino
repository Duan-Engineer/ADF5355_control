#include <SPI.h>
char buff [52];
volatile byte indx;
volatile boolean process;
 
void setup () {
  Serial.begin (9600);
  pinMode(MISO, OUTPUT); //将MISO设置为输出以便数据发送主机
  SPCR |= _BV(SPE); //在从机模式下打开SPI通讯
  indx = 0; // 初始化变量
  process = false;
  SPI.attachInterrupt(); //打开中断
}
 
 
ISR (SPI_STC_vect) // SPI中断程序
{
  byte c = SPDR; // 从SPI数据寄存器读取字节
  if (indx < sizeof buff) {
    buff [indx] = c; // 将数据保存在数组buff中的下一个索引中
    //if (indx == 52) //检查是否是结尾字符,即检测字符是否是\r回车符
      process = true;
  }
}
 
void loop () {
  if (process) {
    process = false; //重置通讯过程
    Serial.print(buff[indx]); //在串口监视器上打印接收到的buff数据
    indx = 0; //重置index,即为重置buff索引
  }
}
