#include <stdio.h> 
#include <math.h>
#define R04    0X36008B84    // DB4=0
#define R04_EN 0X36008B94 //DB4=1

double RFOUT=425000.123;
double  F_pfd=10000.0; 
unsigned long INTR,FRAC1R,FRAC2R;
int RF_Divider,RF_Select=3,X2,RFB;
double MOD1=16777216.0;
double MOD2=16383.0;//max 16383
int AMP=4,I_BLEED_N;
unsigned long R[13]={0X201540,0X1,0X12,0X3,0X36008B84,0X800025,
					0X35406076,0X120000E7,0X102D0428,0X5047CC9,
					0XC0067A,0X61300B,0X1041C}; //参考10MHZ，输出850MHZ，4分频 
long gcd(long x, long y)
{
    while(y^=x^=y^=x%=y);
    return x;
}
/*
void calc( double F_voc,double  F_pfd,float F_chsp,int Divider)
{
	double inter_value;
	double MOD1=16777216.0;
	//printf("F_voc=%.6f\r\n",F_voc);
	//printf("F_pfd=%f\r\n",F_pfd);
	double N = F_voc/F_pfd;
	//printf("N=%.20f\r\n",N);
	int INT = int(N);
	//printf("INT=%d\r\n",INT);
	double f = modf(N,&inter_value);  //inter_value中存放整数部分,f中存放小数部分
	//printf("f=%.16f\r\n",f);	
	int FRAC1 = int(f*MOD1);
	//printf("FRAC1=%d\r\n",FRAC1);
	float gcd_value = gcd(F_pfd*1000000,F_chsp*1000000);
	printf("gcd=%f\r\n",gcd_value);
	int MOD = (F_pfd*1000000)/gcd_value;
	printf("MOD=%d\r\n",MOD);
	int MOD2=16383;
	//printf("MOD2=%d\r\n",MOD2);
	//double a= (N-INT)*MOD1;
	//printf("a=%.16f\r\n",a);
	int FRAC2 =((N-INT)*MOD1-FRAC1)*MOD2;
	//printf("FRAC2=%d\r\n",FRAC2);
	double N_calc=(INT+(FRAC1+(double(FRAC2)/MOD2))/MOD1);
	//printf("N_calc=%.17f\r\n",N_calc);
	double RF_out=N_calc*F_pfd/Divider;
	//printf("RF_out=%.6f\r\n",RF_out);
	printf("%4.6f%10d%10d%10d%10d\r\n",F_voc,INT,FRAC1,FRAC2,MOD2);
}*/
void freq_sel(double  RFOUT)
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
void calc_new()
{
	printf("===========calc RFout=================\r\n");
	RFB=1;X2=0; // RFB off  
    freq_sel(RFOUT);
    printf("freqences select success !\r\n");
    printf("RF_Select=%X",RF_Select);
    printf("%15s%15s%15s%15s%15s\r\n","F_voc","INT","FRAC1","FRAC2","RFOUT_CLC");
    double Fvco=RFOUT*RF_Divider;
    if (X2==1) Fvco= Fvco/2; //6.8GHZ < RFOUT < 13.6GHz 
    //printf("Fvco=%.12f KHz\r\n",Fvco);
    INTR = Fvco/F_pfd;//
    //printf("INTR=%d\r\n",INTR);
    double FRAC = (Fvco-INTR*F_pfd)/F_pfd;
    //printf("FRAC=%.12f\r\n",FRAC);
    FRAC1R=FRAC*MOD1;
    //printf("FRAC1R=%d\r\n",FRAC1R);
    double remain1= FRAC1R/MOD1;
    double remain2=(FRAC-remain1);
    FRAC2R=remain2*MOD1*MOD2;
    //printf("FRAC2R=%d\r\n",FRAC2R);
    double RFout_c=(INTR+(FRAC1R+FRAC2R/MOD2)/MOD1)*F_pfd;
    //printf("%.6f\r\n",(INTR+(FRAC1R+FRAC2R/MOD2)/MOD1)*F_pfd);
    printf("%4.7f%15d%15d%15d    %8.6f\r\n",Fvco,INTR,FRAC1R,FRAC2R,RFout_c);
    
}

void updateRegister(unsigned long INT,unsigned long FRAC1,unsigned long FRAC2,unsigned long MOD2R)
{
	
	R[0] = 0X00200000 | (INT<<4);
	R[1] = 0X1 | (FRAC1<<4);
	R[2] = 0X2 | (MOD2R<<4)|(FRAC2<<17);
	R[6] = 0X35006076|(RF_Select<<21);	
}
void WriteRegister32(const unsigned long value)   //Programme un registre 32bits
{
  /*digitalWrite(ADF5355_LE, LOW);
  for (int i = 3; i >= 0; i--)          // boucle sur 4 x 8bits
  SPI.transfer((value >> 8 * i) & 0xFF); // d茅calage, masquage de l'octet et envoi via SPI
  digitalWrite(ADF5355_LE, HIGH);
  digitalWrite(ADF5355_LE, LOW);*/
}

void SetADF5355()  // Programme tous les registres de l'ADF5355
{ for (int i = 13; i >= 0; i--)  // programmation ADF5355 en commencant par R12
    WriteRegister32(R[i]);
}

void delay(int time)
{
	
}
void updateADF5355()
	{
		AMP=3;I_BLEED_N=9; // N=9	
		WriteRegister32((RF_Select<<21)|(I_BLEED_N<<13)|RFB<<7|(0x35000076)); //R6
		printf("R6=0X%X\r\n",(RF_Select<<21)|(I_BLEED_N<<13)|RFB<<7|(0x35000076));
		
		if (RFB==1)
			printf("RFB = OFF\r\n");
		else
			printf("RFB = ON\r\n");
		
		
		WriteRegister32(4|R04_EN);                                 //R4  DB4=1
		printf("R4=0X%X\r\n",(4|R04_EN));
		WriteRegister32(2|(1000<<4)|(FRAC2R<<18));                 //R2
		printf("R2=0X%X\r\n",(2|(1000<<4)|(FRAC2R<<18)));
		WriteRegister32(1|(FRAC1R<<4));                            //R1
		printf("R1=0X%X\r\n",(1|(FRAC1R<<4)));
		WriteRegister32(0|INTR<<4);                                //R0
		printf("R0=0X%X\r\n",(0|INTR<<4));
		WriteRegister32(R04);										//R4  DB4=0
		printf("R4=0X%X\r\n",R04);
		delay(3); //  pause de 3 ms pour stabilisation VCO
		WriteRegister32(0|0X200000|(INTR<<4));                     //R0
		printf("R0=0X%X\r\n",0|0X200000|(INTR<<4));
	}
int main()
	{
		//double F_voc;
		//printf("input the VOC : ");
    	//scanf("%f",&F_voc);
    	//printf("%10s%10s%10s%10s%10s\r\n","F_voc","INT","FRAC1","FRAC2","MOD2"); 
    	//for(long i=425000000;i<850000001;i++)
    	//{
    		//calc(6795.12,10.000000,5,8);
    	//}
    	//calc_Register(340,207030,4617,5461);
    	
    	calc_new();
    	//updateADF5355();
    	updateRegister(340,1650,4795,5461);
    	//printf("OK");
    	
	}
