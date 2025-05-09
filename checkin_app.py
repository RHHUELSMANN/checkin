
import streamlit as st
from datetime import datetime, timedelta
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
st.header("✈️ Check-in-Rechner für Flugreisen")

# Eingabe 1: Airline-Kürzel
airline_code = st.text_input("✈ Airline-Kürzel (z. B. LH, X3, DE)", max_chars=5).upper().strip()

# Eingabe 2: Check-in-Frist
frist_vorgabe = checkin_fristen.get(airline_code, {}).get("stunden", 24)
hinweis = checkin_fristen.get(airline_code, {}).get("hinweis")
stunden_input = st.number_input("🕓 Check-in-Frist in Stunden", min_value=1, max_value=336, value=frist_vorgabe)

# Eingabe 3: Abflugort
abflugort = st.text_input("📍 Abflugort (Stadt oder Land)", placeholder="z. B. San José, Costa Rica").strip()

# Eingabe 4: Abflugdatum und Uhrzeit
datum_checkin_str = st.text_input("📅 Abflugdatum und Uhrzeit (z. B. 2405 1925)", placeholder="TTMM HHMM").strip()

# Berechnung starten
if st.button("🧮 Check-in-Zeit berechnen"):
    if not airline_code or not abflugort or not datum_checkin_str:
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
            st.error("Ungültiges Datumsformat. Bitte nutze z. B. '2405 1925'")
