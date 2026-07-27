import requests, os
from datetime import datetime, timedelta, timezone

LAT, LON = 47.45804861714617, 19.054431492854786

r = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": LAT, "longitude": LON,
        "hourly": "precipitation,windspeed_10m,windgusts_10m",
        "forecast_days": 2,
        "timezone": "Europe/Budapest"
    }
)
data = r.json()

times  = data["hourly"]["time"]
precip = data["hourly"]["precipitation"]
wind   = data["hourly"]["windspeed_10m"]
gusts  = data["hourly"]["windgusts_10m"]

now_utc = datetime.now(timezone.utc)
is_morning = now_utc.hour < 12

budapest_offset = timedelta(hours=2)
now_local = now_utc + budapest_offset
now_naive = now_local.replace(tzinfo=None)

if is_morning:
    check_start = now_naive.replace(minute=0, second=0, microsecond=0)
    check_end   = check_start + timedelta(hours=12)
    window_label = "ma"
else:
    tomorrow = (now_naive + timedelta(days=1)).date()
    check_start = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 0, 0)
    check_end   = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 23, 59)
    window_label = "holnap"

rain_events = []
wind_events = []

for i, t in enumerate(times):
    dt = datetime.fromisoformat(t)
    if check_start <= dt <= check_end:
        hour_label = dt.strftime("%H:%M")
        if precip[i] > 0:
            rain_events.append((precip[i], f"🌧 Eső ({precip[i]:.1f}mm) {hour_label}-kor"))
        if gusts[i] > 35:
            wind_events.append((gusts[i], f"💨 Széllökés ({gusts[i]:.0f} km/h) {hour_label}-kor"))
        elif wind[i] > 35:
            wind_events.append((wind[i], f"🌬 Szél ({wind[i]:.0f} km/h) {hour_label}-kor"))

top_rain = [msg for _, msg in sorted(rain_events, key=lambda x: x[0], reverse=True)[:1]]
top_wind = [msg for _, msg in sorted(wind_events, key=lambda x: x[0], reverse=True)[:2]]
all_alerts = top_wind + top_rain

if all_alerts:
    message = f"Vidd be a párnákat {window_label}!\n" + "\n".join(all_alerts)
    token = os.environ["PUSHOVER_TOKEN"]
    for key_name in ["PUSHOVER_USER_HAVAG", "PUSHOVER_USER_ENCI"]:
        user_key = os.environ.get(key_name)
        if user_key:
            requests.post("https://api.pushover.net/1/messages.json", data={
                "token": token, "user": user_key, "message": message,
                "title": "🛋 Párna Riasztás",
                "url": "weather://",
                "url_title": "Megnyitás Weather-ben"
            })
    print("Riasztás elküldve:\n", message)
else:
    print(f"Nincs riasztás {window_label}ra.")
