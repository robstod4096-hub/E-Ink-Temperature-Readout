import os
import sys
import time
import tomllib
import sqlite3
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from bme280_sensor import read_sensor_data
from weather_api import get_weather_data

# Open config file
with open("config.toml", "rb") as f:
    data = tomllib.load(f)

# Point Python to the 'lib' folder inside the cloned repo
sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))
from waveshare_epd import epd2in13b_V4

# Initialize the display
print("Initializing display...")
epd = epd2in13b_V4.EPD()

# Prepare canvas for drawing
image_black = Image.new('1', (epd.height, epd.width), 255)
image_red = Image.new('1', (epd.height, epd.width), 255)
draw_black = ImageDraw.Draw(image_black)
draw_red = ImageDraw.Draw(image_red)
font = ImageFont.truetype("fonts/11S01BlackTuesday-6yYD.ttf", 40)

# Initialize button on pin 36 (GPIO 16)
button = Button(16)

def update_display():
                        print("\nUpdating display...")

                        # Wake up display
                        epd.init()
                        epd.Clear()
        
                        # Retrieve atmospheric data from sensor
                        if data["general"]["units"] == "fahrenheit":
                                temperature = read_sensor_data()['temperature_fahrenheit']
                                symbol = "°F"
                        elif data["general"]["units"] == "celsius":
                                temperature = read_sensor_data()['temperature_celsius']
                                symbol = "°C"
                        pressure = read_sensor_data()['pressure']
                        humidity = read_sensor_data()['humidity']
                
                        weather_data = get_weather_data()
                        weather_temp = weather_data.get("temperature")
                        weather_high = weather_data.get("high")
                        weather_low = weather_data.get("low")
                        weather_conditions = weather_data.get("conditions", "Unavailable")

                        # Log data to database
                        log_to_db(temperature, humidity, weather_temp)

                        # Draw data on canvas
                        draw_black.rectangle((0, 0, epd.height, epd.width), fill=255) # Blank black canvas
                        draw_red.rectangle((0, 0, epd.height, epd.width), fill=255) # Blank red canvas
                        draw_black.rectangle((124, 0, 125, 105), fill=0) # Middle Divider line
                        draw_black.rectangle((0, 85, epd.height, 86), fill=0) # Top bar
                        draw_black.rectangle((0, 105, epd.height, 106), fill=0) # Bottom bar

                        # Left Side: Temperature, Pressure, Humidity
                        if temperature >= 80:
                                draw_red.text((20, 5), f"{temperature:.0f} {symbol}", fill=0, font=font)
                        else:
                                draw_black.text((20, 5), f"{temperature:.0f} {symbol}", fill=0, font=font)
                        draw_black.text((5, 60), f"Humidity: {humidity:.2f} %", fill=0)
                        draw_black.text((5, 70), f"Pressure: {pressure:.2f} hPa", fill=0)
                        draw_red.text((5, 90), "Indoors", fill=0)

                        # Right Side: Outdoor Conditions
                        if weather_temp is not None:
                                if weather_temp >= 80:
                                        draw_red.text((135, 5), f"{weather_temp:.0f} {symbol}", fill=0, font=font)
                                else:
                                        draw_black.text((135, 5), f"{weather_temp:.0f} {symbol}", fill=0, font=font)
                        else:
                                draw_black.text((135, 5), "N/A", fill=0, font=font)
                        if weather_conditions is not None:
                                draw_black.text((135, 60), f"{weather_conditions}", fill=0)
                        else:
                                draw_black.text((135, 60), "Unavailable", fill=0)
                        if weather_high is not None:
                                if weather_high >= 80:
                                        draw_red.text((135, 70), f"H: {weather_high:.0f} {symbol}", fill=0)
                                else:
                                        draw_black.text((135, 70), f"H: {weather_high:.0f} {symbol}", fill=0)
                        else:
                                draw_black.text((135, 70), "H: N/A", fill=0)
                        if weather_low is not None:
                                if weather_low >= 80:
                                        draw_red.text((185, 70), f"L: {weather_low:.0f} {symbol}", fill=0)
                                else:
                                        draw_black.text((185, 70), f"L: {weather_low:.0f} {symbol}", fill=0)
                        else:
                                draw_black.text((185, 70), "L: N/A", fill=0)
                        draw_red.text((135, 90), "Outdoors", fill=0)

                        # Button Prompt
                        draw_black.text((5, 110), "Displaying old data.  Hold button to update.", fill=0)

                        # Rotate canvas from portrait to landscape
                        image_black_rotated = image_black.rotate(90, expand=True)
                        image_red_rotated = image_red.rotate(90, expand=True)
        
                        # Push canvas to display
                        epd.display(
                                epd.getbuffer(image_black_rotated), 
                                epd.getbuffer(image_red_rotated),
                                )
        
                        # Put screen to sleep and wait to run again
                        epd.sleep()

def log_to_db(indoor_temp, humidity, outdoor_temp=None):
        conn = sqlite3.connect('climate_data.db')
        cursor = conn.cursor()
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS readings (
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL,
                humidity REAL,
                outdoor_temp REAL
                )
        ''')

        cursor.execute(
                "INSERT INTO readings (temperature, humidity, outdoor_temp) VALUES (?, ?, ?)",
                (indoor_temp, humidity, outdoor_temp)
                )
        conn.commit()
        conn.close()

while True:
        update_display()
        time_remaining = data["general"]["update_interval"]
        for i in range(data["general"]["update_interval"]):
                if button.is_pressed:
                        update_display()
                        time_remaining = data["general"]["update_interval"] + 1
                else:
                        time.sleep(1)
                time_remaining -= 1
                print(f"Time remaining until next update: {time_remaining} seconds. Press button to update now.", end="\r")
