import os
import re
import psycopg2
import psycopg2.extras
from datetime import date, timedelta
from flask import Flask, request, jsonify, session, g, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash

BASE = os.path.dirname(os.path.abspath(__file__))

# إعداد التطبيق بحيث يخدم الواجهة العامة من static ولوحة الأدمن من مجلد admin
app = Flask(__name__, static_folder="static", static_url_path="")
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # الملفات الثابتة ما تتخزّنش في الكاش
app.permanent_session_lifetime = timedelta(days=30)  # الجلسة بتفضل محفوظة 30 يوم

DATABASE_URL = os.environ.get("DATABASE_URL")


@app.before_request
def keep_session():
    session.permanent = True


CITIES = {
    "CAI": "القاهرة",
    "HRG": "الغردقة",
    "SSH": "شرم الشيخ",
    "LXR": "الأقصر",
    "ASW": "أسوان",
    "DXB": "دبي",
    "JED": "جدة",
    "RUH": "الرياض",
    "IST": "إسطنبول",
}
ROUTES = [
    ("CAI", "HRG", 75, 1800),
    ("CAI", "SSH", 80, 2000),
    ("CAI", "LXR", 70, 1500),
    ("CAI", "ASW", 105, 1700),
    ("CAI", "DXB", 240, 9500),
    ("CAI", "JED", 150, 6500),
    ("CAI", "RUH", 170, 7200),
    ("CAI", "IST", 190, 8800),
]
AIRLINES = ["مصر للطيران", "نايل إير", "إير كايرو"]
TIMES = ["07:30", "13:15", "19:45"]
HOTELS = [("فندق ريفييرا", 900), ("منتجع الواحة", 1800), ("جراند بالاس", 3600)]


def get_db_connection():
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL, sslmode="prefer")
        return conn
    else:
        import sqlite3

        db_path = os.path.join(BASE, "rehlaty.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    schema_path = os.path.join(BASE, "schema.sql")
    if os.path.exists(schema_path):
        with open(schema_path, encoding="utf-8") as f:
            script = f.read()
            if DATABASE_URL:
                script = (
                    script.replace("INTEGER PRIMARY KEY AUTOINCREMENT", "SERIAL PRIMARY KEY")
                    .replace("DATETIME", "TIMESTAMP")
                    .replace("CURRENT_TIMESTAMP", "NOW()")
                )
            cursor.execute(script)
            conn.commit()

    cursor.execute("SELECT 1 FROM flights LIMIT 1")
    if not cursor.fetchone():
        for a, b, mins, price in ROUTES:
            for o, d in ((a, b), (b, a)):
                for i, t in enumerate(TIMES):
                    cursor.execute(
                        "INSERT INTO flights(origin,dest,airline,depart_time,duration_min,price)"
                        " VALUES(%s,%s,%s,%s,%s,%s)"
                        if DATABASE_URL
                        else "INSERT INTO flights(origin,dest,airline,depart_time,duration_min,price)"
                        " VALUES(?,?,?,?,?,?)",
                        (o, d, AIRLINES[i], t, mins, price + i * 150),
                    )
        for code, city in CITIES.items():
            for i, (h, price) in enumerate(HOTELS):
                cursor.execute(
                    "INSERT INTO hotels(city,name,stars,price_per_night,rating)"
                    " VALUES(%s,%s,%s,%s,%s)"
                    if DATABASE_URL
                    else "INSERT INTO hotels(city,name,stars,price_per_night,rating)"
                    " VALUES(?,?,?,?,?)",
                    (code, f"{h} {city}", 3 + i, price, round(7.4 + i * 0.8, 1)),
                )
        conn.commit()
    
    # التأكد من وجود حساب أدمن افتراضي للاختبار (Admin / ADFS Federation Mock)
    cursor.execute("SELECT id FROM users WHERE email='admin@rehlti.com'")
    if not cursor.fetchone():
        admin_pass = generate_password_hash("admin12345")
        if DATABASE_URL:
            cursor.execute("INSERT INTO users(name,email,password_hash) VALUES(%s,%s,%s)", ("System Admin", "admin@rehlti.com", admin_pass))
        else:
            cursor.execute("INSERT INTO users(name,email,password_hash) VALUES(?,?,?)", ("System Admin", "admin@rehlti.com", admin_pass))
        conn.commit()

    cursor.close()
    conn.close()


def db():
    if "db" not in g:
        g.db = get_db_connection()
    return g.db


@app.teardown_appcontext
def close_db(_):
    d = g.pop("db", None)
    if d:
        d.close()


def err(msg, code=400):
    return jsonify(error=msg), code


def to_int(v, default=1):
    try:
        return max(1, min(int(v), 20))
    except (TypeError, ValueError):
        return default


def valid_date(s):
    try:
        return date.fromisoformat(s) >= date.today()
    except (TypeError, ValueError):
        return False


def _factor(day, key):
    ahead = (day - date.today()).days
    f = (
        0.85
        if ahead >= 30
        else 1.0 if ahead >= 14 else 1.12 if ahead >= 7 else 1.28
    )
    if day.weekday() in (3, 4):
        f *= 1.12
    if day.month in (7, 8, 12):
        f *= 1.2
    return f * (1 + ((key * 7 + day.toordinal()) % 11 - 5) / 100)


def flight_price(r, day):
    return (
        round(
            r["price"]
            * (0.88 if flight_info(r)[0] else 1)
            * _factor(date.fromisoformat(day), r["id"])
            / 10
        )
        * 10
    )


def hotel_total(r, a, b):
    d0 = date.fromisoformat(a)
    n = (date.fromisoformat(b) - d0).days
    return sum(
        round(
            r["price_per_night"]
            * _factor(d0 + timedelta(i), r["id"])
            / 10
        )
        * 10
        for i in range(n)
    )


INTL = {"DXB", "JED", "RUH", "IST"}
CABIN = {"economy": 1.0, "business": 2.6}
CURRENCIES = {
    "EGP": {"rate": 1, "symbol": "ج.م"},
    "USD": {"rate": 0.0205, "symbol": "$"},
    "SAR": {"rate": 0.077, "symbol": "ر.س"},
    "EUR": {"rate": 0.0189, "symbol": "€"},
}

AIRCRAFT = {
    False: {
        "مصر للطيران": ("بوينج 737-800", 160),
        "نايل إير": ("إيرباص A320", 180),
        "إير كايرو": ("إيرباص A320", 174),
    },
    True: {
        "مصر للطيران": ("إيرباص A330", 280),
        "نايل إير": ("إيرباص A321", 200),
        "إير كايرو": ("بوينج 737-800", 160),
    },
}
MAX_PER_BOOKING = 9


def aircraft(r):
    return AIRCRAFT[r["origin"] in INTL or r["dest"] in INTL][r["airline"]]


def seats_left(r, day):
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(
        f"SELECT COALESCE(SUM(qty),0) FROM bookings WHERE type='flight' AND"
        f" item_id={ph} AND start_date={ph} AND status='confirmed'",
        (r["id"], day),
    )
    taken = cur.fetchone()[0]
    cur.close()
    return max(0, aircraft(r)[1] - taken)


def clean_passengers(items, kind, qty, intl):
    need = qty if kind == "flight" else 1
    if not isinstance(items, list) or len(items) != need:
        return None, "اكتب بيانات كل المسافرين"
    out = []
    for p in items:
        p = p if isinstance(p, dict) else {}
        name = " ".join(str(p.get("full_name") or "").split())
        if kind == "hotel":
            phone = re.sub(r"[ -]", "", str(p.get("phone") or ""))
            if len(name) < 3 or not re.fullmatch(r"\+?\d{8,15}", phone):
                return None, "اكتب اسم النزيل ورقم تليفون صحيح"
            out.append({"full_name": name, "phone": phone})
            continue
        dtype, num, dob = (
            p.get("doc_type"),
            str(p.get("doc_number") or "").strip(),
            p.get("birth_date"),
        )
        if not re.fullmatch(r"[A-Za-z]+( [A-Za-z]+)+", name):
            return (
                None,
                "الاسم لازم يكون بالإنجليزي (الاسم الأول والأخير) زي ما هو في الوثيقة",
            )
        if dtype not in ("national_id", "passport") or (intl and dtype != "passport"):
            return (None, "الرحلات الدولية لازم جواز سفر" if intl else "اختار نوع الوثيقة")
        if dtype == "national_id" and not re.fullmatch(r"\d{14}", num):
            return None, "الرقم القومي لازم يكون 14 رقم"
        if dtype == "passport" and not re.fullmatch(r"[A-Za-z0-9]{6,12}", num):
            return None, "رقم الجواز غير صحيح"
        try:
            if date.fromisoformat(dob) >= date.today():
                raise ValueError
        except (TypeError, ValueError):
            return None, "تاريخ الميلاد غير صحيح"
        out.append({
            "full_name": name.upper(),
            "doc_type": dtype,
            "doc_number": num,
            "birth_date": dob,
        })
    
    # تم تصحيح موقع الإرجاع ليكون خارج حلقة التكرار تماماً لتجنب خطأ الـ NoneType
    return out, None


def flight_info(r):
    stops = (
        1
        if r["airline"] == "إير كايرو"
        and (r["origin"] in INTL or r["dest"] in INTL)
        else 0
    )
    return stops, r["duration_min"] + 85 * stops


def return_price(r, ret, mult):
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(
        f"SELECT * FROM flights WHERE origin={ph} AND dest={ph} AND"
        f" airline={ph} ORDER BY depart_time LIMIT 1",
        (r["dest"], r["origin"], r["airline"]),
    )
    if DATABASE_URL:
        col_names = [desc[0] for desc in cur.description]
        row = cur.fetchone()
        rv = dict(zip(col_names, row)) if row else None
    else:
        rv = cur.fetchone()
    cur.close()
    return (
        round(flight_price(rv, ret) * mult / 10) * 10
        if rv
        else 0
    )


# ---------- المسارات العامة للواجهة ----------
@app.get("/")
def index():
    return app.send_static_file("index.html")


# ---------- مسارات لوحة الأدمن (Admin Dashboard & ADFS Hook) ----------
@app.get("/admin")
@app.get("/admin/")
def admin_index():
    return send_from_directory(os.path.join(BASE, "admin"), "index.html")


@app.get("/admin/<path:filename>")
def admin_static(filename):
    return send_from_directory(os.path.join(BASE, "admin"), filename)


@app.get("/api/admin/bookings")
def admin_get_bookings():
    # التحقق من صلاحيات الأدمن (في المستقبل يتم ربطها بـ ADFS / IAM Federation Claims)
    uid = session.get("uid")
    if not uid:
        return err("يرجى تسجيل الدخول كمسؤول", 401)
    
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    
    # التحقق هل المستخدم الحالي هو المسؤول (admin@rehlti.com)
    cur.execute(f"SELECT email FROM users WHERE id={ph}", (uid,))
    row = cur.fetchone()
    if not row or (row[0] if not DATABASE_URL else row[0]) != "admin@rehlti.com":
        cur.close()
        return err("غير مسموح لك بالدخول، صلاحيات مسؤولين فقط", 403)

    cur.execute(
        "SELECT b.*, u.name as user_name, u.email as user_email FROM bookings b "
        "JOIN users u ON b.user_id = u.id ORDER BY b.id DESC"
    )
    if DATABASE_URL:
        col_names = [desc[0] for desc in cur.description]
        rows = [dict(zip(col_names, row)) for row in cur.fetchall()]
    else:
        rows = [dict(r) for r in cur.fetchall()]

    for r in rows:
        cur.execute(
            f"SELECT full_name, doc_number, phone FROM passengers WHERE booking_id={ph}",
            (r["id"],),
        )
        if DATABASE_URL:
            p_cols = [desc[0] for desc in cur.description]
            ps = [dict(zip(p_cols, row)) for row in cur.fetchall()]
        else:
            ps = [dict(p) for p in cur.fetchall()]
        r["passengers"] = ps

    cur.close()
    return jsonify(rows)


@app.post("/api/admin/bookings/<int:bid>/status")
def admin_update_booking_status(bid):
    uid = session.get("uid")
    if not uid:
        return err("غير مصرح", 401)
    
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(f"SELECT email FROM users WHERE id={ph}", (uid,))
    row = cur.fetchone()
    if not row or row[0] != "admin@rehlti.com":
        cur.close()
        return err("صلاحيات غير كافية", 403)

    j = request.get_json(silent=True) or {}
    new_status = j.get("status")  # confirmed, cancelled
    if new_status not in ("confirmed", "cancelled"):
        cur.close()
        return err("حالة غير صحيحة")

    cur.execute(
        f"UPDATE bookings SET status={ph} WHERE id={ph}",
        (new_status, bid),
    )
    db().commit()
    cur.close()
    return jsonify(ok=True)


# ---------- باقي مسارات الـ API العادية ----------
@app.get("/api/cities")
def cities():
    return jsonify([{"code": k, "name": v} for k, v in CITIES.items()])


@app.post("/api/register")
def register():
    j = request.get_json(silent=True) or {}
    name, email, pw = (
        (j.get("name") or "").strip(),
        (j.get("email") or "").strip().lower(),
        j.get("password") or "",
    )
    if not name or "@" not in email or len(pw) < 6:
        return err("اكتب الاسم وإيميل صحيح وكلمة سر 6 حروف على الأقل")
    try:
        cur = db().cursor()
        ph = "%s" if DATABASE_URL else "?"
        if DATABASE_URL:
            cur.execute(
                f"INSERT INTO users(name,email,password_hash) VALUES({ph},{ph},{ph})"
                " RETURNING id",
                (name, email, generate_password_hash(pw)),
            )
            uid = cur.fetchone()[0]
        else:
            cur.execute(
                f"INSERT INTO users(name,email,password_hash) VALUES({ph},{ph},{ph})",
                (name, email, generate_password_hash(pw)),
            )
            uid = cur.lastrowid
        db().commit()
        cur.close()
    except Exception:
        return err("الإيميل ده مسجل قبل كده", 409)
    session["uid"] = uid
    return jsonify(id=uid, name=name), 201


@app.post("/api/login")
def login():
    j = request.get_json(silent=True) or {}
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(
        f"SELECT * FROM users WHERE email={ph}",
        ((j.get("email") or "").strip().lower(),),
    )
    if DATABASE_URL:
        row = cur.fetchone()
        col_names = [desc[0] for desc in cur.description]
        u = dict(zip(col_names, row)) if row else None
    else:
        u = cur.fetchone()
    cur.close()
    if not u or not check_password_hash(u["password_hash"], j.get("password") or ""):
        return err("الإيميل أو كلمة السر غلط", 401)
    session["uid"] = u["id"]
    return jsonify(id=u["id"], name=u["name"])


@app.post("/api/logout")
def logout():
    session.clear()
    return jsonify(ok=True)


@app.get("/api/me")
def me():
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(f"SELECT id,name,email FROM users WHERE id={ph}", (session.get("uid"),))
    if DATABASE_URL:
        row = cur.fetchone()
        col_names = [desc[0] for desc in cur.description]
        u = dict(zip(col_names, row)) if row else None
    else:
        u = cur.fetchone()
    cur.close()
    return jsonify(dict(u) if u else None)


@app.get("/api/rates")
def rates():
    return jsonify(CURRENCIES)


@app.get("/api/offers")
def offers():
    day = (date.today() + timedelta(days=21)).isoformat()
    out = []
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    for o, d, *_ in ROUTES:
        cur.execute(
            f"SELECT * FROM flights WHERE origin={ph} AND dest={ph}", (o, d)
        )
        if DATABASE_URL:
            col_names = [desc[0] for desc in cur.description]
            rows = [dict(zip(col_names, row)) for row in cur.fetchall()]
        else:
            rows = cur.fetchall()
        best = min(flight_price(r, day) for r in rows) if rows else 0
        out.append({
            "origin": o,
            "dest": d,
            "origin_name": CITIES[o],
            "dest_name": CITIES[d],
            "price": best,
            "date": day,
        })
    cur.close()
    return jsonify(sorted(out, key=lambda x: x["price"])[:6])


@app.get("/api/flights")
def flights():
    o, d, day = (
        request.args.get("from"),
        request.args.get("to"),
        request.args.get("date"),
    )
    n, ret = min(
        to_int(request.args.get("passengers")), MAX_PER_BOOKING
    ), request.args.get("return_date") or None
    mult = CABIN.get(request.args.get("cabin", "economy"), 1.0)
    if o not in CITIES or d not in CITIES or o == d:
        return err("اختار مدينة سفر ومدينة وصول مختلفتين")
    if not valid_date(day):
        return err("التاريخ لازم يكون النهارده أو بعده")
    if ret and (not valid_date(ret) or ret < day):
        return err("تاريخ العودة لازم يكون بعد تاريخ السفر")

    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(
        f"SELECT * FROM flights WHERE origin={ph} AND dest={ph} ORDER BY"
        " depart_time",
        (o, d),
    )
    if DATABASE_URL:
        col_names = [desc[0] for desc in cur.description]
        rows = [dict(zip(col_names, row)) for row in cur.fetchall()]
    else:
        rows = cur.fetchall()
    cur.close()

    out = []
    for r in rows:
        stops, dur = flight_info(r)
        p = (
            round(flight_price(r, day) * mult / 10) * 10
            + (return_price(r, ret, mult) if ret else 0)
        )
        left = seats_left(r, day)
        out.append({
            **dict(r),
            "stops": stops,
            "duration_min": dur,
            "price": p,
            "total": p * n,
            "aircraft": aircraft(r)[0],
            "capacity": aircraft(r)[1],
            "seats_left": left,
            "available": left >= n,
            "international": r["origin"] in INTL or r["dest"] in INTL,
            "round_trip": bool(ret),
            "origin_name": CITIES[o],
            "dest_name": CITIES[d],
        })
    return jsonify(out)


@app.get("/api/hotels")
def hotels():
    city, a, b = (
        request.args.get("city"),
        request.args.get("checkin"),
        request.args.get("checkout"),
    )
    rooms = to_int(request.args.get("rooms"))
    if city not in CITIES:
        return err("اختار المدينة")
    if not valid_date(a) or not valid_date(b) or b <= a:
        return err("تاريخ الخروج لازم يكون بعد تاريخ الدخول")
    nights = (date.fromisoformat(b) - date.fromisoformat(a)).days

    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(
        f"SELECT * FROM hotels WHERE city={ph} ORDER BY price_per_night", (city,)
    )
    if DATABASE_URL:
        col_names = [desc[0] for desc in cur.description]
        rows = [dict(zip(col_names, row)) for row in cur.fetchall()]
    else:
        rows = cur.fetchall()
    cur.close()

    out = []
    for r in rows:
        t = hotel_total(r, a, b)
        out.append({
            **dict(r),
            "city_name": CITIES[city],
            "nights": nights,
            "price_per_night": round(t / nights),
            "total": t * rooms,
        })
    return jsonify(out)


@app.post("/api/bookings")
def book():
    uid = session.get("uid")
    if not uid:
        return err("سجّل دخولك الأول", 401)
    j = request.get_json(silent=True) or {}
    kind, start, end, qty = (
        j.get("type"),
        j.get("date"),
        j.get("end_date"),
        to_int(j.get("qty")),
    )
    if not valid_date(start):
        return err("التاريخ غير صحيح")

    conn = db()
    cur = conn.cursor()
    ph = "%s" if DATABASE_URL else "?"

    if kind == "flight":
        cur.execute(f"SELECT * FROM flights WHERE id={ph}", (j.get("item_id"),))
        if DATABASE_URL:
            row = cur.fetchone()
            col_names = [desc[0] for desc in cur.description]
            r = dict(zip(col_names, row)) if row else None
        else:
            r = cur.fetchone()

        if not r:
            cur.close()
            return err("الرحلة مش موجودة", 404)
        if qty > MAX_PER_BOOKING:
            cur.close()
            return err(f"أقصى عدد ركاب في الحجز الواحد {MAX_PER_BOOKING}")

        left = seats_left(r, start)
        if left < qty:
            cur.close()
            return err(
                "الرحلة دي مكتملة"
                if left == 0
                else f"المتاح {left} مقعد بس في الرحلة دي",
                409,
            )

        mult, ret = CABIN.get(j.get("cabin"), 1.0), j.get("return_date") or None
        if ret and (not valid_date(ret) or ret < start):
            cur.close()
            return err("تاريخ العودة لازم يكون بعد تاريخ السفر")

        p = (
            round(flight_price(r, start) * mult / 10) * 10
            + (return_price(r, ret, mult) if ret else 0)
        )
        title = (
            f"{CITIES[r['origin']]} إلى {CITIES[r['dest']]} - {r['airline']} -"
            f" {r['depart_time']}"
            + (" - ذهاب وعودة" if ret else "")
            + (" - رجال أعمال" if mult > 1 else "")
        )
        total, end = p * qty, ret

    elif kind == "hotel":
        cur.execute(f"SELECT * FROM hotels WHERE id={ph}", (j.get("item_id"),))
        if DATABASE_URL:
            row = cur.fetchone()
            col_names = [desc[0] for desc in cur.description]
            r = dict(zip(col_names, row)) if row else None
        else:
            r = cur.fetchone()

        if not r:
            cur.close()
            return err("الفندق مش موجود", 404)
        if not valid_date(end) or end <= start:
            cur.close()
            return err("تاريخ الخروج لازم يكون بعد الدخول")
        title = r["name"]
        total = hotel_total(r, start, end) * qty
    else:
        cur.close()
        return err("نوع الحجز غير صحيح")

    pax, msg = clean_passengers(
        j.get("passengers"),
        kind,
        qty,
        kind == "flight" and (r["origin"] in INTL or r["dest"] in INTL),
    )
    if msg:
        cur.close()
        return err(msg)

    if DATABASE_URL:
        cur.execute(
            f"INSERT INTO bookings(user_id,type,item_id,title,start_date,end_date,qty,total) VALUES({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph}) RETURNING id",
            (uid, kind, r["id"], title, start, end, qty, total),
        )
        booking_id = cur.fetchone()[0]
    else:
        cur.execute(
            f"INSERT INTO bookings(user_id,type,item_id,title,start_date,end_date,qty,total) VALUES({ph},{ph},{ph},{ph},{ph},{ph},{ph},{ph})",
            (uid, kind, r["id"], title, start, end, qty, total),
        )
        booking_id = cur.lastrowid

    for p in pax:
        cur.execute(
            f"INSERT INTO passengers(booking_id,full_name,doc_type,doc_number,birth_date,phone) VALUES({ph},{ph},{ph},{ph},{ph},{ph})",
            (
                booking_id,
                p["full_name"],
                p.get("doc_type"),
                p.get("doc_number"),
                p.get("birth_date"),
                p.get("phone"),
            ),
        )

    conn.commit()
    cur.close()
    return jsonify(id=booking_id, total=total), 201


@app.get("/api/bookings")
def my_bookings():
    uid = session.get("uid")
    if not uid:
        return err("سجّل دخولك الأول", 401)

    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(
        f"SELECT * FROM bookings WHERE user_id={ph} ORDER BY id DESC", (uid,)
    )
    if DATABASE_URL:
        col_names = [desc[0] for desc in cur.description]
        rows = [dict(zip(col_names, row)) for row in cur.fetchall()]
    else:
        rows = cur.fetchall()

    out = []
    for r in rows:
        cur.execute(
            f"SELECT full_name,doc_number FROM passengers WHERE booking_id={ph}",
            (r["id"],),
        )
        if DATABASE_URL:
            p_cols = [desc[0] for desc in cur.description]
            ps = [dict(zip(p_cols, row)) for row in cur.fetchall()]
        else:
            ps = cur.fetchall()

        out.append({
            **dict(r),
            "passengers": [{
                "full_name": p["full_name"],
                "doc_masked": (
                    ("•••••" + p["doc_number"][-3:]) if p["doc_number"] else ""
                ),
            } for p in ps],
        })
    cur.close()
    return jsonify(out)


@app.delete("/api/bookings/<int:bid>")
def cancel(bid):
    uid = session.get("uid")
    if not uid:
        return err("سجّل دخولك الأول", 401)
    cur = db().cursor()
    ph = "%s" if DATABASE_URL else "?"
    cur.execute(
        f"UPDATE bookings SET status='cancelled' WHERE id={ph} AND user_id={ph}",
        (bid, uid),
    )
    rowcount = cur.rowcount
    db().commit()
    cur.close()
    return jsonify(ok=True) if rowcount else err("الحجز مش موجود", 404)


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5055))
    print(f"\n>>> افتح الموقع على: http://127.0.0.1:{port}\n")
    print(f">>> لوحة الأدمن على: http://127.0.0.1:{port}/admin\n")
    app.run(debug=True, port=port)
