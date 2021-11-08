

/* BNO055 and Nano */
/* as v6 but with different IMU channels */

#include <Wire.h>
#include <PacketSerial.h>
#include <SoftwareSerial.h>

#define SERIAL
#define BLE

#ifdef SERIAL
PacketSerial myPacketSerial;
#endif
#ifdef BLE
SoftwareSerial ble(2, 3); // RX, TX
#endif
/* Timing */
unsigned long SAMPLE_INTERVAL=10000;  // 50 milliseconds
unsigned long TIME0=0;

/* BNO055 */
//configuration addresses
const byte BNO055_I2C_ADDR=0x28; //default I2C address
const byte BNO055_CHIP_ID_ADDR=0x00;
const byte OPR_MODE_ADDR=0x3D;
const byte UNIT_SEL_ADDR=0x3B;
const byte AXIS_MAP_SIGN_ADDR=0x42;
//const byte GYR_Config_1_ADDR=0x00;
//const byte GYR_Config_0_ADDR=0x38;
//const byte ACC_Config_ADDR=0x0B;

//configuration data
const byte OPR_MODE_CONFIG=B00000000;  // see tables 3-3, 3-5 xxxx0000 CONFIGMODE
const byte OPR_MODE_ACCGYRO=B00000101; // see tables 3-3, 3-5 xxxx0101 ACCGYRO
const byte OPR_MODE_IMU=B00001000;     // see tables 3-3, 3-5 xxxx1000 IMU (fusion mode, 100Hz)
const byte OPR_MODE_NDOF=B00001100;     // see tables 3-3, 3-5 xxxx1100 NDOF (fusion mode, 100Hz)

const byte UNIT_SEL=B00000110; //see table 3-11: xxx0xxxx centigrade; xxxxx1xx radians; xxxxxx1x rad/s; xxxxxxx0 m/s^2
const byte AXIS_MAP_SIGN=B00000110; //see section 3.4: xxxxx1xx -ve x-axis; xxxxxx1x -ve y-axis; xxxxxxx0 +ve z-axis

const byte ACC_Config=B00000000; //see table 3-8: 000xxxxx normal; xxx100xx 125Hz (000 7.8Hz); xxxxxx00 2g (01 4g)


// first data address
const byte ACC_DATA_Y_LSB_ADDR=0x0A;
const byte GYR_DATA_Z_LSB_ADDR=0x18;
const byte GRV_DATA_X_LSB_ADDR=0x2E;

const byte ACC_INDEX=4;
const byte GYR_INDEX=6;
const byte IMU_INDEX=8;
const byte SUM_INDEX=12;

//const byte LIA_DATA_X_LSB_ADDR=0x28; // linear xyz accn data in 6 bytes starting here (in NDOF fusion mode)
byte buf[SUM_INDEX]; //initialise empty array of 25 bytes (time=4, imu=18, encoder=2, checksum=1)

// encoder
//const byte encoder0PinA = 2; // pin D2 on arduino
//const byte encoder0PinB = 3; // pin D3 on arduino
//volatile short encoder0Pos = 0; // signed 2 bytes
//volatile short encoder0PosCopy = 0; // copy for reading when interrupts are disabled


void setup()
{
  /* serial port */
  #ifdef SERIAL
  Serial.begin(9600);//, SERIAL_8N1); //57600
  myPacketSerial.setStream(&Serial);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  #endif
  #ifdef BLE
  ble.begin(9600);
  #endif
  // myPacketSerial.setPacketHandler(&onPacketReceived);  //only needed to receive packets
  
  /* BNO055 */
  Wire.begin(); // join i2c bus
  delay(1000);
  // read chip ID
  byte BNO055_CHIP_ID=0;
  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(BNO055_CHIP_ID_ADDR);
  Wire.endTransmission();
  Wire.requestFrom(BNO055_I2C_ADDR,(byte)1);
  BNO055_CHIP_ID = Wire.read();
  //Serial.print("BNO055 chip ID: ");
  //Serial.println(BNO055_CHIP_ID);

  // set operating mode
  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(OPR_MODE_ADDR);
  Wire.write(OPR_MODE_CONFIG);
  Wire.endTransmission(); //send bytes
  delay(20); //delay 20ms for mode switching


  // debug - read units
  //Wire.beginTransmission(BNO055_I2C_ADDR);
  //Wire.write(UNIT_SEL_ADDR);
  //Wire.endTransmission();
  //Wire.requestFrom(BNO055_I2C_ADDR,(byte)1);
  //UNIT_BEFORE = Wire.read();
  //Serial.print("UNIT_BEFORE: ");
  //Serial.println(UNIT_BEFORE);

  // set units
  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(UNIT_SEL_ADDR);
  Wire.write(UNIT_SEL);
  Wire.endTransmission(); //send bytes


  // debug - read units
  //Wire.beginTransmission(BNO055_I2C_ADDR);
  //Wire.write(UNIT_SEL_ADDR);
  //Wire.endTransmission();
  //Wire.requestFrom(BNO055_I2C_ADDR,(byte)1);
  //UNIT_AFTER = Wire.read();
  //Serial.print("UNIT_AFTER: ");
  //Serial.println(UNIT_AFTER);

  // set axes
  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(AXIS_MAP_SIGN_ADDR);
  Wire.write(AXIS_MAP_SIGN);
  Wire.endTransmission(); //send bytes

  // set operating mode
  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(OPR_MODE_ADDR);
  Wire.write(OPR_MODE_IMU);
  Wire.endTransmission(); //send bytes
  delay(20); //delay 20ms for mode switching

  // encoder pins
  //pinMode(encoder0PinA, INPUT);
  //pinMode(encoder0PinB, INPUT);

  // encoder pin on interrupt 0 (pin 2)
  //attachInterrupt(digitalPinToInterrupt(encoder0PinA), doEncoderA, RISING);
  TIME0 = millis();
}

/*
void doEncoderA() {
  if (bitRead(PIND,encoder0PinA) == bitRead(PIND,encoder0PinB)) {
    encoder0Pos--;
  } else {
    encoder0Pos++;
  }
}
*/

void loop()
{   
  word checksum=0;
  
//  Serial.println("RESET");
  buf[0] = (byte)(TIME0);    //convert long into 4 bytes. truncate using cast
  buf[1] = (byte)(TIME0>>8);
  buf[2] = (byte)(TIME0>>16);
  buf[3] = (byte)(TIME0>>24);
  
  for (byte i = 0; i < ACC_INDEX; i++)
  {
      checksum+=buf[i];   // sum the first 4 bytes
  }
  
  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(ACC_DATA_Y_LSB_ADDR);
  Wire.endTransmission();
  Wire.requestFrom(BNO055_I2C_ADDR, (byte)2); // request 6 bytes for acc data

  for (byte i = ACC_INDEX; i < GYR_INDEX; i++)
  {
      buf[i] = (byte) Wire.read(); // read each byte in turn from the i2c bus
      checksum+=buf[i];
  }

  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(GYR_DATA_Z_LSB_ADDR);
  Wire.endTransmission();
  Wire.requestFrom(BNO055_I2C_ADDR, (byte)2); // request 2 bytes for gyr data

  for (byte i = GYR_INDEX; i < IMU_INDEX; i++)
  {
      buf[i] = (byte) Wire.read(); // read each byte in turn from the i2c bus
      checksum+=buf[i];
  }

  Wire.beginTransmission(BNO055_I2C_ADDR);
  Wire.write(GRV_DATA_X_LSB_ADDR);
  Wire.endTransmission();
  Wire.requestFrom(BNO055_I2C_ADDR, (byte)4); // request 2 bytes for imu data

  for (byte i = IMU_INDEX; i < SUM_INDEX; i++)
  {
      buf[i] = (byte) Wire.read(); // read each byte in turn from the i2c bus
      checksum+=buf[i];
  }

  /*
  // read the encoder counter (convert short to 2 bytes)
  noInterrupts(); // turn off interrupts to avoid risk of reading encoder0Pos when it is being incremented
  encoder0PosCopy=encoder0Pos;
  interrupts();   // turn interrupts back on
  buf[22]=encoder0PosCopy;
  buf[23]=(byte)(encoder0PosCopy>>8);

  //add to checksum
  checksum+=buf[22];
  checksum+=buf[23];
  */
  buf[SUM_INDEX] = checksum & 0xFF; //write lowest byte of sum to last element of buf (checksum)

  buf[SUM_INDEX+1] = 0x00;
  #ifdef SERIAL
  myPacketSerial.send(buf,SUM_INDEX+1); // Send the array. This is terminated with 0x00
  #endif
  #ifdef BLE
  ble.write(buf, SUM_INDEX+1);
  #endif
  /*
  for (byte i = 0; i < 25; i++)
  {
    Serial.print(buf[i]);
    Serial.print(',');
  }
  Serial.println();               // debugging code
  */
  //Serial.print(TIME0);            // debugging code
  //Serial.print(encoder0short);    // debugging code 
//  Serial.print("Before: ");
//  Serial.print(millis()- TIME0);
//  Serial.print(", ");
//  Serial.println(TIME0);
//  TIME0 = millis();
  /*
  while (millis()- TIME0 < SAMPLE_INTERVAL)
  {
    
     // wait for time to increment by SAMPLE_INTERVAL
  }
  */
  delay(50);
//  Serial.print("After:");
//  Serial.println(millis()-TIME0);
}
