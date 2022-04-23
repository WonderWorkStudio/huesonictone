from microbit import *
import math
import random

# load the calibration function from MicroBit
compass.calibrate()

# MIDI NOTE ON function. Send the value of MicroBit buttons as MIDI message.
def midiNoteOn(chan, n, vel):
    MIDI_NOTE_ON = 0x90
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return
    msg = bytes([MIDI_NOTE_ON | chan, n, vel])
    uart.write(msg)

# MIDI NOTE OFF function. Send the value of MicroBit buttons as MIDI message.
    MIDI_NOTE_OFF = 0x80
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return
    msg = bytes([MIDI_NOTE_OFF | chan, n, vel])
    uart.write(msg)

# MIDI Controle Change function
# Send the values of MicroBit accelerometers and compass as MIDI message.
def midiControlChange(chan, n, value):
    MIDI_CC = 0xB0
    if chan > 15:
        return
    if n > 127:
        return
    if value > 127:
        return
    msg = bytes([MIDI_CC | chan, n, value])
    uart.write(msg)


# UART protocol for sending MIDI messages
def Start():
    uart.init(baudrate=31250, bits=8, parity=None, stop=1, tx=pin0)

# Variable field 
lastA = False
lastB = False
BUTTON_A_NOTE = 0
BUTTON_B_NOTE = 0
last_tiltX = 0
last_vol_pot = 0
last_bearing = 0
gyro = 0

Start()

# Command loop
while True:
    
    # MicroBit button A
    a = button_a.is_pressed()
    if a is True and lastA is False:
        # Creating ramdom MIDI velocity (currently not used)
        BUTTON_A_NOTE = random.randint(1, 127)
        midiNoteOn(0, BUTTON_A_NOTE, 127)
    elif a is False and lastA is True:
        midiNoteOff(0, BUTTON_A_NOTE, 127)  # Send MIDI message

    # MicroBit button B
    b = button_b.is_pressed()  
    if b is True and lastB is False:
        midiNoteOff(0, BUTTON_B_NOTE, 127)  # Send MIDI message
    lastB = b

    # MicroBit accelerometer
    current_tiltX = accelerometer.get_x()
    if current_tiltX != last_tiltX:
        mod_x = math.floor(math.fabs((((current_tiltX + 1024) / 2048) * 127)))
        # convert the range to 0-127
        midiControlChange(0, 21, mod_x)  # Send MIDI message
        last_tilt = current_tiltX

    # Potentiometer
    knob = pin2.read_analog()  # load the potentiometer
    calibrator = math.floor(knob / 1024 * 300)  # convert the range to 0-300

    # MicroBit compass
    current_bearing = compass.heading()  # load compass direction
    if current_bearing != last_bearing:
        # make only 90 degrees active, and ignore the other values
        if current_bearing < calibrator or current_bearing > calibrator + 89:
            current_bearing = last_bearing
        # convert the 90 degree range to 0-127 for MIDI message 
        gyro = math.floor(math.fabs((current_bearing - calibrator) / 90 * 127))
        midiControlChange(0, 22, gyro)  # Send MIDI message
        current_bearing = last_bearing

    sleep(100)
