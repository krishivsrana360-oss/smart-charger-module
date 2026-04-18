import subprocess 
import RPi.GPIO as GPIO 
import time 
from RPLCD.i2c import CharLCD 
# GPIO Setup 
BUZZER_PIN = 17 
SERVO_PIN = 18 
KEYPAD_ROWS = [5, 6, 13, 19] # R1, R2, R3, R4 
KEYPAD_COLS = [12, 16, 20, 21] # C1, C2, C3, C4 
GPIO.setmode(GPIO.BCM) 
GPIO.setup(BUZZER_PIN, GPIO.OUT) 
GPIO.output(BUZZER_PIN, GPIO.LOW) 
# Servo Setup - Prevent Initial Movement 
GPIO.setup(SERVO_PIN, GPIO.OUT) 
servo = GPIO.PWM (SERVO_PIN, 50) # 50Hz PWM frequency 
servo.start(0)   
# LCD Setup 
lcd = CharLCD('PCF8574', 0x27, auto_linebreaks=True) 
# Corrected Keypad Layout 
KEYPAD = [ 
['1', '2', '3', 'A'], 
['4', '5', '6', 'B'], 
['7', '8', '9', 'C'], 
['*', '0', '#', 'D'] 
] 
# Setup GPIO for keypad 
for row in KEYPAD_ROWS: 
GPIO.setup(row, GPIO.OUT) 
GPIO.output(row, GPIO.HIGH) 
for col in KEYPAD_COLS: 
GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
# Function to get battery level 
def get_battery_status(): 
9  
Electronics & Communication Department, Faculty of Technology, DDU, Nadiad.  
 Electronics & Communication Department, Faculty of Technology, DDU, Nadiad.  10  
    try: 
        result = subprocess.run(["adb", "shell", "dumpsys", "battery"], stdout=subprocess.PIPE, 
text=True, check=True) 
 
        for line in result.stdout.splitlines(): 
            if "level:" in line: 
 
                return int(line.split(":")[1].strip()) 
 
    except subprocess.CalledProcessError: 
 
        return None 
    return None 
 
# Function to read keypad input 
 
def read_keypad(): 
 
    for i, row in enumerate (KEYPAD_ROWS): 
 
        GPIO.output(row, GPIO.LOW) 
        for j, col in enumerate (KEYPAD_COLS): 
 
            if GPIO.input(col) == GPIO.LOW: 
                time.sleep(0.2)  # Debounce 
 
                while GPIO.input(col) == GPIO.LOW: 
                    pass  # Wait for key release 
                GPIO.output(row, GPIO.HIGH) 
 
                return KEYPAD[i][j] 
        GPIO.output(row, GPIO.HIGH) 
    return None 
 
# Function to get cutoff value 
 
def get_cutoff_value(): 
 
    lcd.clear() 
    lcd.write_string("Press A for 1s") 
    print("Press 'A' key for 1 second to enter cutoff...") 
 
    while True: 
        key = read_keypad() 
        if key == 'A': 
            break 
 
    lcd.clear() 
    lcd.write_string("Enter cutoff:") 
print("Enter cutoff value:") 
cutoff_value = "" 
while True: 
key = read_keypad() 
if key: 
if key == 'D':  # 'D' to confirm 
break 
elif key.isdigit(): 
cutoff_value += key 
lcd.clear() 
lcd.write_string(f"Cutoff: {cutoff_value}") 
print(f"Current input: {cutoff_value}") 
return int(cutoff_value) 
# Function to move servo 
def rotate_servo(): 
print("Servo moving to 90°") 
servo.ChangeDutyCycle(7.5) 
time.sleep(1) 
print("Returning to 0°") 
servo.ChangeDutyCycle(0)  # Stop movement 
time.sleep(1) 
# Battery monitoring loop 
def monitor_battery(): 
global cutoff_value   
lcd.clear() 
lcd.write_string(f"Cutoff: {cutoff_value}%") 
print(f"Monitoring battery. Cutoff at {cutoff_value}%.") 
servo_triggered = False   
try: 
while True: 
key = read_keypad() 
if key == 'A':   
cutoff_value = get_cutoff_value() 
lcd.clear() 
lcd.write_string(f"New Cutoff: {cutoff_value}%") 
print(f"New cutoff: {cutoff_value}%") 
servo_triggered = False   
battery_level = get_battery_status() 
if battery_level is None: 
lcd.clear() 
lcd.write_string("ADB Error!") 
print("ADB Error: Could not get battery status.") 
GPIO.output(BUZZER_PIN, GPIO.LOW) 
else: 
lcd.clear() 
lcd.write_string(f"Battery: {battery_level}%") 
print(f"Battery Level: {battery_level}%") 
if battery_level >= cutoff_value and not servo_triggered: 
GPIO.output(BUZZER_PIN, GPIO.HIGH) 
print("Buzzer ON! Battery at cutoff.") 
rotate_servo() 
servo_triggered = True 
elif battery_level < cutoff_value: 
servo_triggered = False 
GPIO.output(BUZZER_PIN, GPIO.LOW) 
time.sleep(5) 
except KeyboardInterrupt: 
print("Exiting...") 
GPIO.cleanup() 
# Set cutoff before starting 
cutoff_value = get_cutoff_value() 
# Start monitoring 
monitor_battery()
