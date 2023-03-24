# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 14:05:43 2023

@author: Mayk Al-Ghrawi
"""

import requests
import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import ttk
from PIL import Image, ImageTk
from opencage.geocoder import OpenCageGeocode
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

api_key = '6ae1bdf87608c0e2922ec5daf684633c'
opencage_api_key = '6a2db0af0a9744128a6f4a9e1ce97ff7'
geocoder = OpenCageGeocode(opencage_api_key)

canvas = None  # Add global variable for canvas

def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    weather_data = response.json()
    forecasts = {}
    target_hour = 12  # Target hour for forecasts, e.g., 12 for noon

    for forecast in weather_data['list']:
        date_time = forecast['dt_txt']
        date, time = date_time.split()  # Extract date and time from date_time string
        hour = int(time.split(':')[0])

        # Check if the date is not in the forecasts and the hour is close to the target hour
        if date not in forecasts and abs(hour - target_hour) <= 1:
            temperature = forecast['main']['temp']
            humidity = forecast['main']['humidity']
            wind_speed = forecast['wind']['speed']
            weather_icon = forecast['weather'][0]['icon']
            forecasts[date] = {'temperature': temperature, 'humidity': humidity, 'wind_speed': wind_speed, 'weather_icon': weather_icon}
        if len(forecasts) == 5:
            break

    return forecasts

def get_city_suggestions(query):
    results = geocoder.geocode(query, language='en', limit=5, no_annotations=1)
    suggestions = [result['formatted'] for result in results]
    return suggestions

def update_weather():
    city = city_combobox.get()
    weather_data = get_weather_data(city)
    temperatures = [forecast_data['temperature'] for forecast_data in weather_data.values()]  # Get temperatures for the 5 days
    temperature_label.config(text=f'Temperature: {temperatures[0]}°C')
    humidity_label.config(text=f'Humidity: {list(weather_data.values())[0]["humidity"]}%')
    wind_speed_label.config(text=f'Wind Speed: {list(weather_data.values())[0]["wind_speed"]} m/s')
    update_weather_icon(list(weather_data.values())[0]["weather_icon"])

    for i, (date, forecast) in enumerate(weather_data.items()):
        day_label = day_labels[i]
        day_label.config(text=f'{date}: {forecast["temperature"]}°C, {forecast["humidity"]}% humidity, {forecast["wind_speed"]} m/s wind')

    # Plot temperature forecast
    fig, ax = plt.subplots()
    ax.plot(range(1, 6), temperatures)
    ax.set_xlabel('Day')
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Temperature Forecast')

    global canvas  # Add global variable for canvas
    if canvas is not None:  # Check if canvas already exists
        canvas.get_tk_widget().destroy()  # Destroy old canvas

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()

def update_weather_icon(icon_code):
    icon_url = f'http://openweathermap.org/img/wn/{icon_code}@2x.png'
    icon_image = Image.open(requests.get(icon_url, stream=True).raw)
    icon_image = icon_image.resize((64, 64), Image.ANTIALIAS)
    icon_photo = ImageTk.PhotoImage(icon_image)
    weather_icon_label.config(image=icon_photo)
    weather_icon_label.image = icon_photo

def on_combobox_change(event):
    update_weather()

def update_city_suggestions():
    query = city_combobox.get()
    suggestions = get_city_suggestions(query)
    city_combobox['values'] = suggestions

root = tk.Tk()

city_label = tk.Label(root, text='City:')
city_label.pack()

city_combobox = ttk.Combobox(root, values=[], postcommand=update_city_suggestions)
city_combobox.bind("<<ComboboxSelected>>", on_combobox_change)
city_combobox.pack()

update_button = tk.Button(root, text='Update', command=update_weather)
update_button.pack()

temperature_label = tk.Label(root, text='')
temperature_label.pack()

humidity_label = tk.Label(root, text='')
humidity_label.pack()

wind_speed_label = tk.Label(root, text='')
wind_speed_label.pack()

weather_icon_label = tk.Label(root, image=None)
weather_icon_label.pack()

forecast_label = tk.Label(root, text='5-Day Forecast:', font=('Arial', 14))
forecast_label.pack()

day_labels = []
for i in range(5):
    day_label = tk.Label(root, text='', font=('Arial', 12))
    day_label.pack()
    day_labels.append(day_label)

root.geometry('640x640')
root.mainloop()