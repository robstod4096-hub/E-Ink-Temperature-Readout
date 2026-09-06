import os
import sys
import time
import tomllib
from gpiozero import Button
from PIL import Image, ImageDraw, ImageFont
from bme280_sensor import read_sensor_data
from weather_api import get_weather_data

# Point Python to the 'lib' folder inside the cloned repo
sys.path.append(os.path.join(os.path.dirname(__file__), 'e-Paper/RaspberryPi_JetsonNano/python/lib'))
from waveshare_epd import epd2in13b_V4

# Initialize the display and clear it
print("Initializing display...")
epd = epd2in13b_V4.EPD()
epd.init()
epd.Clear()

# Prepare canvas for drawing
image_black = Image.new('1', (epd.height, epd.width), 255)
image_red = Image.new('1', (epd.height, epd.width), 255)
draw_black = ImageDraw.Draw(image_black)
draw_red = ImageDraw.Draw(image_red)
font = ImageFont.truetype("11S01BlackTuesday-6yYD.ttf", 40)

# Initialize button on pin 36 (GPIO 16)
button = Button(16)

# Open config file
with open("config.toml", "rb") as f:
    data = tomllib.load(f)

def draw_weather_icon(draw, condition, x, y):
        condition = condition.lower()
        if any(word in condition for word in ("rain", "drizzle", "shower")):
                draw.ellipse((x + 4, y, x + 25, y + 14), outline=0, fill=255)
                draw.rectangle((x + 4, y + 7, x + 25, y + 14), fill=255)
                for offset in (7, 15, 23):
                        draw.line((x + offset, y + 16, x + offset - 3, y + 23), fill=0, width=2)
        elif any(word in condition for word in ("snow", "sleet", "ice")):
                draw.ellipse((x + 4, y, x + 25, y + 14), outline=0, fill=255)
                draw.rectangle((x + 4, y + 7, x + 25, y + 14), fill=255)
                for offset in (7, 15, 23):
                        draw.text((x + offset, y + 13), "*", fill=0)
        elif any(word in condition for word in ("cloud", "overcast", "partly")):
                draw.ellipse((x + 2, y + 8, x + 18, y + 22), outline=0, fill=255)
                draw.ellipse((x + 10, y + 3, x + 28, y + 22), outline=0, fill=255)
                draw.rectangle((x + 2, y + 14, x + 28, y + 22), outline=0, fill=255)
        else:
                draw.ellipse((x + 7, y + 5, x + 25, y + 23), outline=0, fill=255)
                for dx, dy in ((16, 0), (16, 28), (3, 4), (29, 4), (3, 22), (29, 22)):
                        draw.line((x + 16, y + 14, x + dx, y + dy), fill=0, width=2)

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
        
                        # Draw data on canvas
                        draw_black.rectangle((0, 0, epd.height, epd.width), fill=255)
                        draw_black.rectangle((124, 0, 125, epd.width), fill=0) # Divider line

                        # Left Side: Temperature, Pressure, Humidity
                        if temperature >= 80:
                                draw_red.text((20, 10), f"{temperature:.0f} {symbol}", fill=0, font=font)
                        else:
                                draw_black.text((20, 10), f"{temperature:.0f} {symbol}", fill=0, font=font)
                        draw_black.text((5, 80), f"Humidity: {humidity:.2f} %", fill=0)
                        draw_black.text((5, 90), f"Pressure: {pressure:.2f} hPa", fill=0)
                        draw_red.text((5, 110), "Indoor Conditions", fill=0)

                        # Right Side: Outdoor Conditions
                        if weather_temp is not None:
                                draw_red.text((135, 10), f"{weather_temp:.0f} {symbol}", fill=0, font=font)
                        draw_black.text((135, 70), f"Cond: {weather_conditions}", fill=0)
                        draw_weather_icon(draw_black, weather_conditions, 215, 35)
                        
                        if weather_high is not None:
                                draw_black.text((135, 85), f"High: {weather_high:.0f} {symbol}", fill=0)
                        if weather_low is not None:
                                draw_black.text((135, 95), f"Low: {weather_low:.0f} {symbol}", fill=0)
                        draw_red.text((135, 110), "Outdoor Conditions", fill=0)

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
