#include <Sprite.h>
#include <Matrix.h>

/* create a new Matrix instance
data  (din) load  (load) clock (clk)
WRONG ORDER?!?!?!?!? 13=>12, 1=>10, 12=>11

order: data, clock, load
*/
Matrix myMatrix = Matrix(10, 12, 11);

/* create a new Sprite instance
   8 pixels wide, 4 pixels tall
*/
/*
Sprite wave = Sprite(
  8, 8,
  B11111111,
  B00000001,
  B00000001,
  B10101011,
  B00000001,
  B01010101,
  B11111111,
  B00000001
);
*/

void setup()
{ 

}

int x = 0;
int y = 7;

void loop()
{
  // myMatrix.write(x, 0, wave);     // place sprite on screen
  // myMatrix.write(x - 8, 2, wave); // place sprite again, elsewhere on screen
  
  myMatrix.clear();               // clear the screen for next animation frame
  
  myMatrix.write(0, y, 1);
  // myMatrix.setBrightness(1);
  myMatrix.write(1, y, 1);
  // myMatrix.setBrightness(5);
  myMatrix.write(2, y, 1);
  // myMatrix.setBrightness(10);
  myMatrix.write(3, y, 1);
  myMatrix.write(4, y, 1);
  // myMatrix.setBrightness(15);
  myMatrix.write(5, y, 1);
  myMatrix.write(6, y, 1);
  myMatrix.write(7, y, 1);
  
  delay(75);                      // wait a little bit
  y++;
  if(y == 8)                      // if reached end of animation sequence
  {
    y = 0;                        // start from beginning
  }
}

