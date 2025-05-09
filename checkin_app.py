
import streamlit as st
from datetime import datetime, timedelta, date
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
import pytz

# Airline-Check-in-Fristen (in Stunden)
checkin_fristen = {
    "4M": {"name": "Mavi Gök Airlines", "stunden": 24},
    "ART": {"name": "SmartLynx Airlines", "stunden": 72},
    "DE": {"name": "Condor", "stunden": 24},
    "EW": {"name": "Eurowings", "stunden": 72, "hinweis": "Check-in evtl. kostenpflichtig"},
    "LH": {"name": "Lufthansa", "stunden": 30},
    "SR": {"name": "Sundair", "stunden": 48, "hinweis": "Reisepass erforderlich"},
    "XC": {"name": "Corendon Airlines", "stunden": 72, "hinweis": "Check-in evtl. kostenpflichtig"},
    "X3": {"name": "TUIfly", "stunden": 336, "hinweis": "Check-in evtl. kostenpflichtig"},
    "XQ": {"name": "SunExpress", "stunden": 72, "hinweis": "Check-in evtl. kostenpflichtig, Reisepass erforderlich"},
}

st.set_page_config(page_title="Check-in & Visumrechner", page_icon="🧾")
st.title("🧾 Check-in- und Visumrechner")

# Abschnitt 1: Check-in-Rechner
st.header("✈️ Check-in-Rechner für Flugreisen")

airline_code = st.text_input("✈ Airline-Kürzel (z. B. LH, X3, DE)", max_chars=5).upper().strip()
frist_vorgabe = checkin_fristen.get(airline_code, {}).get("stunden", 24)
hinweis = checkin_fristen.get(airline_code, {}).get("hinweis")
stunden_input = st.number_input("🕓 Check-in-Frist in Stunden", min_value=1, max_value=336, value=frist_vorgabe)
abflugort = st.text_input("📍 Abflugort (Stadt oder Land)", placeholder="z. B. San José, Costa Rica").strip()
datum_checkin_str = st.text_input("📅 Abflugdatum und Uhrzeit (z. B. 2405 1925)", placeholder="TTMM HHMM").strip()

if st.button("🧮 Check-in-Zeit berechnen"):
    if not abflugort or not datum_checkin_str:
        st.error("Bitte alle Felder ausfüllen.")
    else:
        try:
            year = datetime.now().year
            abflug_dt = datetime.strptime(datum_checkin_str, "%d%m %H%M").replace(year=year)
            geolocator = Nominatim(user_agent="checkin_app")
            location = geolocator.geocode(abflugort)
            if not location:
                st.error("Ort konnte nicht gefunden werden.")
            else:
                tf = TimezoneFinder()
                tz_name = tf.timezone_at(lng=location.longitude, lat=location.latitude)
                if not tz_name:
                    st.error("Zeitzone konnte nicht bestimmt werden.")
                else:
                    tz_local = pytz.timezone(tz_name)
                    abflug_dt_local = tz_local.localize(abflug_dt)
                    checkin_dt_local = abflug_dt_local - timedelta(hours=stunden_input)
                    tz_de = pytz.timezone("Europe/Berlin")
                    checkin_dt_de = checkin_dt_local.astimezone(tz_de)
                    st.success("✅ Ergebnis:")
                    st.markdown(f"**Abflugzeit (lokal):** {abflug_dt_local.strftime('%d.%m.%Y %H:%M')} ({tz_name})")
                    st.markdown(f"**Check-in frühestens ab:** {checkin_dt_de.strftime('%d.%m.%Y %H:%M')} 🇩🇪 (deutsche Zeit)")
                    if hinweis:
                        st.info(f"ℹ️ Hinweis zur Airline: {hinweis}")
        except ValueError:
            st.error("Ungültiges Datumsformat. Bitte TTMM HHMM eingeben.")

# Abschnitt 2: Altersberechnung
st.header("🧓 Altersberechnung")
geburtsdatum_str = st.text_input("Geburtsdatum (TTMMJJJJ)", "")
def parse_geburtsdatum(text):
    if not text or len(text.strip()) != 8 or not text.strip().isdigit():
        return "-"
    try:
        geb = datetime.strptime(text.strip(), "%d%m%Y")
        heute = date.today()
        alter = heute.year - geb.year - ((heute.month, heute.day) < (geb.month, geb.day))
        return str(alter)
    except:
        return "-"
st.success(f"Alter: {parse_geburtsdatum(geburtsdatum_str)} Jahre") if parse_geburtsdatum(geburtsdatum_str) != "-" else st.warning("Bitte TTMMJJJJ eingeben")

# Abschnitt 3: Visum-Gültigkeit
st.header("🛂 Visum-Gültigkeit")
visum_start_str = st.text_input("Visum-Ausstellungsdatum (TTMMJJJJ)", "")
visum_tage = st.number_input("Gültigkeit in Tagen", min_value=1, max_value=365, value=30)
try:
    visum_start = datetime.strptime(visum_start_str, "%d%m%Y").date()
    visum_ablauf = visum_start + timedelta(days=visum_tage)
    st.success(f"Ablaufdatum: {visum_ablauf.strftime('%d.%m.%Y')}")
except:
    if visum_start_str:
        st.error("Ungültiges Datum. Format: TTMMJJJJ")

# Abschnitt 4: Datumsdifferenz
st.header("📊 Datumsdifferenz in Tagen")
datum1_str = st.text_input("Erstes Datum (TTMMJJJJ)", "")
datum2_str = st.text_input("Zweites Datum (TTMMJJJJ)", "")
try:
    d1 = datetime.strptime(datum1_str.strip(), "%d%m%Y").date()
    d2 = datetime.strptime(datum2_str.strip(), "%d%m%Y").date()
    diff = abs((d2 - d1).days)
    st.success(f"Unterschied: {diff} Tage")
except:
    if datum1_str and datum2_str:
        st.error("Bitte beide Daten korrekt im Format TTMMJJJJ eingeben.")

