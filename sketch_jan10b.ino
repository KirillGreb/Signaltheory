#include <Servo.h>

#define LEFT_MOTOR_PIN 2  // Пин левого мотора
#define RIGHT_MOTOR_PIN 3 // Пин правого мотора

Servo left_motor;
Servo right_motor;

const int STRAIGHT_SPEED = 1500; // Скорость прямо
const int TURN_SPEED = 1300;    // Скорость при повороте

void setup() {
    Serial.begin(9600);               // Инициализация последовательного порта
    left_motor.attach(LEFT_MOTOR_PIN);  // Присоединяем левый мотор
    right_motor.attach(RIGHT_MOTOR_PIN); // Присоединяем правый мотор
}

void loop() {
    if (Serial.available() > 0) {
        char command = Serial.read(); // Получаем команду с Raspberry Pi

        if (command == 'L') {
            turnLeft();
        } else if (command == 'R') {
            turnRight();
        } else if (command == 'F') {
            goForward();
        }
    }
}

void goForward() {
    left_motor.writeMicroseconds(STRAIGHT_SPEED);
    right_motor.writeMicroseconds(STRAIGHT_SPEED);
}

void turnLeft() {
    left_motor.writeMicroseconds(TURN_SPEED);     // Уменьшаем скорость левого
    right_motor.writeMicroseconds(STRAIGHT_SPEED); // Правый мотор движется быстрее
    delay(500);  // Время поворота
    goForward();
}

void turnRight() {
    left_motor.writeMicroseconds(STRAIGHT_SPEED); // Левый мотор движется быстрее
    right_motor.writeMicroseconds(TURN_SPEED);     // Уменьшаем скорость правого
    delay(500);  // Время поворота
    goForward();
}