import requests, os
from datetime import datetime, timedelta, timezone

LAT, LON = 47.45804861714617, 19.054431492854786

r = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": LAT, "longitude": LON,
        "hourly": "precipitation,windspeed_10m",
        "forecast_days": 2,
        "timezone": "Europe/Budapest"
    }
)
data = r.json()

times  = data["hourly"]["time"]
precip = data["hourly"]["precipitation"]
wind   = data["hourly"]["windspeed_10m"]

# Determine if we're in the AM or PM run
now_utc = datetime.now(timezone.utc)
is_morning = now_utc.hour < 12

# Morning run: check today's remaining hours (next 12h)
# Evening run: check tomorrow's hours
budapest_offset = timedelta(hours=2)  # adjust to +1 in winter if needed
now_local = now_utc + budapest_offset

if is_morning:
    check_start = now_local.replace(minute=0, second=0, microsecond=0)
    check_end   = check_start + timedelta(hours=12)
    window_label = "today"
else:
    tomorrow = (now_local + timedelta(days=1)).date()
    check_start = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0)
    check_end   = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59)
    window_label = "tomorrow"

alerts = []
for i, t in enumerate(times):
    dt = datetime.fromisoformat(t)
    if check_start <= dt <= check_end:
        hour_label = dt.strftime("%H:%M")
        if precip[i] > 0:
            alerts.append(f"🌧 Rain ({precip[i]:.1f}mm) at {hour_label}")
        if wind[i] > 0:
            alerts.append(f"💨 Wind ({wind[i]:.0f} km/h) at {hour_label}")

if alerts:
    message = f"Get the pillows in {window_label}!\n" + "\n".join(alerts)
    token = os.environ["PUSHOVER_TOKEN"]
    for key_name in ["PUSHOVER_USER_HAVAG"]:
        user_key = os.environ.get(key_name)
        if user_key:
            requests.post("https://api.pushover.net/1/messages.json", data={
                "token": token, "user": user_key, "message": message,
                "title": "🛋 Pillow Alert"
            })
    print("Alert sent:\n", message)
else:
    print(f"No alert needed for {window_label}.")
