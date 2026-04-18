import subprocess
import RPi.GPIO as GPIO
import time
from RPLCD.i2c import CharLCD

# ─────────────────────────────────────────
# GPIO Pin Configuration
# ─────────────────────────────────────────
BUZZER_PIN = 17
SERVO_PIN = 18
KEYPAD_ROWS = [5, 6, 13, 19]   # R1, R2, R3, R4
KEYPAD_COLS = [12, 16, 20, 21] # C1, C2, C3, C4

# ─────────────────────────────────────────
# GPIO Initialization
# ─────────────────────────────────────────
GPIO.setmode(GPIO.BCM)

# Buzzer setup
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(BUZZER_PIN, GPIO.LOW)

# Servo setup — start at 0 to prevent unwanted movement on boot
GPIO.setup(SERVO_PIN, GPIO.OUT)
servo = GPIO.PWM(SERVO_PIN, 50)  # 50Hz PWM frequency
servo.start(0)

# ─────────────────────────────────────────
# LCD Setup (I2C, address 0x27)
# ─────────────────────────────────────────
lcd = CharLCD('PCF8574', 0x27, auto_linebreaks=True)

# ─────────────────────────────────────────
# Keypad Layout (4x4)
# ─────────────────────────────────────────
KEYPAD = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# Configure keypad row pins as OUTPUT
for row in KEYPAD_ROWS:
    GPIO.setup(row, GPIO.OUT)
    GPIO.output(row, GPIO.HIGH)

# Configure keypad column pins as INPUT with pull-up
for col in KEYPAD_COLS:
    GPIO.setup(col, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# ─────────────────────────────────────────
# Function: Get Battery Level via ADB
# Returns battery % as int, or None on error
# ─────────────────────────────────────────
def get_battery_status():
    try:
        result = subprocess.run(
            ["adb", "shell", "dumpsys", "battery"],
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        for line in result.stdout.splitlines():
            if "level:" in line:
                return int(line.split(":")[1].strip())
    except subprocess.CalledProcessError:
        return None
    return None


# ─────────────────────────────────────────
# Function: Read Single Keypress from Keypad
# Returns the key character or None
# ─────────────────────────────────────────
def read_keypad():
    for i, row in enumerate(KEYPAD_ROWS):
        GPIO.output(row, GPIO.LOW)
        for j, col in enumerate(KEYPAD_COLS):
            if GPIO.input(col) == GPIO.LOW:
                time.sleep(0.2)  # Debounce delay
                while GPIO.input(col) == GPIO.LOW:
                    pass  # Wait for key release
                GPIO.output(row, GPIO.HIGH)
                return KEYPAD[i][j]
        GPIO.output(row, GPIO.HIGH)
    return None


# ─────────────────────────────────────────
# Function: Get Cutoff % from User via Keypad
# Press A to start input, digits to enter %, D to confirm
# ─────────────────────────────────────────
def get_cutoff_value():
    lcd.clear()
    lcd.write_string("Press A to set")
    print("Press 'A' key to enter cutoff percentage...")

    # Wait for A key to begin input
    while True:
        key = read_keypad()
        if key == 'A':
            break

    lcd.clear()
    lcd.write_string("Enter cutoff:")
    print("Enter cutoff value (press D to confirm):")

    cutoff_value = ""
    while True:
        key = read_keypad()
        if key:
            if key == 'D':  # D = confirm/enter
                break
            elif key.isdigit():
                cutoff_value += key
                lcd.clear()
                lcd.write_string(f"Cutoff: {cutoff_value}%")
                print(f"Current input: {cutoff_value}%")

    return int(cutoff_value)


# ─────────────────────────────────────────
# Function: Rotate Servo to Cut Off Charger
# Moves to 90° then returns to 0°
# ─────────────────────────────────────────
def rotate_servo():
    print("Servo moving to 90° — cutting power")
    servo.ChangeDutyCycle(7.5)  # 90 degrees
    time.sleep(1)
    print("Servo returning to 0°")
    servo.ChangeDutyCycle(0)    # Stop signal
    time.sleep(1)


# ─────────────────────────────────────────
# Main Function: Monitor Battery Continuously
# Triggers cutoff when battery reaches set %
# ─────────────────────────────────────────
def monitor_battery():
    global cutoff_value

    lcd.clear()
    lcd.write_string(f"Cutoff: {cutoff_value}%")
    print(f"Monitoring started. Cutoff set at {cutoff_value}%.")

    servo_triggered = False  # Prevents repeated triggering

    try:
        while True:
            # Allow user to update cutoff % during monitoring
            key = read_keypad()
            if key == 'A':
                cutoff_value = get_cutoff_value()
                lcd.clear()
                lcd.write_string(f"New Cutoff: {cutoff_value}%")
                print(f"Cutoff updated to: {cutoff_value}%")
                servo_triggered = False  # Reset trigger for new cutoff

            # Fetch current battery level
            battery_level = get_battery_status()

            if battery_level is None:
                # ADB communication failed
                lcd.clear()
                lcd.write_string("ADB Error!")
                print("ADB Error: Could not read battery level.")
                GPIO.output(BUZZER_PIN, GPIO.LOW)

            else:
                # Display current battery level on LCD
                lcd.clear()
                lcd.write_string(f"Battery: {battery_level}%")
                print(f"Battery Level: {battery_level}%")

                if battery_level >= cutoff_value and not servo_triggered:
                    # Cutoff reached — alert user and stop charging
                    GPIO.output(BUZZER_PIN, GPIO.HIGH)
                    print("Cutoff reached! Activating servo...")
                    rotate_servo()
                    servo_triggered = True

                elif battery_level < cutoff_value:
                    # Battery below cutoff — reset state
                    servo_triggered = False
                    GPIO.output(BUZZER_PIN, GPIO.LOW)

            time.sleep(5)  # Check every 5 seconds

    except KeyboardInterrupt:
        print("Program stopped by user.")
        GPIO.cleanup()


# ─────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────
cutoff_value = get_cutoff_value()  # Get initial cutoff from user
monitor_battery()                  # Start monitoring loop
