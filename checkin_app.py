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

st.set_page_config(page_title="Check-in-Rechner", page_icon="🛫")
st.title("🛫 Check-in-Rechner für Flugreisen")

st.markdown("Gib deine Flugdaten ein und erfahre, **ab wann der Online-Check-in in Deutschland möglich ist**.")

# Eingabefelder
airline_code = st.text_input("✈ Airline-Kürzel (z. B. LH, X3, DE)", max_chars=5).upper().strip()
abflugort = st.text_input("📍 Abflugort (Stadt oder Land)", placeholder="z. B. San José, Costa Rica").strip()
datum_str = st.text_input("📅 Abflugdatum und Uhrzeit (lokal)", placeholder="z. B. 24.05.2025 19:25").strip()

if st.button("🧮 Check-in-Zeit berechnen"):
    if not airline_code or not abflugort or not datum_str:
        st.error("Bitte alle Felder ausfüllen.")
    elif airline_code not in checkin_fristen:
        st.error(f"Airline-Kürzel '{airline_code}' ist nicht in der Positivliste hinterlegt.")
    else:
        try:
            # Datum interpretieren
            abflug_dt = datetime.strptime(datum_str, "%d.%m.%Y %H:%M")

            # Geokoordinaten und Zeitzone finden
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
                    # Lokale Zeitzone anwenden
                    tz_local = pytz.timezone(tz_name)
                    abflug_dt_local = tz_local.localize(abflug_dt)

                    # Airline-Check-in-Frist holen
                    frist_stunden = checkin_fristen[airline_code]["stunden"]
                    checkin_dt_local = abflug_dt_local - timedelta(hours=frist_stunden)

                    # Umrechnen nach deutscher Zeit (mit Sommerzeit)
                    tz_de = pytz.timezone("Europe/Berlin")
                    checkin_dt_de = checkin_dt_local.astimezone(tz_de)

                    # Ausgabe
                    st.success("✅ Ergebnis:")
                    st.markdown(f"**Abflugzeit (lokal):** {abflug_dt_local.strftime('%d.%m.%Y %H:%M')} ({tz_name})")
                    st.markdown(f"**Check-in frühestens ab:** {checkin_dt_de.strftime('%d.%m.%Y %H:%M')} 🇩🇪 (deutscher Zeit)")

                    # Hinweis, falls vorhanden
                    hinweis = checkin_fristen[airline_code].get("hinweis")
                    if hinweis:
                        st.info(f"ℹ️ Hinweis zur Airline: {hinweis}")

        except ValueError:
            st.error("Ungültiges Datumsformat. Bitte nutze TT.MM.JJJJ HH:MM")