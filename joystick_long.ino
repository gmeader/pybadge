#include <Adafruit_Arcada.h>

Adafruit_Arcada arcada;

const unsigned long shortPress = 50; millisec
const unsigned long  longPress = 500;
typedef struct Buttons {
    unsigned long counter=0;
    uint8_t prevState = 0;
    uint8_t currentState;
    uint8_t lastButton = 0;
} Button;

uint8_t lastButtonState = 0;
uint8_t buttonState = 0;
unsigned long lastMillis = 0;

unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 25; 
unsigned long counter = 0;

// create a Button variable type
Button button;

void setup(void) {
  while (!Serial) delay(10);     // wait till serial port is ready!

  Serial.begin(115200);
  Serial.println("Controls Test");

  if (!arcada.arcadaBegin()) {
    Serial.print("Failed to begin");
    while (1);
  }
  arcada.displayBegin();
  arcada.display->fillScreen(ARCADA_BLACK);
  arcada.setBacklight(250);
  arcada.display->println(" Press buttons ");
}

void loop()
{

  // every 15 seconds, clear the screen
    if(millis()-lastMillis > 15000){
      lastMillis = millis();
      arcada.display->fillScreen(ARCADA_BLACK);
      arcada.display->setCursor(10,10);
      arcada.display->println(" Press buttons ");
      counter = 0;
    }

  // check the buttons
  button.currentState = arcada.readButtons();
  // has it changed?
  if (button.currentState != button.prevState) {
      delay(25);
      // update status in case of bounce
      button.currentState = arcada.readButtons();
      if (button.currentState != 0) {
          // a new press event occured
          // record when button went down
          button.counter = millis();
          button.lastButton = button.currentState;  // remeber which button was pressed
      }

      if (button.currentState == 0) {
          // but no longer pressed, how long was it down?
          unsigned long currentMillis = millis();
          
          if ((currentMillis - button.counter >= shortPress) && !(currentMillis - button.counter >= longPress)) {
              // short press detected. 
              do_buttons(button.lastButton,0);
          }
          if ((currentMillis - button.counter >= longPress)) {
              // the long press was detected
              do_buttons(button.lastButton,1);
          }
      }
      // used to detect when state changes
      button.prevState = button.currentState;
  } 
 
/*
   // read the state of the switches 
   uint8_t reading = arcada.readButtons();
  // check to see if you just pressed a button
  // and you've waited long enough
  // since the last press to ignore any noise

  // If the buttons changed, due to noise or pressing:
  if (reading != lastButtonState) {
    // reset the debouncing timer
    lastDebounceTime = millis();
    lastButtonState = reading;
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    // whatever the reading is at, it's been there for longer than the debounce
    // delay, so take it as the actual current state:

    // if the button state has changed:
    if (reading != buttonState) {
      buttonState = reading;
      do_buttons(reading);
      lastButtonState = reading;
    }
  }
*/
} // loop

void do_buttons(uint8_t buttons, bool pressType) {
  if (buttons != 0) {
      if (pressType) {
        //Serial.print("^ ");
        arcada.display->print("long  ");
      }
      if (buttons & ARCADA_BUTTONMASK_UP) {
        //Serial.print("^ ");
        arcada.display->print("UP ");
      }
      if (buttons & ARCADA_BUTTONMASK_DOWN) {
        ///Serial.print("v ");
        arcada.display->print("DOWN ");
      }
      if (buttons & ARCADA_BUTTONMASK_LEFT) {
        Serial.print("< ");
        arcada.display->print(" LEFT ");
      }
      if (buttons & ARCADA_BUTTONMASK_RIGHT) {
        //Serial.print("> ");
        arcada.display->print(" RIGHT ");
      }
      if (buttons & ARCADA_BUTTONMASK_A) {
        //Serial.print("A ");
           arcada.display->setTextColor(ARCADA_BLACK,ARCADA_WHITE);
           arcada.display->print(" A ");
        }
      if (buttons & ARCADA_BUTTONMASK_B) {
        //Serial.print("B ");
           arcada.display->setTextColor(ARCADA_GREEN);
           arcada.display->setTextSize(2);
           arcada.display->print(" B ");
        
      }
      if (buttons & ARCADA_BUTTONMASK_START) {
        //Serial.println("Sta ");
        arcada.display->fillScreen(ARCADA_BLACK);
        arcada.display->setCursor(0,0);
        arcada.display->print("START ");
      }
      
      if (buttons & ARCADA_BUTTONMASK_SELECT) {
        //Serial.println("Sel ");
        arcada.display->fillScreen(ARCADA_RED);
        arcada.display->setTextColor(ARCADA_YELLOW);
        //arcada.display->setCursor(0,0);
        arcada.display->print("SELECT ");
      }
      counter++;
      arcada.display->print(counter);
      arcada.display->println();
      arcada.display->setTextSize(1);
  }
}
