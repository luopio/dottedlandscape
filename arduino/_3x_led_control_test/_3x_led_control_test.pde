#include <Matrix.h>

/*  
  create three Matrix instances
  order: data, clock, load
*/
Matrix oneMatrix = Matrix(10, 11, 12);
Matrix twoMatrix = Matrix(2, 3, 4);
Matrix threeMatrix = Matrix(5, 6, 7);

void setup()
{ 

}

int x = 0;
int y = 0;
int y2 = 1;
int y3 = 2;

void loop()
{
  /*
  oneMatrix.write(0, y, 1);
  oneMatrix.write(1, y, 1);
  oneMatrix.write(2, y, 1);
  oneMatrix.write(3, y, 1);
  oneMatrix.write(4, y, 1);
  oneMatrix.write(5, y, 1);
  oneMatrix.write(6, y, 1);
  */
  oneMatrix.write(x, y, 1);
  /*
  twoMatrix.write(0, y2, 1);
  twoMatrix.write(1, y2, 1);
  twoMatrix.write(2, y2, 1);
  twoMatrix.write(3, y2, 1);
  twoMatrix.write(4, y2, 1);
  twoMatrix.write(5, y2, 1);
  twoMatrix.write(6, y2, 1);
  */
  twoMatrix.write(x, y2, 1);
  
  /*
  threeMatrix.write(0, y3, 1);
  threeMatrix.write(1, y3, 1);
  threeMatrix.write(2, y3, 1);
  threeMatrix.write(3, y3, 1);
  threeMatrix.write(4, y3, 1);
  threeMatrix.write(5, y3, 1);
  threeMatrix.write(6, y3, 1);
  */
  threeMatrix.write(x, y3, 1);
  
  delay(75);                      // wait a little bit
  oneMatrix.clear();               // clear the screen for next animation frame
  twoMatrix.clear();               // clear the screen for next animation frame
  threeMatrix.clear();               // clear the screen for next animation frame
  y++; y2++; y3++; x++;
  if(y == 8) { y = 0; }
  if(y2 == 8) { y2 = 0; }
  if(y3 == 8) { y3 = 0; }
  
  if(x == 8) { x = 0; }
}


void write_D() {
  oneMatrix
}
