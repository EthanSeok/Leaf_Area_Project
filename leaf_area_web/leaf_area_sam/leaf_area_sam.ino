#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

const int debounceTime = 500;  // 딜레이 시간을 밀리초 단위로 설정

void setup() {
  lcd.init();
  lcd.backlight();
  Serial.begin(9600);
  pinMode(5, INPUT_PULLUP); // 5번 핀 ==> Capture 버튼
  pinMode(4, INPUT_PULLUP); // 4번 핀 ==> Send 버튼
}

void loop() {
  int buttonState = digitalRead(5);
  int exitButtonState = digitalRead(4);

  if (buttonState == LOW) {
      Serial.println("CAPTURE");
      lcd.clear();
      lcd.print("Capture complete");
      delay(debounceTime);  // 버튼 입력 후 일정 시간 동안 대기
  }

  if (exitButtonState == LOW) {
      Serial.println("SEND");
      lcd.clear();
      lcd.print("Send Complete");
      delay(debounceTime);  // 버튼 입력 후 일정 시간 동안 대기
  }
}
