#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup() {
  lcd.init();
  lcd.backlight();
  Serial.begin(9600);
  pinMode(5, INPUT_PULLUP); // 5번 핀 ==> 버튼
  pinMode(4, INPUT_PULLUP); // 4번 핀 ==> 추가 버튼
}

void loop() {
  int buttonState = digitalRead(5);
  int exitButtonState = digitalRead(4); // Exit button state

  if (buttonState == LOW) {
    Serial.println("YES");
    while (digitalRead(5) == LOW); // 버튼이 놓아질 때까지 대기
  }

  if (exitButtonState == LOW) {
    Serial.println("NO");
    while (digitalRead(4) == LOW); // NO 버튼이 놓아질 때까지 대기
  }
  
  if (Serial.available() > 0) {
    String leafArea = Serial.readString();
    lcd.setCursor(0, 0);
    lcd.print("Leaf Area:");
    lcd.setCursor(0, 1);
    lcd.print(leafArea + " cm^2");
  }

  delay(1500);
}
