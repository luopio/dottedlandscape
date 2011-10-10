#include <Sprite.h>
#include <Matrix.h>

/* 
 Create a new Matrix instance to control the MAX7219
 data (din)  load (load)  clock (clk)
*/
Matrix ledMatrix = Matrix(10, 12, 11);

int y = 0;
byte headerByte = 0;
byte redByte = 0;
byte blueByte = 0;
byte greenByte = 0;

void setup()
{ 
  Serial.begin(19200);
}

void loop()
{
  if (Serial.available() > 0) 
  {
    // look for the header byte that should be 0
    // used for syncing
    while(Serial.available()) 
    {
      headerByte = Serial.read();
      if(headerByte == 255) {
        break;
      }
    }
      
    ledMatrix.clear();
    y = 0;
    while(y < 8) 
    {
      // get incoming frame data
      redByte = Serial.read();
      greenByte = Serial.read();
      blueByte = Serial.read();
      
      // mind bogling 1..0 indexing!
      // first byte for is for the red row
      ledMatrix.write(1, y, redByte & 1);
      ledMatrix.write(2, y, redByte & 2);
      ledMatrix.write(3, y, redByte & 4);
      ledMatrix.write(4, y, redByte & 8);
      ledMatrix.write(5, y, redByte & 16);
      ledMatrix.write(6, y, redByte & 32);
      ledMatrix.write(7, y, redByte & 64);
      ledMatrix.write(0, y, redByte & 128);
      // green..
      // blue..
      
      y++;
    }
    
  } 
  // Serial.flush();
  // delay(100);    
  

}

