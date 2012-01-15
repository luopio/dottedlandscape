import processing.opengl.*;

/* calculates some crucial values from 
  valopesä testing samples */

PImage[] images = new PImage[6];
String[] imageFiles = new String[6];

short curImage = 0;
int[] vHistogram = new int[256];
int[] rHistogram = new int[256];
int[] gHistogram = new int[256];
int[] bHistogram = new int[256];
int curMaxValue = 0;
float averageBrightness = 0;
float relativeMaximum = 0;
boolean calculationsDone = false;
PFont font;

void setup() {
  font = loadFont("Ubuntu-Regular-14.vlw");
  textFont(font, 14);
  // String path = "/home/lauri/Documents/gradu/pesavertailu/kuvat/";
  String path = "/home/lauri/Documents/gradu/pesavertailu/uudet_kuvat/";
/*  imageFiles[0] = "cc_IMG_3834.JPG";
  imageFiles[1] = "cc_IMG_3835.JPG";
  imageFiles[2] = "cc_IMG_3836.JPG";
  imageFiles[3] = "cc_IMG_3837.JPG"; 
  imageFiles[4] = "cc_IMG_3838.JPG";
  imageFiles[5] = "cc_IMG_3839.JPG";
  imageFiles[6] = "cc_IMG_3840.JPG";
  imageFiles[7] = "cc_IMG_3840.JPG";
  imageFiles[8] = "cc_IMG_3876.JPG"; */

  imageFiles[0] = "IMG_3884.JPG";
  imageFiles[1] = "IMG_3885.JPG";
  imageFiles[2] = "IMG_3887.JPG";
  imageFiles[3] = "IMG_3888.JPG"; 
  imageFiles[4] = "IMG_3893.JPG";
  imageFiles[5] = "IMG_3914.JPG";

  for(int i = 0; i < images.length; i++) {
    images[i] = loadImage( path+imageFiles[i] );
  }
  size(1000, 480, OPENGL);
  frameRate(5);
}


void draw() {
  if(!calculationsDone) {
    // reset all
    for(int i = 0; i < 256; i++) {
      vHistogram[i] = rHistogram[i] = gHistogram[i] = bHistogram[i] = 0;
    }
    averageBrightness = 0;
    relativeMaximum = 0;
    curMaxValue = 0;
    
    // resize image. note this weakends data accuracy, but with these 
    // marginals not much
    if(images[curImage].height > 485) {
      println("resize " + images[curImage].height);
      images[curImage].resize(0, 480);
    }
    
    images[curImage].loadPixels();
    
    for(int i = 0; i < images[curImage].width * images[curImage].height; i++) {
      color c = images[curImage].pixels[i];
      vHistogram[(int)brightness(c)]++;
      rHistogram[(int)red(c)]++;
      gHistogram[(int)green(c)]++;
      bHistogram[(int)blue(c)]++;
      averageBrightness += brightness(c);
    }
    averageBrightness /= (images[curImage].width * images[curImage].height);
    // calculate the maximum value so that the histogram can be scaled
    for(int i = 0; i < 255; i++) {
      curMaxValue = max(vHistogram[i], curMaxValue);
      curMaxValue = max(rHistogram[i], curMaxValue);
      curMaxValue = max(gHistogram[i], curMaxValue);
      curMaxValue = max(bHistogram[i], curMaxValue);
    }
    relativeMaximum = curMaxValue / (float)(images[curImage].width * images[curImage].height);
    println("maximum: " + curMaxValue);
    calculationsDone = true;
  }
   
  background(0);
  // image(images[curImage], 0, 0);
  image(images[curImage], -100, 0);
  
  //blend(images[curImage], 0, 0, images[curImage].width, images[curImage].height,
  //      500, 0, images[curImage].width, images[curImage].height, DODGE);
  
  // draw the histogram
  // int hx = 580;
  int hx = 680;
  int hy = 90;
  int hh = 300;
  fill(10, 10, 10);
  stroke(20, 20, 20);
  rect(hx - 2, hy - 2, 257, hh + 2);
  for(int i = 0; i < 255; i++) {
    stroke(200, 200, 200, 200);
    int val = (int)(vHistogram[i] / (float)curMaxValue * hh);
    line(hx + i, hy + hh, hx + i, hy + hh - val);
    
    stroke(200 + hx/255. * 40.0, 0, 0, 200);    
    val = (int)(rHistogram[i] / (float)curMaxValue * hh);
    line(hx + i, hy + hh, hx + i, hy + hh - val);
    
    stroke(0, 200 + hx/255. * 40.0, 0, 200);    
    val = (int)(gHistogram[i] / (float)curMaxValue * hh);
    line(hx + i, hy + hh, hx + i, hy + hh - val);

    stroke(0, 0, 200 + hx/255. * 40.0, 200);    
    val = (int)(bHistogram[i] / (float)curMaxValue * hh);
    line(hx + i, hy + hh, hx + i, hy + hh - val);
  }
  stroke(255, 255, 255);
  fill(255, 255, 255);
  textAlign(LEFT);
  text("average brightness: " + averageBrightness, hx, 20);
  // useless text("relative maximum: " + relativeMaximum, hx, 40);
  textAlign(CENTER);
  // y-axis
  text(" max: \n" + curMaxValue, hx - 28, hy);
  text("0", hx - 13, hy + hh);
  // x-axis
  text("0", hx, hy + hh + 20);
  text("255", hx + 245, hy + hh + 20);
}

void keyPressed() {
  if(keyCode == RIGHT) {
    println("right");
    if(curImage < imageFiles.length - 1) { curImage++; }
  } else if(keyCode == LEFT) {
    println("left");
    if(curImage > 0) { curImage--; }
  } else if(key == 's') {
    String filename = imageFiles[curImage] + "_result.png";
    println("save file to " + filename);
    saveFrame(filename);
  }
  
  calculationsDone = false;
  println(curImage);
}
