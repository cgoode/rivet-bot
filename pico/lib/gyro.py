from machine import Pin, I2C
from imu import MPU6050


class Gyro:

    def __init__(self, sda: Pin, scl: Pin):
        i2c = I2C(1, sda=sda, scl=scl, freq=400000)
        self.imu = MPU6050(i2c)

    def get_orientation(self):
        return self.imu.gyro
