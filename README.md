## Overview
This project reads local room temperature data and pulls weather conditions for a configured location, then renders the information on a low-power e-paper display. It also displays a graph of the last 24 hours on a web interface. It is designed for continuous monitoring in a home, office, or workshop.

## Features
- Displays indoor temperature
- Displays outdoor temperature and weather information
- Uses a low-power E-Ink display for easy readability
- Runs on Raspberry Pi Zero 2 W
- Configurable via `config.toml`
- Supports SPI/I2C-related peripherals used by the display and sensors
- Logs temperature data and displays it via a web interface

## Hardware Requirements
- Raspberry Pi (or compatible single-board computer)
- E-Ink display module
- Temperature sensor
- Wiring for SPI/I2C as required by your display and sensor setup
- Stable power supply

## Setup and Install
1. Clone the E-Ink display drivers from the Waveshare repository:
   https://github.com/waveshareteam/e-Paper/tree/master/RaspberryPi_JetsonNano/python
2. Copy or configure the correct display driver in `main.py` for your specific E-Ink model.
3. Install dependencies required by `main.py`, `app.py`, and the I2C/SPI hardware stack.
4. Ensure Python packages for the display and sensors are installed.
5. Update `config.toml`

## Configuration
Edit `config.toml` to change the following:
- location
- refresh rate
- temperature units (`C` or `F`)

## Running the Project
Set up main.py and app.py as systemd services so they can run simultaneously.