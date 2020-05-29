from datetime import datetime
import RPi.GPIO as GPIO

def setUp():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)

def set_speed(speed):
    print("%s - Current Speed: %d" % (datetime.now(), speed))
    if speed > 0:
        GPIO.output(8, GPIO.HIGH)
    else:
        GPIO.output(8, GPIO.LOW)