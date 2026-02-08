import streamlit as st
import requests, os
from dotenv import load_dotenv
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression

if "current" not in st.session_state:
    st.session_state.current = None
if "forecast" not in st.session_state:
    st.session_state.forecast = None

# =============================
# LOAD API KEY
# =============================
load_dotenv()
API_KEY = os.getenv("API_KEY")

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="🌦️ Smart Weather ML Dashboard",
    layout="wide"
)

st.title("🌦️ Smart Weather Dashboard with ML Prediction")
st.caption("Overview • Hourly • Monthly • Trends • Map • Alerts • ML • Dynamic UI")

# =============================
# FUNCTION: Dynamic Background + Rain
# =============================
def apply_weather_ui(weather, current_time, sunset_time):
    is_night = current_time > sunset_time

    # Background
    if is_night:
        bg = "linear-gradient(to right, #0f2027, #203a43, #2c5364)"  # Night
    elif weather == "Clear":
        bg = "linear-gradient(to right, #fceabb, #f8b500)"
    elif weather == "Clouds":
        bg = "linear-gradient(to right, #bdc3c7, #2c3e50)"
    elif weather in ["Rain", "Drizzle"]:
        bg = "linear-gradient(to right, #4b79a1, #283e51)"
    elif weather == "Thunderstorm":
        bg = "linear-gradient(to right, #232526, #414345)"
    else:
        bg = "linear-gradient(to right, #83a4d4, #b6fbff)"

    # Rain animation
    rain_html = ""
    if weather in ["Rain", "Drizzle", "Thunderstorm"]:
        rain_html = """
        <div class="rain">
            """ + "".join([f"<div class='drop'></div>" for _ in range(80)]) + """
        </div>
        """

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {bg};
            transition: background 1s ease;
        }}
        .rain {{
            position: fixed;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            pointer-events: none;
            z-index: 0;
        }}
        .drop {{
            position: absolute;
            bottom: 100%;
            width: 2px;
            height: 15px;
            background: rgba(255,255,255,0.6);
            animation: fall 0.6s linear infinite;
        }}
        @keyframes fall {{
            to {{
                transform: translateY(110vh);
            }}
        }}
        </style>
        {rain_html}
        """,
        unsafe_allow_html=True
    )

# =============================
# SIDEBAR
# =============================
st.sidebar.header("⚙️ Controls")
city = st.sidebar.text_input("🌍 City", "Karachi")
theme = st.sidebar.radio("🌙 Theme", ["Light", "Dark"])
temp_alert = st.sidebar.slider("🌡️ Temperature Alert (°C)", -10, 50, 35)

# =============================
# THEME
# =============================
chart_theme = "plotly"
if theme == "Dark":
    st.markdown("""
        <style>
        .stApp { background-color: #0E1117; color: white; }
        </style>
    """, unsafe_allow_html=True)
    chart_theme = "plotly_dark"

# =============================
# API URLs
# =============================
current_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"

# =============================
# GET WEATHER
# =============================
if st.sidebar.button("🚀 Get Weather"):
    with st.spinner("Fetching weather data..."):
        st.session_state.current = requests.get(current_url).json()
        st.session_state.forecast = requests.get(forecast_url).json()

current = st.session_state.current
forecast = st.session_state.forecast

if current is None or forecast is None:
    st.info("Click 'Get Weather' to load data")
    st.stop()

    # =============================
    # Dynamic Background & Rain
    # =============================
weather_condition = current["weather"][0]["main"]
current_time = current["dt"]
sunset_time = current["sys"]["sunset"]
apply_weather_ui(weather_condition, current_time, sunset_time)

    # =============================
    # WEATHER OVERVIEW CARDS
    # =============================
st.subheader("🌤 Weather Overview")
temp = current["main"]["temp"]

if temp >= temp_alert:
    st.error(f"🔥 HIGH TEMP ALERT: {temp} °C")
elif temp <= 5:
    st.warning(f"❄️ LOW TEMP ALERT: {temp} °C")
else:
    st.success(f"✅ Temperature Normal: {temp} °C")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("🌡 Temp", f"{temp} °C")
c2.metric("🤔 Feels Like", f"{current['main']['feels_like']} °C")
c3.metric("💧 Humidity", f"{current['main']['humidity']} %")
c4.metric("🌬 Wind", f"{current['wind']['speed']} m/s")
c5.metric("📊 Pressure", f"{current['main']['pressure']} hPa")
st.info(f"**Condition:** {current['weather'][0]['description'].title()}")

    # =============================
    # WEATHER DETAILS
    # =============================
st.subheader("🧾 Weather Details")
colA, colB = st.columns(2)
colA.write(f"🌅 Sunrise: {pd.to_datetime(current['sys']['sunrise'], unit='s')}")
colA.write(f"🌇 Sunset: {pd.to_datetime(current['sys']['sunset'], unit='s')}")
colB.write(f"🌍 Country: {current['sys']['country']}")
colB.write(f"👁 Visibility: {current.get('visibility',0)/1000} km")

    # =============================
    # FORECAST DATA
    # =============================
rows = []
for item in forecast["list"]:
    rows.append({
        "Datetime": item["dt_txt"],
        "Temperature": item["main"]["temp"],
        "Humidity": item["main"]["humidity"]
    })

df = pd.DataFrame(rows)
df["Datetime"] = pd.to_datetime(df["Datetime"])
df["Hour"] = df["Datetime"].dt.hour
df["Month"] = df["Datetime"].dt.month_name()

    # =============================
    # HOURLY TREND
    # =============================
st.subheader("⏰ Hourly Temperature Trend")
hourly = df.groupby("Hour", as_index=False)["Temperature"].mean()
fig_hour = px.line(hourly, x="Hour", y="Temperature", markers=True, template=chart_theme)
st.plotly_chart(fig_hour, use_container_width=True)

    # =============================
    # WEATHER TRENDS
    # =============================
st.subheader("📈 Weather Trends")
fig_trend = px.line(df, x="Datetime", y=["Temperature", "Humidity"], template=chart_theme)
st.plotly_chart(fig_trend, use_container_width=True)

    # =============================
    # MONTHLY TREND
    # =============================
st.subheader("📅 Monthly Temperature Trend")
monthly = df.groupby("Month", as_index=False)["Temperature"].mean()
fig_month = px.bar(monthly, x="Month", y="Temperature", color="Temperature", template=chart_theme)
st.plotly_chart(fig_month, use_container_width=True)

    # =============================
    # WEATHER MAP
    # =============================
st.subheader("🗺 Weather Map")
lat = current["coord"]["lat"]
lon = current["coord"]["lon"]
m = folium.Map(location=[lat, lon], zoom_start=8)
folium.Marker([lat, lon], popup=f"{city} - {temp} °C").add_to(m)
st_folium(m, width=700)

    # =============================
    # ML TEMPERATURE PREDICTION
    # =============================
st.subheader("🤖 ML Temperature Prediction")
print(df)
X  = df[["Hour","Humidity"]].values  # numpy array
y = df["Temperature"].values
model = LinearRegression()
model.fit(X, y)

next_hour = (df["Hour"].iloc[-1] + 1) % 24
avg_humidity = df["Humidity"].mean()

    # Predict
prediction = model.predict([[next_hour, avg_humidity]])
st.success(f"🌡 Predicted Temperature (Next Hour): **{prediction[0]:.2f} °C**")

    # =============================
    # WEATHER NEWS
    # =============================
st.subheader("📰 Weather News")
st.write("🔹 Climate change increasing extreme weather")
st.write("🔹 Heatwaves across South Asia")
st.write("🔹 Monsoon season updates")
st.write("🔹 Rising global temperatures")

    # =============================
    # RAW DATA
    # =============================
with st.expander("📊 View Raw Forecast Data"):
    st.dataframe(df)
