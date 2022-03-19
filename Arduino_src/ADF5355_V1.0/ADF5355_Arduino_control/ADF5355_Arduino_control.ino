//author:DUAN
//Date:2021/3/18
#include <SPI.h>
#define ADF5355_LE 10
#define R04 0X36008B84    // DB4=0
#define R04_EN 0X36008B94 //DB4=1
byte X2=1,AMP=4;
unsigned long RFout=4225600000;//Hz;

long RF_Divider;
unsigned long RF_Select,RFB,FVCO;
//unsigned long FVCO=6000000;//KH
unsigned long MOD1=16777216;
unsigned long MOD2=16383;//max 16383

unsigned long INTR,FRAC1R,FRAC2R,I_BLEED_N;
unsigned long FPFD=61440000;

uint32_t registers [13] = {0x200E60, 0xC4EC4E1, 0xC043E82, 0x3, 0x36008B84, 0x800025, 0x35A12076, 0x12000007, 0x102D0428, 0xB0B3CC9, 0xC0107A, 0x61300B, 0x1041C}; // 187,5 MHz with a 26 MHz Reference Clock
void freq_sel(unsigned long  RFOUT)
{
    if((53125<=RFOUT)&&(RFOUT<106250))   {RF_Divider=64;RF_Select=6;}  // RFOUT = Frequence de sortie en KHz
    if((106250<=RFOUT)&&(RFOUT<212500))  {RF_Divider=32;RF_Select=5;}  
    if((212500<=RFOUT)&&(RFOUT<425000))  {RF_Divider=16;RF_Select=4;}
    if((425000<=RFOUT)&&(RFOUT<850000))  {RF_Divider=8;RF_Select=3;} 
    if((850000<=RFOUT)&&(RFOUT<1700000)) {RF_Divider=4;RF_Select=2;}
    if((1700000<=RFOUT)&&(RFOUT<3400000)){RF_Divider=2;RF_Select=1;}
    if((3400000<=RFOUT)&&(RFOUT<6800000)){RF_Divider=1;RF_Select=0;}
    if((6800000<=RFOUT)&&(RFOUT<=13600000)){RF_Divider=1;RF_Select=0;X2=1;RFB=0;} // et mettre la sortie X2
}
void WriteRegister32(const uint32_t value)   //Programme un registre 32bits
{
  digitalWrite(ADF5355_LE, LOW);
  for (int i = 3; i >= 0; i--)          // boucle sur 4 x 8bits
  SPI.transfer((value >> 8 * i) & 0xFF); // décalage, masquage de l'octet et envoi via SPI
  digitalWrite(ADF5355_LE, HIGH);
  digitalWrite(ADF5355_LE, LOW);
}

void SetADF5355()  // Programme tous les registres de l'ADF5355
{ for (int i = 13; i >= 0; i--)  // programmation ADF5355 en commencant par R12
    WriteRegister32(registers[i]);
}

void updateADF5355() { // mise à jour des registres

   AMP=3;I_BLEED_N=9; // N=9
   WriteRegister32((RF_Select<<21)|(I_BLEED_N<<13)|RFB<<7|(0x35000076)); //R6      0X35000076 == R6 avec RF_divider et I_BLEED
   //TEST=((RF_Select<<21)|(I_BLEED_N<<13)|0x35000076);
   //Serial.print("TEST=");Serial.println(TEST,HEX);
    Serial.println("");
   if (RFB==1) {Serial.println ("RFB = OFF");} else {Serial.println("RFB = ON");}         
   Serial.print("RF_Select=");Serial.println(RF_Select,DEC);// 
   Serial.print("MOD2 = ");Serial.println(MOD2);
   Serial.print("FRAC2 = ");Serial.println(FRAC2R);
   WriteRegister32(4|R04_EN);                                 //R4  DB4=1
   WriteRegister32(2|(1000<<4)|(FRAC2R<<18));                 //R2
   Serial.print("FRAC1 = ");Serial.println(FRAC1R);
   WriteRegister32(1|(FRAC1R<<4));                            //R1
   Serial.print("INT= ");Serial.println(INTR);
   WriteRegister32(0|INTR<<4);                                //R0   
   WriteRegister32(R04);                                      //R4  DB4=0
   delay(3); //  pause de 3 ms pour stabilisation VCO
   WriteRegister32(0|0X200000|(INTR<<4));                     //R0               
}
//======================setup==================
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.println("******"+String(RFout));
  Serial.println(RFout);
  Serial.println("Synthesizer ADF5355 Control");
  Serial.println("Author:DUAN");
  pinMode(ADF5355_LE, OUTPUT);          // Setup pins
  digitalWrite(ADF5355_LE, HIGH);
  SPI.begin();                          // Init SPI bus
  SPI.setDataMode(SPI_MODE0);           // CPHA = 0 et Clock positive
  SPI.setBitOrder(MSBFIRST);            // poids forts en tête
  
  Serial.println("RFout="+String(RFout,16));
  calc();
  //updateADF5355();
  Serial.println("Update"); 
}
void calc()
{
    RFB=1;X2=0; // RFB off  
    freq_sel(RFout);
    RF_Divider=1;
    Serial.println("freqences select success !");
    FVCO=RFout*RF_Divider;
    double Fvco_temp= RFout*RF_Divider;
    Serial.println("FVCO="+String(FVCO));
    long ref=FPFD;
    INTR = FVCO/ref;//参考频率10MHz
    Serial.println("INTR="+String(INTR));
    double FRAC = (FVCO-INTR*ref)/ref;
    Serial.println("FRAC="+String(FRAC));
    FRAC1R=FRAC*MOD1;
    //Serial.println("a="+String(FRAC*MOD1,12));
    Serial.println("FRAC1R="+String(FRAC1R));
    double remain1= FRAC1R/double(MOD1);
    //Serial.println("remain1="+String(remain1,12));
    double remain2=(FRAC*10E6-remain1*10E6);
    //Serial.println("remain2="+String(remain2,12));
    FRAC2R=remain2/10E6*MOD1*MOD2;
    Serial.println("FRAC2R="+String(FRAC2R));
    Serial.println("===========calc RFout=================");
    Serial.println(String((INTR+(FRAC1R+FRAC2R/MOD2)/MOD1)*ref,6));
    
}
void loop() {
  // put your main code here, to run repeatedly:
  
}
