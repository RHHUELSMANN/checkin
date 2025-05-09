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

# Funktion zur flexiblen Datumserkennung
def parse_datum(eingabe: str) -> date:
    eingabe = eingabe.strip().replace('.', '').replace(' ', '')
    formate = ["%d%m%y", "%d%m%Y", "%d.%m.%Y", "%d.%m.%y"]
    for fmt in formate:
        try:
            return datetime.strptime(eingabe, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"❌ Ungültiges Datumsformat: {eingabe}")

st.set_page_config(page_title="Check-in & Visumrechner", page_icon="🧾")
st.title("🧾 Check-in- und Visumrechner")

# Abschnitt 1: Check-in-Zeitrechner
st.header("🛫 Check-in-Rechner für Flugreisen")
airline_code = st.text_input("✈ Airline-Kürzel (z. B. LH, X3, DE)", max_chars=5).upper().strip()
abflugort = st.text_input("📍 Abflugort (Stadt oder Land)", placeholder="z. B. San José, Costa Rica").strip()
datum_checkin_str = st.text_input("📅 Abflugdatum und Uhrzeit (z. B. 2405 1925)", placeholder="TTMM HHMM").strip()

if st.button("🧮 Check-in-Zeit berechnen"):
    if not airline_code or not abflugort or not datum_checkin_str:
        st.error("Bitte alle Felder ausfüllen.")
    elif airline_code not in checkin_fristen:
        st.error(f"Airline-Kürzel '{airline_code}' ist nicht in der Positivliste hinterlegt.")
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
                    frist_stunden = checkin_fristen[airline_code]["stunden"]
                    checkin_dt_local = abflug_dt_local - timedelta(hours=frist_stunden)
                    tz_de = pytz.timezone("Europe/Berlin")
                    checkin_dt_de = checkin_dt_local.astimezone(tz_de)

                    st.success("✅ Ergebnis:")
                    st.markdown(f"**Abflugzeit (lokal):** {abflug_dt_local.strftime('%d.%m.%Y %H:%M')} ({tz_name})")
                    st.markdown(f"**Check-in frühestens ab:** {checkin_dt_de.strftime('%d.%m.%Y %H:%M')} 🇩🇪 (deutscher Zeit)")

                    hinweis = checkin_fristen[airline_code].get("hinweis")
                    if hinweis:
                        st.info(f"ℹ️ Hinweis zur Airline: {hinweis}")
        except ValueError:
            st.error("Ungültiges Datumsformat. Bitte nutze z. B. '2405 1925'")

# Abschnitt 2: Altersberechnung
st.header("🧓 Altersberechnung")
geburtsdatum_str = st.text_input("Geburtsdatum (TT.MM.JJJJ oder 060525)", "17.08.1959")
try:
    geburtsdatum = parse_datum(geburtsdatum_str)
    heute = date.today()
    alter = heute.year - geburtsdatum.year - ((heute.month, heute.day) < (geburtsdatum.month, geburtsdatum.day))
    st.success(f"Alter: {alter} Jahre")
except ValueError as e:
    st.error(str(e))

# Abschnitt 3: Visumgültigkeit
st.header("🛂 Visum-Gültigkeit")
visum_start_str = st.text_input("Visum-Ausstellungsdatum (z. B. 100425)", "10.04.2025")
visum_tage = st.number_input("Gültigkeit in Tagen", min_value=1, max_value=365, value=35)
try:
    visum_start = parse_datum(visum_start_str)
    visum_ablauf = visum_start + timedelta(days=visum_tage)
    st.success(f"Ablaufdatum: {visum_ablauf.strftime('%d.%m.%Y')}")
except ValueError as e:
    st.error(str(e))

# Abschnitt 4: Datumsdifferenz
st.header("📊 Datumsdifferenz in Tagen")
datum1_str = st.text_input("Erstes Datum (z. B. 011224)", "01.12.2024")
datum2_str = st.text_input("Zweites Datum (z. B. 120325)", "12.03.2025")
try:
    datum1 = parse_datum(datum1_str)
    datum2 = parse_datum(datum2_str)
    diff_tage = abs((datum2 - datum1).days)
    st.success(f"Unterschied: {diff_tage} Tage")
except ValueError as e:
    st.error(str(e))
