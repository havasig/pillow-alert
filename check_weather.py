import requests, os

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

precip = data["hourly"]["precipitation"][24:48]
wind   = data["hourly"]["windspeed_10m"][24:48]

rain_expected = any(p > 0 for p in precip)
wind_expected = any(w > 40 for w in wind)

if rain_expected or wind_expected:
    reasons = []
    if rain_expected: reasons.append(f"🌧 Rain up to {max(precip):.1f}mm/h")
    if wind_expected: reasons.append(f"💨 Wind up to {max(wind):.0f} km/h")
    message = "Get the pillows in! " + " · ".join(reasons)

    token = os.environ["PUSHOVER_TOKEN"]
    for key_name in ["PUSHOVER_USER_HAVAG"]:
        user_key = os.environ.get(key_name)
        if user_key:
            requests.post("https://api.pushover.net/1/messages.json", data={
                "token": token, "user": user_key, "message": message,
                "title": "🛋 Pillow Alert for Tomorrow"
            })
    print("Alert sent:", message)
else:
    print("No alert needed.")
