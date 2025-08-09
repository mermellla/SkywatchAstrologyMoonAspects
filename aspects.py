import swisseph as swe
from datetime import datetime, timedelta, timezone

PLANET_CODES = {
    "Sun": swe.SUN, "Mer": swe.MERCURY, "Ven": swe.VENUS, "Mars": swe.MARS,
    "Jup": swe.JUPITER, "Sat": swe.SATURN, "Ura": swe.URANUS,
    "Nep": swe.NEPTUNE, "Plu": swe.PLUTO
}
ASPECTS = [0.0, 60.0, 90.0, 120.0, 180.0]

def to_jd(dt_utc):
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                      dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)

def lon(jd, body):
    return swe.calc_ut(jd, body, swe.FLG_SWIEPH | swe.FLG_SPEED)[0]

def delta_angle(a, b):
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)

def refine_exact(t0, t1, target_deg, body):
    # binary search until crossing |Δ - target| minimum
    for _ in range(28):
        tm = t0 + (t1 - t0)/2
        dm = delta_angle(lon(to_jd(tm), swe.MOON), lon(to_jd(tm), body))
        d0 = delta_angle(lon(to_jd(t0), swe.MOON), lon(to_jd(t0), body))
        if d0 < target_deg:
            going_up = dm > d0
        else:
            going_up = dm > d0
        # split on which side of target
        if dm < target_deg:
            t0 = tm
        else:
            t1 = tm
    return (t0 + (t1 - t0)/2)

def moon_daily_aspects(day_date, tz, bodies, orb_deg=1.0):
    local_start = tz.localize(datetime(day_date.year, day_date.month, day_date.day, 0, 0, 0))
    local_end   = local_start + timedelta(days=1)
    t0 = local_start.astimezone(timezone.utc)
    t1 = local_end.astimezone(timezone.utc)

    step = timedelta(minutes=10)
    events = []
    last_hit = { (b, asp): None for b in bodies for asp in ASPECTS }

    t = t0
    while t <= t1:
        jd = to_jd(t)
        moon_lon = lon(jd, swe.MOON)
        for b in bodies:
            body = PLANET_CODES[b]
            body_lon = lon(jd, body)
            d = delta_angle(moon_lon, body_lon)
            for asp in ASPECTS:
                if abs(d - asp) <= orb_deg:
                    # avoid duplicates by spacing hits at least 2 hours apart
                    key = (b, asp)
                    if last_hit[key] is None or (t - last_hit[key]).total_seconds() > 7200:
                        exact = refine_exact(t - step, t + step, asp, body)
                        events.append({
                            "moon_aspect": asp,
                            "to": b,
                            "timestamp_local": exact.astimezone(tz).isoformat(),
                            "timestamp_utc": exact.isoformat()
                        })
                        last_hit[key] = exact
        t += step
    # sort by time
    events.sort(key=lambda e: e["timestamp_utc"])
    return events
