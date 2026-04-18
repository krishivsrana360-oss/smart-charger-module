# smart-charger-module
Raspberry Pi based smart charger that auto-stops charging at user-set battery % using ADB protocol, servo motor cutoff, and buzzer alerts
# Smart Charger Module

A Raspberry Pi based smart charging system that automatically stops charging 
when the battery reaches a user-defined percentage. Built
project at Dharmsinh Desai University.

## What it does

- User sets a charging cutoff % using a 4x4 keypad (e.g. 80%)
- Raspberry Pi monitors phone battery level in real time via ADB protocol
- When battery hits the set %, a servo motor physically turns off the switch
- If phone is plugged in but charger is OFF, a buzzer alert notifies the user
- LCD display shows live battery % and system status

## Hardware Used

- Raspberry Pi 4
- 4x4 Matrix Keypad
- 16x2 LCD Display (I2C)
- Servo Motor (SG90)
- Op-Amp as Voltage Comparator
- Buzzer
- Custom PCB wiring

## Tech Stack

- Python (RPi.GPIO, subprocess, RPLCD)
- ADB (Android Debug Bridge) protocol
- I2C communication
- PWM servo control

## How to Run

1. Connect all hardware as per circuit diagram
2. Enable I2C on Raspberry Pi
3. Connect phone via USB and enable ADB
4. Run the main script:

   python3 smart_charger.py

5. Enter cutoff % on keypad when prompted
6. System starts monitoring automatically

## Project Demo

*Photos of working setup below*
## Project Photos

### Circuit Diagram
![Circuit Diagram](./Screenshot%202026-04-18%20230508.png)

### Output
![Output](./Screenshot%202026-04-18%20230523.png)

### Raspberry Pi Pinout
![Raspberry Pi Pinout](./Screenshot%202026-04-18%20230541.png)

### Keypad Pinout
![Keypad Pinout](./Screenshot%202026-04-18%20230557.png)

### Results Graph
![Results Graph](./Screenshot%202026-04-18%20230606.png)

### Full Setup
![Full Setup](./Screenshot%202026-04-18%20230653.png)

## Limitations

- Servo motor has mechanical wear over time
- Requires stable power supply
- Currently supports one device at a time

## Future Improvements

- Multi-device support
- Thermal overheating detection
- Wireless monitoring via mobile app

## Made By

Krishiv S Rana
