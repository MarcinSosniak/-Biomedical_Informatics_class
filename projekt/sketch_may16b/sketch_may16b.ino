/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com  
*********/

#include <Wire.h>
#include "BluetoothSerial.h"

#if !defined(CONFIG_BT_ENABLED) || !defined(CONFIG_BLUEDROID_ENABLED)
#error Bluetooth is not enabled! Please run `make menuconfig` to and enable it
#endif

#define SINGLE_WINDOW_SIZE 16
#define WINDOW_COUNT 5
#define TERM_READ_DELAY_MS 55
#define FIVE_POINT_STENCIL_H ((SINGLE_WINDOW_SIZE*TERM_READ_DELAY_MS)/1000.0)
#define DEVICE_PREFIX "ESP32TERM"

BluetoothSerial SerialBT;
 
uint8_t address = 0x48;

class ProbeGatherer
{
  int32_t windows_sum[WINDOW_COUNT]={0};
  double current_point=0; 
  int32_t current_sum=0;
  uint16_t probe_id=0;
  bool new_point=false;
  uint16_t points_gathered=0;
public:
  ProbeGatherer() {}
  bool is_new_point(){return new_point;}
  double get_point() {new_point=false; return current_point;}
  void add_probe(int16_t probe)
  {
    current_sum+=probe; 
    if(probe_id ==SINGLE_WINDOW_SIZE -1 )
    {
      for(uint16_t i=WINDOW_COUNT-1 ;i>=1;i--)
      {
        windows_sum[i] = windows_sum[i-1];
      }
      windows_sum[0]=current_sum;
      if(points_gathered<WINDOW_COUNT)
      {
        points_gathered++;
      }
      current_point=0.0;
      for(uint16_t i=0;i<points_gathered;i++)
      {
        current_point +=windows_sum[i];
      }
      current_point /= (SINGLE_WINDOW_SIZE * points_gathered*256); // remember
      probe_id=0;
      
      current_sum=0;
      new_point=true;
    }
    else
    {
      probe_id++;
    }
  }
  #if WINDOW_COUNT >= 5
  double get_derative()
  {
    return (((double) (windows_sum[WINDOW_COUNT-1] -8*windows_sum[WINDOW_COUNT-2] +8*windows_sum[WINDOW_COUNT-4] -windows_sum[WINDOW_COUNT-5]))/(256.0*SINGLE_WINDOW_SIZE))
    /(12*FIVE_POINT_STENCIL_H);
  }
  #endif
  void debug_serial_print()
  {
    Serial.print("probe_id : ");
    Serial.print(probe_id);
    Serial.print("\n");
    Serial.print("buffor : \n[");
    for(uint16_t i=0;i<WINDOW_COUNT;i++)
    {
      Serial.print(" ");
      Serial.print(((double)windows_sum[i])/(256.0*SINGLE_WINDOW_SIZE),3);
      Serial.print(";\n");
    }
    Serial.print("]\n");
  }
};

ProbeGatherer pg;

void setup() {
  Wire.begin();
  Serial.begin(115200);
  Serial.println("\nI2C Scanner");
  SerialBT.begin("ESP32test"); //Bluetooth device name

}

int16_t get_temp()
{
  //Serial.println("sending register address as 1 byte of data");
  Wire.beginTransmission(address);
  Wire.write((byte)0x00);
  Wire.endTransmission();
  //Serial.println("requesteing 2 bytes of data");
  uint8_t bytes_returned= Wire.requestFrom(address,(uint8_t) 2);    // request 2 bytes from slave device #2
  int id=0;
  byte bytes[2]={0,0};
  while(Wire.available())    // slave may send less than requested
  { 
    byte c = Wire.read(); // receive a byte as character
    bytes[id]=c;
    id++;
    //Serial.print(c);         // print the character
  }

  int16_t temp;
  temp =  ((uint16_t) bytes[0]) << 8;
  temp = temp | bytes[1];
  return temp;
}
void send_bluetooth_double(double dVal)
{
  char suff[]={'\0'};
  char pref[]={'\0'};
  send_bluetooth_double(dVal,pref,suff);
}
void send_bluetooth_double(double dVal, const char* suffix)
{
  char pref[]={'\0'};
  send_bluetooth_double(dVal,pref,suffix);
}

void send_bluetooth_double(double dVal, const char* prefix, const char* suffix)
{
  char table[128];
  sprintf(table,"%s%.8f%s\n",prefix,dVal,suffix);
  for(uint32_t i=0;i < 32;i++)
  {
    if(table[i]=='\0')
    {
      break;
    }
    SerialBT.write(table[i]);
  }
}

void send_data_with_prefix(double temp, double derative)
{
  char table[128]={'0'};
  sprintf(table,"%s %.8f %.8f\n",DEVICE_PREFIX,temp,derative);
  Serial.print(table);
  for(uint32_t i=0;i < 128;i++)
  {
    if(table[i]=='\0')
    {
      break;
    }
    SerialBT.write(table[i]);
  }
}


void loop() {
  byte error;  
  pg.add_probe(get_temp());
  if(pg.is_new_point())
  {
    double dtemp = pg.get_point();
    double derative = pg.get_derative();
    send_data_with_prefix(dtemp,derative);
    pg.debug_serial_print();
//    Serial.print(dtemp,8);
//    Serial.print("C\n");
//    Serial.print("Derative: ");
//    Serial.print(derative,8);
//    Serial.print("[C/s]\n");
//    send_bluetooth_double(dtemp,"C");
//    send_bluetooth_double(derative,"Derative: ","[C/s]");
  }
 
  //pg.debug_serial_print();
  delay(TERM_READ_DELAY_MS);          
}
