import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

st.title("🌦️ Weather Dashboard")

city = st.text_input("Enter city name")

if city.strip() == "":
    st.info("👆 Please enter a city name")
    st.stop()

geo_url = (
    f"https://api.openweathermap.org/geo/1.0/direct"
    f"?q={city}&limit=1&appid={API_KEY}"
)

geo_resp = requests.get(geo_url).json()

if not isinstance(geo_resp, list) or len(geo_resp) == 0:
    st.error("City not found or API error")
    st.write("API response:", geo_resp)
    st.stop()

lat = geo_resp[0]["lat"]
lon = geo_resp[0]["lon"]

weather_url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
)

weather = requests.get(weather_url).json()

if weather.get("cod") != 200:
    st.error("⚠️ Weather API error")
    st.write(weather)
    st.stop()

st.subheader("🌤 Current Weather")
st.write(f"🌡 Temperature: {weather['main']['temp']} °C")
st.write(f"💧 Humidity: {weather['main']['humidity']}%")
st.write(f"☁ Description: {weather['weather'][0]['description']}")

forecast_url = (
    f"https://api.openweathermap.org/data/2.5/forecast"
    f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
)

forecast = requests.get(forecast_url).json()

if forecast.get("cod") != "200":
    st.error("⚠️ Forecast API error")
    st.write(forecast)
    st.stop()

df = pd.DataFrame(forecast["list"])
df["date"] = pd.to_datetime(df["dt_txt"])
df["temp"] = df["main"].apply(lambda x: x["temp"])

st.subheader("📈 Temperature Forecast")

fig = px.line(
    df,
    x="date",
    y="temp",
    title="Temperature Forecast (Next 5 Days)"
)

st.plotly_chart(fig)