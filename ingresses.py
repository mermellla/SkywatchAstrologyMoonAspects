import swisseph as swe
from datetime import datetime, timedelta, timezone

# Helpers
def to_jd(dt_utc):
    return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, 
                      dt_utc.hour + dt_utc.minute/60 + dt_utc.second/3600)

def moon_longitude(jd):
    lon, lat, dist, _ = swe.calc_ut(jd, swe.MOON, swe.FLG_SWIEPH | swe.FLG_SPEED)
    return lon

def sign_index(lon):  # 0..11
    return int(lon // 30)

def refine_ingress(t0, t1):
    # binary search for when Moon crosses a 30° multiple
    for _ in range(24):
        tm = t0 + (t1 - t0)/2
        jd0, jd1, jdm = to_jd(t0), to_jd(t1), to_jd(tm)
        s0, sm = sign_index(moon_longitude(jd0)), sign_index(moon_longitude(jdm))
        if s0 == sm:
            t0 = tm
        else:
            t1 = tm
    return t1

def moon_ingresses(day_date, tz):
    # search from local midnight to next midnight in UTC
    local_start = tz.localize(datetime(day_date.year, day_date.month, day_date.day, 0, 0, 0))
    local_end   = local_start + timedelta(days=1)
    t0 = local_start.astimezone(timezone.utc)
    t1 = local_end.astimezone(timezone.utc)

    step = timedelta(minutes=30)
    events = []
    prev_sign = sign_index(moon_longitude(to_jd(t0)))
    t = t0 + step
    while t <= t1:
        s = sign_index(moon_longitude(to_jd(t)))
        if s != prev_sign:
            exact_utc = refine_ingress(t - step, t)
            exact_local = exact_utc.astimezone(tz)
            events.append({
                "event": "Moon ingress",
                "sign_index": s,
                "timestamp_local": exact_local.isoformat(),
                "timestamp_utc": exact_utc.isoformat()
            })
            prev_sign = s
        t += step
    return events
