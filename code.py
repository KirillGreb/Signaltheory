import cv2
import serial
import time
import numpy as np

# ��������� ����������������� ����� (�������� � ���� ����� ����������)
SERIAL_PORT = "/dev/ttyACM0"  # ��� Arduino �� USB
SERIAL_BAUDRATE = 9600

# ��������� ������
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

try:
    ser = serial.Serial(SERIAL_PORT, SERIAL_BAUDRATE, timeout=1)
    print("���������� � Arduino")
except serial.SerialException as e:
    print(f"������ ����������� � Arduino: {e}")
    exit(1)

camera = cv2.VideoCapture(0)  # ������� ������ Raspberry Pi
camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)


def process_frame(frame):
    """
    ��������� �����: ����������� �������� � �������� �������.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # ������������ � �����-�����
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # �������� ��� ���������� ����

    edges = cv2.Canny(blurred, 50, 150)  # ����������� ������
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        biggest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(biggest_contour)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cX, cY), 7, (0, 0, 255), -1)  # ������ ������ �� ������
            if cX < CAMERA_WIDTH / 3:
                command = "L"  # ������� �����
            elif cX > CAMERA_WIDTH * 2 / 3:
                command = "R"  # ������� ������
            else:
                command = "F"  # ����� �����
        else:
            command = "F"
    else:
        command = "F"  # ���� ��� �������� - ����� �����

    return command, frame


while True:
    ret, frame = camera.read()
    if not ret:
        print("�� ������� �������� ���� � ������.")
        break

    command, frame = process_frame(frame)
    cv2.imshow("Camera feed", frame)  # ����� ������ � ������ (��� �������)

    try:
        ser.write(command.encode())  # ���������� ������� �� Arduino
        print(f"���������� �������: {command}")
    except serial.SerialException as e:
        print(f"������ �������� ������� �� Arduino: {e}")

    time.sleep(1)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):  # ����� �� ������� 'q'
        break

camera.release()
cv2.destroyAllWindows()
ser.close()

