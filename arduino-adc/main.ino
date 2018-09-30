int x = 0;
int y = 0;
int z = 0;

void writeInt(int f){
  byte *b = (byte *) &f;
  Serial.write(b[0]);
  Serial.write(b[1]);
}

void setup(){
  Serial.begin(19200);
}

void loop(){
  x = analogRead(A0);
  y = analogRead(A1);
  z = analogRead(A2);
  Serial.write(0xFF);
  writeInt(x);
  writeInt(y);
  writeInt(z);
}

