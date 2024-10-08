from flask import Flask, render_template, request
import requests
from datetime import datetime
from collections import defaultdict

WEATHER_API_KEY = "fd0e6bd8dfbb84569e65f891339f8679"  # Replace with your actual API key
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_API_URL = 'http://api.openweathermap.org/data/2.5/forecast'
app = Flask(__name__)


def get_weather(city, unit):
    params = {'q': city, 'appid': WEATHER_API_KEY, 'units': unit}
    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        return {"error": str(err)}
    except Exception as e:
        return {"error": "An error occurred: " + str(e)}


def get_forecast(city, unit):
    params = {'q': city, 'appid': WEATHER_API_KEY, 'units': unit}
    try:
        response = requests.get(FORECAST_API_URL, params=params)
        response.raise_for_status()
        forecast_data = response.json()

        # Group forecast entries by day and calculate daily averages
        daily_data = defaultdict(lambda: {
            'temps': [],
            'humidities': [],
            'weather_desc': []
        })

        for entry in forecast_data['list']:
            dt = datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S")
            day_of_week = dt.strftime('%A')
            temp = entry['main']['temp']
            humidity = entry['main']['humidity']
            weather_desc = entry['weather'][0]['description']

            daily_data[day_of_week]['temps'].append(temp)
            daily_data[day_of_week]['humidities'].append(humidity)
            daily_data[day_of_week]['weather_desc'].append(weather_desc)

        # Compute averages
        averaged_forecast = []
        for day, data in daily_data.items():
            avg_temp = round(sum(data['temps']) /
                             len(data['temps']))  # Rounded average temperature
            avg_humidity = sum(data['humidities']) / len(data['humidities'])
            weather_desc = max(
                set(data['weather_desc']),
                key=data['weather_desc'].count)  # Most common description
            averaged_forecast.append({
                'day_of_week': day,
                'avg_temp': avg_temp,
                'avg_humidity': avg_humidity,
                'weather_desc': weather_desc
            })

        return forecast_data[
            'city'], averaged_forecast  # Returning city dict and averaged forecast
    except requests.exceptions.HTTPError as err:
        return {"error": str(err)}
    except Exception as e:
        return {"error": "An error occurred: " + str(e)}


@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    forecast_data = None
    city_info = None
    error_message = None
    if request.method == 'POST':
        city = request.form.get('city')
        unit = request.form.get('unit')
        weather_data = get_weather(city, unit)
        city_info, forecast_data = get_forecast(city, unit)

        if "error" in weather_data:
            error_message = weather_data["error"]

    return render_template(
        'index.html',
        weather_data=weather_data,
        forecast_data=forecast_data,
        city_info=city_info,  # Pass city information
        error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)
