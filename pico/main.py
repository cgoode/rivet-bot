from machine import Pin
import network
from lib.connect import connect_to_wifi, open_socket
from lib.web_server import handle_client
from lib.motor_control import Motor, MotorController
# from lib.gyro import Gyro
from lib.imu import MPUException



import uasyncio as asyncio


ACCESS_POINT = True
led_pin = Pin("LED", Pin.OUT)


async def main():
    if ACCESS_POINT:
        ssid = 'Rivet-Bot'
        password = '123456789'

        wlan = network.WLAN(network.AP_IF)
        wlan.config(essid=ssid, password=password)
        wlan.active(True)
    else:
        ssid = "wife-fi"
        password = "fragola303"
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        wlan.connect(ssid, password)
    while not wlan.isconnected():
        print("Waiting to connect...")
        led_pin.toggle()
        await asyncio.sleep(0.5)
    print("Connected to Wi-Fi:", wlan.ifconfig()[0])
    led_pin.on()

    left_motor = Motor(Pin("GPIO9", Pin.OUT), Pin("GPIO11", Pin.OUT), Pin("GPIO10", Pin.OUT), "Left")
    right_motor = Motor(Pin("GPIO12", Pin.OUT), Pin("GPIO14", Pin.OUT), Pin("GPIO13", Pin.OUT), "Right")
    motor_controller = MotorController(left_motor=left_motor, right_motor=right_motor)
    # try:
    #     gyro = Gyro(sda=Pin("GPIO10"), scl=Pin("GPIO11"))
    # except:
    #     gyro = None
    #     print("Unable to connect to gyro!")

    async def client_wrapper(reader, writer):
        await handle_client(reader, writer, motor_controller)
    
    await asyncio.start_server(client_wrapper, "0.0.0.0", 80)
    
    print("Serving on ws://" + wlan.ifconfig()[0])

    # Keep the loop alive
    while True:
        await asyncio.sleep(1)
        # orientation = gyro.get_orientation()
        # print(f"x: {orientation.x}, y: {orientation.y}, z: {orientation.z}")


asyncio.run(main())
