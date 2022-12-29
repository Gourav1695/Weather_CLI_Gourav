import sys
import json
import argparse
from logging import exception
from configparser import ConfigParser
from urllib import error,parse,request

import style

BASE_WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

THUNDERSTORM = range(200, 300)
RAIN = range(500, 600)
DRIZZLE = range(300, 400)
SNOW = range(600, 700)
ATMOSPHERE = range(700, 800)
CLEAR = range(800, 801)
CLOUDY = range(801, 900)


def _get_api_key():
    
    """
    Function to get the API 
    """

    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]

def read_user_cli_args():

    """
    Function to handle user CLI interactions
    """

    parser = argparse.ArgumentParser(
        description="Gets weather information for a city"
    )

    parser.add_argument(
        "city", nargs="+", type=str, help="Enter the city name"
    )

    parser.add_argument(
        "-i",
        "--imperial",
        action="store_true",
        help="Display the temperature in imperial units"
    )
    return parser.parse_args()

def build_weather_query(city_input, imperial=False):

    """
    Function to build the URL for an API request 
    to OpenWeather's weather API
    """
    api_key = _get_api_key()
    city_name = " ".join(city_input)
    url_encoded_city_name = parse.quote_plus(city_name)
    units = "imperial" if imperial else "metric"
    url = (
        f"{BASE_WEATHER_API_URL}?q={url_encoded_city_name}"
        f"&units={units}&APPID={api_key}"
    )
    return url

def get_weather_data(query_url):
    """
    Function to get the weather data using API call
    """

    try:
        response = request.urlopen(query_url)
    except error.HTTPError:
        sys.exit("Sorry cannot find the data for this city")

    data = response.read()

    try:
        return json.loads(data)
    except json.JSONDecodeError:
        sys.exit("Could not read the server response")

def display_weather_info(weather_data, imperial=False):
    """
    Function to print the received data in a well-formatted way
    """

    city = weather_data["name"]
    weather_id = weather_data["weather"][0]["id"]
    weather_description = weather_data["weather"][0]["description"]
    temperature = weather_data["main"]["temp"]
    humidity = weather_data["main"]["humidity"]

    style.change_color(style.REVERSE)
    print(f"{city:^{style.PADDING}}", end="")
    style.change_color(style.RESET)

    weather_symbol, color = _select_weather_display_params(weather_id)

    style.change_color(color)
    print(f"\t{weather_symbol}", end=" ")
    print(
        f"{weather_description.capitalize():^{style.PADDING}}",
        end=" ",
    )
    style.change_color(style.RESET)

    print(f"({temperature}°{'F' if imperial else 'C'})",end="\t")
    print(f"({humidity}% Humidity)")

def _select_weather_display_params(weather_id):
    if weather_id in THUNDERSTORM:
        display_params = ("⛈", style.RED)
    elif weather_id in DRIZZLE:
        display_params = ("💧", style.CYAN)
    elif weather_id in RAIN:
        display_params = ("💦", style.BLUE)
    elif weather_id in SNOW:
        display_params = ("⛄️", style.WHITE)
    elif weather_id in ATMOSPHERE:
        display_params = ("🌀", style.BLUE)
    elif weather_id in CLEAR:
        display_params = ("🔆", style.YELLOW)
    elif weather_id in CLOUDY:
        display_params = ("💨", style.WHITE)
    else:  # In case the API adds new weather codes
        display_params = ("🌈", style.RESET)
    return display_params

if __name__ == "__main__":
    user_args = read_user_cli_args()
    query_url = build_weather_query(user_args.city,user_args.imperial)
    weather_data = get_weather_data(query_url)
    display_weather_info(weather_data,user_args.imperial)