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

now_utc = datetime.now(timezone.utc)
is_morning = now_utc.hour < 12

budapest_offset = timedelta(hours=2)
now_local = now_utc + budapest_offset
now_naive = now_local.replace(tzinfo=None)  # strip timezone for comparison

if is_morning:
    check_start = now_naive.replace(minute=0, second=0, microsecond=0)
    check_end   = check_start + timedelta(hours=12)
    window_label = "today"
else:
    tomorrow = (now_naive + timedelta(days=1)).date()
    check_start = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0)
    check_end   = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59)
    window_label = "tomorrow"

alerts = []
for i, t in enumerate(times):
    dt = datetime.fromisoformat(t)  # naive, matches check_start/check_end now
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
