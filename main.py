from flask import Flask, render_template, request
import requests

WEATHER_API_KEY = "fd0e6bd8dfbb84569e65f891339f8679"  # Replace with your actual API key
WEATHER_API_URL = 'http://api.openweathermap.org/data/2.5/weather'
FORECAST_API_URL = 'http://api.openweathermap.org/data/2.5/forecast'  # New endpoint
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
        return response.json()
    except requests.exceptions.HTTPError as err:
        return {"error": str(err)}
    except Exception as e:
        return {"error": "An error occurred: " + str(e)}


@app.route('/', methods=['GET', 'POST'])
def home():
    weather_data = None
    forecast_data = None
    error_message = None
    if request.method == 'POST':
        city = request.form.get('city')
        unit = request.form.get('unit')
        weather_data = get_weather(city, unit)
        forecast_data = get_forecast(city, unit)

        if "error" in weather_data:
            error_message = weather_data["error"]

    return render_template('index.html',
                           weather_data=weather_data,
                           forecast_data=forecast_data,
                           error_message=error_message)


if __name__ == '__main__':
    app.run(debug=True)