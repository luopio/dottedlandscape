#include <Sprite.h>
#include <Matrix.h>

/* create a new Matrix instance
data  (din) load  (load) clock (clk)
*/
Matrix myMatrix = Matrix(10, 12, 11);

/* create a new Sprite instance
   8 pixels wide, 4 pixels tall
*/
Sprite wave = Sprite(
  8, 8,
  B11111111,
  B00000000,
  B00000000,
  B10101010,
  B00000000,
  B01010101,
  B00000000,
  B00000000
);

void setup()
{ 
}

int x = 0;
int y = 7;

void loop()
{
  // myMatrix.write(x, 0, wave);     // place sprite on screen
  // myMatrix.write(x - 8, 2, wave); // place sprite again, elsewhere on screen
  myMatrix.write(y,0,1);
  myMatrix.setBrightness(1);
  myMatrix.write(y,1,1);
  myMatrix.setBrightness(5);
  myMatrix.write(y,2,1);
  myMatrix.setBrightness(10);
  myMatrix.write(y,3,1);
  myMatrix.write(y,4,1);
  myMatrix.setBrightness(15);
  myMatrix.write(y,5,1);
  myMatrix.write(y,6,1);
  myMatrix.write(y,7,1);
  
  delay(75);                      // wait a little bit
  myMatrix.clear();               // clear the screen for next animation frame
  y++;
  if(y == 8)                      // if reached end of animation sequence
  {
    y = 0;                        // start from beginning
  }
}

