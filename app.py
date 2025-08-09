from flask import Flask, request, jsonify
from dateutil import parser as dtp
import pytz
from aspects import moon_daily_aspects
from ingresses import moon_ingresses

app = Flask(__name__)

@app.get("/health")
def health():
    return {"ok": True}

def parse_date_tz():
    date_str = request.args.get("date")  # YYYY-MM-DD or ISO
    tz_str = request.args.get("tz", "UTC")
    d = dtp.parse(date_str).date()
    tz = pytz.timezone(tz_str)
    return d, tz

@app.get("/moon/ingresses")
def ingresses():
    d, tz = parse_date_tz()
    events = moon_ingresses(d, tz)
    return jsonify({"date": d.isoformat(), "tz": str(tz), "events": events})

@app.get("/moon/aspects")
def aspects():
    d, tz = parse_date_tz()
    bodies = request.args.get("bodies", "Sun,Mer,Ven,Mars,Jup,Sat").split(",")
    orb = float(request.args.get("orb", "1.0"))
    events = moon_daily_aspects(d, tz, bodies=bodies, orb_deg=orb)
    return jsonify({"date": d.isoformat(), "tz": str(tz), "orb_deg": orb, "events": events})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
