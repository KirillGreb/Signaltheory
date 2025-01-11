import cv2
import serial
import time
import numpy as np

# Настройки последовательного порта (скорость и порт могут отличаться)
SERIAL_PORT = "/dev/ttyACM0"  # Для Arduino на USB
SERIAL_BAUDRATE = 9600

# Настройки камеры
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

try:
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
    print("Подключено к Arduino")
except serial.SerialException as e:
    print(f"Ошибка подключения к Arduino: {e}")
    exit(1)

camera = cv2.VideoCapture(0)  # Открыть камеру Raspberry Pi
camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)


def process_frame(frame):
    """
    Обработка кадра: обнаружение объектов и принятие решения.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # Конвертируем в черно-белый
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Размытие для уменьшения шума

    edges = cv2.Canny(blurred, 50, 150)  # Обнаружение границ
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        biggest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(biggest_contour)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cX, cY), 7, (0, 0, 255), -1)  # Рисуем кружок на центре
            if cX < CAMERA_WIDTH / 3:
                command = "L"  # Поворот влево
            elif cX > CAMERA_WIDTH * 2 / 3:
                command = "R"  # Поворот вправо
            else:
                command = "F"  # Плыть прямо
        else:
            command = "F"
    else:
        command = "F"  # Если нет объектов - плыть прямо

    return command, frame


while True:
    ret, frame = camera.read()
    if not ret:
        print("Не удалось получить кадр с камеры.")
        break

    command, frame = process_frame(frame)
    cv2.imshow("Camera feed", frame)  # Показ кадров с камеры (для отладки)

    try:
        ser.write(command.encode())  # Отправляем команду на Arduino
        print(f"Отправлена команда: {command}")
    except serial.SerialException as e:
        print(f"Ошибка отправки команды на Arduino: {e}")

    time.sleep(1)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # Выход по нажатию 'q'
        break

camera.release()
cv2.destroyAllWindows()
ser.close()

