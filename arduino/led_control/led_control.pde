#include <Sprite.h>
#include <Matrix.h>

/* 
 Create a new Matrix instance to control the MAX7219
 data (din)  load (load)  clock (clk)
*/
// Matrix ledMatrix = Matrix(10, 12, 11);

Matrix blueMatrix = Matrix(10, 11, 12);
Matrix greenMatrix = Matrix(2, 3, 4);
Matrix redMatrix = Matrix(5, 6, 7);

int y = 0;
int yr = 0;
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
      
    //redMatrix.clear();
    //blueMatrix.clear();
    //greenMatrix.clear();
    y = 0;
    
    while(y < 8) 
    {
      // get incoming frame data
      redByte = Serial.read();
      greenByte = Serial.read();
      blueByte = Serial.read();
      
      // mind bogling 1..0 indexing!
      // first byte for is for the red row
      /*
      ledMatrix.write(1, y, redByte & 1);
      ledMatrix.write(2, y, redByte & 2);
      ledMatrix.write(3, y, redByte & 4);
      ledMatrix.write(4, y, redByte & 8);
      ledMatrix.write(5, y, redByte & 16);
      ledMatrix.write(6, y, redByte & 32);
      ledMatrix.write(7, y, redByte & 64);
      ledMatrix.write(0, y, redByte & 128);
      */
      
      // reverting the coordinates for turned panel
      if(y == 0) {
        yr = 1;
      } else if(y == 7) {
        yr = 0;
      } else {
        yr = y + 1;
      }
      
      redMatrix.write(yr, 7, redByte & 1);
      redMatrix.write(yr, 6, redByte & 2);
      redMatrix.write(yr, 5, redByte & 4);
      redMatrix.write(yr, 4, redByte & 8);
      redMatrix.write(yr, 3, redByte & 16);
      redMatrix.write(yr, 2, redByte & 32);
      redMatrix.write(yr, 1, redByte & 64);
      redMatrix.write(yr, 0, redByte & 128);
      
      greenMatrix.write(yr, 7, greenByte & 1);
      greenMatrix.write(yr, 6, greenByte & 2);
      greenMatrix.write(yr, 5, greenByte & 4);
      greenMatrix.write(yr, 4, greenByte & 8);
      greenMatrix.write(yr, 3, greenByte & 16);
      greenMatrix.write(yr, 2, greenByte & 32);
      greenMatrix.write(yr, 1, greenByte & 64);
      greenMatrix.write(yr, 0, greenByte & 128);
      
      blueMatrix.write(yr, 7, blueByte & 1);
      blueMatrix.write(yr, 6, blueByte & 2);
      blueMatrix.write(yr, 5, blueByte & 4);
      blueMatrix.write(yr, 4, blueByte & 8);
      blueMatrix.write(yr, 3, blueByte & 16);
      blueMatrix.write(yr, 2, blueByte & 32);
      blueMatrix.write(yr, 1, blueByte & 64);
      blueMatrix.write(yr, 0, blueByte & 128);
      
      y++;
    }
    
  }
  
  Serial.flush();
  delay(100);      
}

