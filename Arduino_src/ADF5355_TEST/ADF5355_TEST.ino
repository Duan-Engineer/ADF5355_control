/*
ADF5355 Evalution Board Control Software

 Circuit:
 ADF5355 Evalution Board attached to pins 6, 7, 10 - 13:
 CE: pin 2
 SPI_CS: pin 10
 SPI_MOSI: pin 11
 SPI_MISO: pin 12
 SPI_SCK: pin 13

 created 12 March 2021
 modified 14 August 2010
 by Duan Xuefeng
 */

// the Board communicates using SPI, so include the library:
#include <SPI.h>
// set pin 10 as the slave select for the digital pot:
const int slaveSelectPin = 10;

// pins used for the connection with the sensor
// the other you need are controlled by the SPI library):
const int chipSelectPin = 2;

int i;
//Rigisters
unsigned long R[13]={0x201910,0x1478DC1,0X8AAFFFF2,
0X3,0X36008B84,0X800025,
0X35404076,0X120000E7,0X102d0428,
0X5047CC9,0X0067A,0X61300B,0X1041C};
/*char data[52]={0x00,0x01,0x04,0x1C,0x00,
              ,0x61,0x30,0x0B,0x00,0xC0,0x06,0x7A,0x05,0x04,0x7C,0xC9,0x10,0x2D,0x04,0x28,0x12
              ,0x00,0x00,0xE7,0x35,0x40,0x40,0x76,0x00,
              ,0x80,0x00,0x25,0x36,0x00,0x8B,0x84,0x00,0x00,0x00,0x03,0x8A,0xAF,0xFF,0xF2,0x01,0x47,0x8D
              ,0xC1,0x00,0x20,0x19,0x10}*/
void setup() {
  Serial.begin(9600);
  Serial.println("Serial init Success!!");
  Serial.println("Start Setup...");
  // set the slaveSelectPin as an output:
  pinMode(slaveSelectPin, OUTPUT);
  // initalize the  data ready and chip select pins:
  pinMode(chipSelectPin, OUTPUT);
  // take the chip select high to select the device::
  digitalWrite(slaveSelectPin, HIGH);
  digitalWrite(chipSelectPin, HIGH);
  // start the SPI library:
  SPI.begin();
  //SPI.beginTransaction(SPISettings(4000000, MSBFIRST, SPI_MODE0));
  Serial.println("Setup OK!");
  Serial.println("Start Initialization...");
  
  // give the sensor time to set up:
  delay(100);
}

void loop() {
  for(int i=12;i>-1;i--)
  {
    Serial.println("Writing R"+String(i));
    writeRegister(R[i]);
    delay(20);
    Serial.println("0x"+String(R[i],HEX)+" Writen to device");
  }
}

//Sends a write command to ADF5355
void writeRegister(unsigned long RegisterValue) {
  
  byte value[4],temp;
  // take the SS pin low to select the chip:
  digitalWrite(slaveSelectPin, LOW);
  //delay(1);
  //  send in the address and value via SPI:
  /*for(int n=0;n<4;n++)
  {
    //temp= byte(((RegisterValue<<(n*8)) & 0xFF000000)>>24 & 0XFF);
    //temp= byte(((RegisterValue>>(n*8)) & 0x000000FF));
    SPI.transfer(temp);
    //Serial.println("0x"+String(temp,HEX)+" Writen to device");
  }*/
  SPI.transfer(&RegisterValue,4);
  //delay(1);
  // take the SS pin high to de-select the chip:
  digitalWrite(slaveSelectPin, HIGH);
  //delay(1);
}
