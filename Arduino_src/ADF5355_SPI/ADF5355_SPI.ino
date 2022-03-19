const int slaveSelectPin = 10;
const int mosiPin = 11;
const int clkPin = 13;
const int cePin = 2;
unsigned long R[13]={0x201910,0x1478DC1,0X8AAFFFF2,
0X3,0X36008B84,0X800025,
0X35404076,0X120000E7,0X102d0428,
0X5047CC9,0X0067A,0X61300B,0X1041C};
void setup() {
  // put your setup code here, to run once:
  pinMode(slaveSelectPin,OUTPUT);
  pinMode(mosiPin,OUTPUT);
  pinMode(clkPin,OUTPUT);
  pinMode(cePin,OUTPUT);
  digitalWrite(cePin,HIGH);
  digitalWrite(slaveSelectPin,HIGH);
  digitalWrite(clkPin,LOW);
  digitalWrite(mosiPin,HIGH);
  for(int i=12;i>-1;i--)
  {
    shif(R[i]);
  }
  
  
}

void loop() {
  // put your main code here, to run repeatedly:

}

void shif(unsigned long R)
{
  digitalWrite(slaveSelectPin,LOW);
  for(int n=31;n>-1;n--)
  {
    digitalWrite(mosiPin,(R>>n)&0x00000001);
    digitalWrite(clkPin,HIGH);
    delay(1);
    digitalWrite(clkPin,LOW);
    delay(1);
  }
  digitalWrite(slaveSelectPin,HIGH);
  delay(10);
}
