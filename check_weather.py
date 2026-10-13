import requests, os
from datetime import datetime, timedelta, timezone

LAT, LON = 47.45804861714617, 19.054431492854786
BUDAPEST_OFFSET = timedelta(hours=2)

r = requests.get(
    "https://api.open-meteo.com/v1/forecast",
    params={
        "latitude": LAT, "longitude": LON,
        "hourly": "precipitation,windspeed_10m,windgusts_10m",
        "forecast_days": 2,
        "timezone": "Europe/Budapest"
    },
    timeout=30
)
data = r.json()

times  = data["hourly"]["time"]
precip = data["hourly"]["precipitation"]
wind   = data["hourly"]["windspeed_10m"]
gusts  = data["hourly"]["windgusts_10m"]

now_utc = datetime.now(timezone.utc)
is_morning = now_utc.hour < 12

now_local = now_utc + BUDAPEST_OFFSET
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

# Collect hourly values in the window
window = []
for i, t in enumerate(times):
    dt = datetime.fromisoformat(t)
    if check_start <= dt <= check_end:
        window.append((dt, precip[i], wind[i], gusts[i]))

# --- Rain: group consecutive rainy hours into periods, keep the heaviest ---
rain_periods = []
period_start = None
period_total = 0.0
period_hours = 0

for dt, p, w, g in window:
    if p > 0:
        if period_start is None:
            period_start = dt
        period_total += p
        period_hours += 1
    else:
        if period_start is not None:
            rain_periods.append((period_total, period_start, period_hours))
            period_start = None
            period_total = 0.0
            period_hours = 0
if period_start is not None:
    rain_periods.append((period_total, period_start, period_hours))

rain_alerts = []
if rain_periods:
    total, start, hours = min(rain_periods, key=lambda x: x[1])
    duration = f"{hours} órán át" if hours > 1 else "1 órán át"
    rain_alerts.append(f"🌧 Eső {start.strftime('%H:%M')}-tól {total:.1f}mm {duration}")

# --- Wind: top 2 individual hours by gust or sustained ---
wind_events = []
for dt, p, w, g in window:
    hour_label = dt.strftime("%H:%M")
    if g > 35:
        wind_events.append((g, f"💨 Széllökés ({g:.0f} km/h) {hour_label}-kor"))
    elif w > 35:
        wind_events.append((w, f"🌬 Szél ({w:.0f} km/h) {hour_label}-kor"))

top_wind = [msg for _, msg in sorted(wind_events, key=lambda x: x[0], reverse=True)[:2]]

all_alerts = top_wind + rain_alerts

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
            }, timeout=15)
    print("Riasztás elküldve:\n", message)
else:
    print(f"Nincs riasztás {window_label}ra.")
