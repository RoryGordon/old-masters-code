#include <SoftwareSerial.h>
SoftwareSerial ble(2, 3); // RX, TX

byte testbyte = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  ble.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  ble.write(testbyte);
  testbyte ++;
  delay(1000);


}
