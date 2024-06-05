import time
import RPi.GPIO as GPIO

# Pin definitions
DATA_PIN = 22  # GPIO22 (Pin 15)
LATCH_PIN = 27  # GPIO27 (Pin 13)
CLOCK_PIN = 17  # GPIO17 (Pin 11)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(DATA_PIN, GPIO.OUT)
GPIO.setup(LATCH_PIN, GPIO.OUT)
GPIO.setup(CLOCK_PIN, GPIO.OUT)

def get_memory_info():
    with open('/proc/meminfo', 'r') as file:
        meminfo = file.readlines()

    meminfo_dict = {}
    for line in meminfo:
        key, value = line.split(':')
        meminfo_dict[key.strip()] = int(value.split()[0]) * 1024  # Convert kB to bytes

    total_memory = meminfo_dict.get('MemTotal', 0)
    free_memory = meminfo_dict.get('MemFree', 0)
    buffers = meminfo_dict.get('Buffers', 0)
    cached = meminfo_dict.get('Cached', 0)
    
    used_memory = total_memory - (free_memory + buffers + cached)
    memory_percentage = (used_memory / total_memory) * 100

    return total_memory, used_memory, memory_percentage

def round_to_nearest_multiple_of_10(value):
    # Ensure the value is between 0 and 100
    value = max(0, min(100, value))
    
    # Round to the nearest multiple of 10
    rounded_value = round(value / 10) * 10
    
    return rounded_value

def print_memory_usage():
    while True:
        total_memory, used_memory, memory_percentage = get_memory_info()
        rounded_memory_percentage = round_to_nearest_multiple_of_10(memory_percentage)

        print(f"Total Memory: {total_memory / (1024 ** 2):.2f} MB")
        print(f"Used Memory: {used_memory / (1024 ** 2):.2f} MB")
        print(f"Memory Usage: {memory_percentage:.2f}%")
        print(f"Memory Usage: {memory_percentage:.2f}% (Rounded to {rounded_memory_percentage}%)")
        
        # Update the bar graph with the rounded memory percentage
        update_led_bar_graph(rounded_memory_percentage)

        time.sleep(2)
def shift_out(data_pin, clock_pin, value):
    for i in range(8):
        GPIO.output(clock_pin, GPIO.LOW)
        GPIO.output(data_pin, (value >> (7 - i)) & 1)
        GPIO.output(clock_pin, GPIO.HIGH)

def update_led_bar_graph(completeness):
    # Map completeness to the number of segments to light up
    num_segments = int(completeness / 10)
    led_value = (1 << num_segments) - 1 if num_segments > 0 else 0

    # Clear previous values
    GPIO.output(LATCH_PIN, GPIO.LOW)
    shift_out(DATA_PIN, CLOCK_PIN, 0)
    GPIO.output(LATCH_PIN, GPIO.HIGH)
    
    # Shift out the led_value
    GPIO.output(LATCH_PIN, GPIO.LOW)
    shift_out(DATA_PIN, CLOCK_PIN, led_value)
    GPIO.output(LATCH_PIN, GPIO.HIGH)

if __name__ == "__main__":
    print_memory_usage()
