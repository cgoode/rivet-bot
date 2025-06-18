from machine import Pin, PWM

MAX_MAGNITUDE = 2 # Max joystick values found expirementally
MOTOR_FREQUENCY = 5000 # hz


class Motor:
    def __init__(self, pwm_pin: Pin, forward_pin: Pin, reverse_pin: Pin, label="Unknown"):
        self.pwm_pin = pwm_pin
        self.pwm = PWM(pwm_pin)
        self.pwm.freq(MOTOR_FREQUENCY)
        self.forward_pin = forward_pin
        self.reverse_pin = reverse_pin
        self.label = label
        self.power = 0
        self.direction = "None"
    
    def set_direction(self, forward: bool):
        if forward:
            self.forward_pin.on()
            self.reverse_pin.off()
            self.direction = "Forward"
        else:
            self.reverse_pin.on()
            self.forward_pin.off()
            self.direction = "Reverse"

    def set_pwm(self, magnitude: float):
        magnitude = 1.0 if magnitude > 1.0 else magnitude
        magnitude = 0.0 if magnitude < 0.0 else magnitude
        self.pwm.duty_u16(int(magnitude*65535))
        self.power = magnitude
    
    def __repr__(self):
        return f"{self.label}, {self.direction}, {self.power}"


class MotorController:

    def __init__(self, left_motor: Motor, right_motor: Motor):
        self.left_motor = left_motor
        self.right_motor = right_motor

    def control(self, forward: float, turn: float):
        normal_forward = abs(forward)/MAX_MAGNITUDE
        normal_turn = abs(turn)/MAX_MAGNITUDE
        
        # If forward > 0 then engage both motors forward pins
        if forward > 0:
            self.left_motor.set_direction(True)
            self.right_motor.set_direction(True)
        elif forward < 0:
            self.left_motor.set_direction(False)
            self.right_motor.set_direction(False)
        
        # Set pwm based on the magnitude of forward/reverse
        left = normal_forward
        right = normal_forward

        # Reduce the left power if there is a left turn
        if turn < 0:
            left -= normal_turn
            if left < 0: left = 0
        if turn > 0:
            right -= normal_turn
            if right < 0: right = 0
        
        # If there is no forward/backward requested and there is turn
        # then try to turn in place
        if forward == 0 and turn != 0:
            left = normal_turn
            right = normal_turn
            if turn < 0: # turn left
                self.left_motor.set_direction(False)
                self.right_motor.set_direction(True)
            if turn > 0: # Turn right
                self.left_motor.set_direction(True)
                self.right_motor.set_direction(False)

        self.left_motor.set_pwm(left)
        self.right_motor.set_pwm(right)

        print(self.left_motor)
        print(self.right_motor)

