import streamlit as st
import requests
from datetime import datetime
from geopy.distance import geodesic
import pandas as pd
# ================================
# Stop Coordinates Dictionary
# ================================
stop_coords = {
    "Kottar": (8.1850, 77.4380),
    "Suchindram": (8.1625, 77.4764),
    "Vadasery": (8.1793, 77.4425),
    "Kulasekaram": (8.4450, 77.3000),
    "Kanyakumari": (8.0780, 77.5410),
    "Nagercoil": (8.1780, 77.4280),
    "Aralvaimozhi": (8.2590, 77.5600),
    "Boothapandi": (8.2510, 77.4720),
    "Tirunelveli Junction": (8.7294, 77.7081),
    "Tirunelveli Bus Stand": (8.7350, 77.7083),
    "Asaripallam": (8.2030, 77.4480),
    "Marthandam": (8.3160, 77.2170),
    "Thuckalay": (8.2700, 77.3050),
    "Kurunthancode": (8.1870, 77.3850),
    "Muttom": (8.1500, 77.3170),
    "Colachel Junction": (8.1780, 77.2580),
    "Colachel": (8.1760, 77.2580),
    "Vetturnimadam": (8.1820, 77.4385),
    "Kuzhithurai": (8.3100, 77.2200),
    "Thiruvattar": (8.3300, 77.3400),
    "Padmanabhapuram": (8.2510, 77.3380),
    "Parvathipuram": (8.1800, 77.4420),
    "Erumbukadu": (8.1900, 77.4400),
    "Thovalai": (8.2500, 77.4700),
    "Marthandam Bus Stand": (8.3200, 77.2300),
    "Eathamozhi": (8.2000, 77.4000),
    "Thingal Nagar": (8.2000, 77.3700),
    "Eraniel Junction": (8.2300, 77.3000),
    "Eraniel": (8.2250, 77.3000),
    "Meenakshipuram": (8.1400, 77.4800),
    "Puthalam": (8.1100, 77.5000),
    "Kaliyakkavilai": (8.1000, 77.5200),
    "Kottarakkara": (8.1500, 77.5500)
}
import requests

st.set_page_config(page_title="TNSTC Bus Attendance")

st.title("🚌 TNSTC Live Bus Attendance")

# Load buses ONCE
try:
    response = requests.get("http://127.0.0.1:8000/buses")
    buses = response.json()
except Exception:
    st.error("⚠️ Could not load buses. Is the backend running?")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🧑 Passenger",
    "🧑‍✈️ Conductor",
    "📊 Revenue Dashboard",
    "🚏 TNSTC Station Overview"
])

# ------------------------------
# Passenger Tab
# ------------------------------
with tab1:
    st.subheader("Mark Your Attendance")

    with st.expander("🚌 List of Buses Available (Click to View)"):
        for bus in buses:
            st.write(
                f"**{bus['bus_id']}** — {bus['route']} | "
                f"Departure: {bus['departure']} | Arrival: {bus['arrival']} | "
                f"Status: {bus['status']}"
            )

    bus_options = [bus["bus_id"] for bus in buses]
    selected_bus_id = st.selectbox("Select Bus", bus_options)

    selected_bus = next((b for b in buses if b["bus_id"] == selected_bus_id), None)
    stop_options = selected_bus["stops"]

    stop_name = st.selectbox("Select Your Stop", stop_options)
    passenger_id = st.text_input("Your Passenger ID (e.g., Mobile Number)")
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    status = st.radio("Current Status", ["waiting", "onboard"])

    if st.button("✅ Submit Attendance"):
        if not passenger_id:
            st.warning("Please fill all fields.")
        else:
            payload = {
                "passenger_id": passenger_id,
                "bus_id": selected_bus_id,
                "stop_name": stop_name,
                "gender": gender,
                "timestamp": datetime.utcnow().isoformat(),
                "status": status,
                "bus_lat": selected_bus["current_lat"],  # Capture bus position
                "bus_lon": selected_bus["current_lon"]
            }

            try:
                res = requests.post("http://127.0.0.1:8000/attendance", json=payload)
                if res.status_code == 200:
                    st.success("✅ Attendance recorded successfully.")

                    try:
                        bus_location = (selected_bus["current_lat"], selected_bus["current_lon"])
                        stop_location = stop_coords.get(stop_name)

                        if stop_location:
                            # Calculate ETA using geodesic distance
                            from geopy.distance import geodesic
                            bus_location = (selected_bus["current_lat"], selected_bus["current_lon"])
                            stop_location = stop_coords.get(stop_name)
                            distance_km = geodesic(bus_location, stop_location).km
                            eta_minutes = distance_km / 40 * 60
                            st.info(
                                f"🚍 Estimated arrival at **{stop_name}** in ~{int(eta_minutes)} minutes "
                                f"(Distance: {distance_km:.1f} km)"
                            )
                        else:
                            st.warning("⚠️ Stop location unknown; cannot calculate ETA.")
                    except Exception as e:
                        st.warning(f"⚠️ Could not calculate ETA: {e}")
                else:
                    st.error(f"❌ Error: {res.text}")
            except Exception:
                st.error("⚠️ Could not submit attendance.")

# ------------------------------
# Conductor Tab
# ------------------------------
with tab2:
    import folium
    from streamlit_folium import st_folium

    st.subheader("🎯 Bus Attendance Overview")

    selected_bus_id_conductor = st.selectbox(
        "Select Bus to View Attendance",
        [bus["bus_id"] for bus in buses]
    )

    st.write(f"📍 **Selected Bus:** {selected_bus_id_conductor}")

    try:
        res = requests.get(f"http://127.0.0.1:8000/attendance/{selected_bus_id_conductor}")
        if res.status_code == 200:
            records = res.json()
            if records:
                df = pd.DataFrame(records)
                st.success(f"✅ Found {len(df)} passengers for Bus {selected_bus_id_conductor}")

                m = folium.Map(location=[8.2, 77.4], zoom_start=9, tiles="cartodbpositron")

                selected_bus = next((b for b in buses if b["bus_id"] == selected_bus_id_conductor), None)
                if selected_bus:
                    bus_location = (selected_bus["current_lat"], selected_bus["current_lon"])
                    folium.Marker(
                        location=bus_location,
                        popup=f"🚌 Bus {selected_bus_id_conductor} Current Location",
                        icon=folium.Icon(color="red", icon="bus")
                    ).add_to(m)

                for _, row in df.iterrows():
                    stop_location = stop_coords.get(row["stop_name"])
                    if stop_location:
                        folium.Marker(
                            location=stop_location,
                            popup=f"Passenger: {row['passenger_id']}<br>Stop: {row['stop_name']}",
                            icon=folium.Icon(color="blue", icon="user")
                        ).add_to(m)

                st_folium(m, width=900, height=500)
                st.info(f"👥 **Total passengers booked for this bus:** {len(df)}")
            else:
                st.info("No attendance records for this bus yet.")
        else:
            st.error("Error retrieving attendance records.")
    except Exception as e:
        st.error(f"⚠️ Could not connect to backend: {e}")

# ------------------------------
# Revenue Dashboard Tab
# ------------------------------
# ------------------------------
# Revenue Dashboard Tab
# ------------------------------
with tab3:
    from datetime import timedelta, datetime as dt
    import plotly.express as px

    st.subheader("📊 TNSTC Revenue Dashboard")

    all_records = []
    for bus in buses:
        try:
            res = requests.get(f"http://127.0.0.1:8000/attendance/{bus['bus_id']}")
            if res.status_code == 200:
                records = res.json()
                for r in records:
                    r["bus_id"] = bus["bus_id"]
                    r["route"] = bus["route"]
                all_records.extend(records)
        except Exception:
            st.warning(f"⚠️ Could not fetch data for {bus['bus_id']}")

    if not all_records:
        st.info("No attendance data available.")
        st.stop()

    df = pd.DataFrame(all_records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    today = dt.utcnow().date()

    # Calculate fare per passenger based on distance
    fare_per_km = 2.0

    def calculate_fare(row):
        stop_location = stop_coords.get(row["stop_name"])
        if stop_location:
            dist_km = geodesic(
                (row["bus_lat"], row["bus_lon"]),
                stop_location
            ).km
            return dist_km * fare_per_km
        return 0.0

    df["fare"] = df.apply(calculate_fare, axis=1)

    st.markdown("### 📅 Last 7 Days Revenue Overview")

    # Daily revenue
    daily_summary = (
        df.groupby("date")
        .agg(
            passenger_count=("passenger_id", "count"),
            revenue=("fare", "sum")
        )
        .reset_index()
    )

    fig2 = px.bar(
        daily_summary,
        x="date",
        y="revenue",
        labels={"date": "Date", "revenue": "Revenue (₹)"},
        title="💰 Revenue per Day (Last 7 Days)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("### 🚌 Today's Bus-wise Usage")
    today_data = df[df["date"] == today]
    bus_summary = (
        today_data.groupby(["bus_id", "route"])
        .agg(
            passenger_count=("passenger_id", "count"),
            revenue=("fare", "sum")
        )
        .reset_index()
    )

    if bus_summary.empty:
        st.info("No passengers recorded today.")
    else:
        fig3 = px.bar(
            bus_summary,
            x="bus_id",
            y="passenger_count",
            hover_data=["route"],
            labels={"bus_id": "Bus", "passenger_count": "Passengers"},
            title="👥 Passengers per Bus Today"
        )
        st.plotly_chart(fig3, use_container_width=True)

        fig4 = px.bar(
            bus_summary,
            x="bus_id",
            y="revenue",
            hover_data=["route"],
            labels={"bus_id": "Bus", "revenue": "Revenue (₹)"},
            title="💵 Revenue per Bus Today"
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.success(f"**Total Passengers Today:** {bus_summary['passenger_count'].sum()}")        
        st.success(f"**Total Revenue Today:** ₹{bus_summary['revenue'].sum():.2f}")

# ------------------------------
# TNSTC Station Overview Tab
# ------------------------------
with tab4:
    import plotly.graph_objects as go

    st.subheader("🚏 TNSTC Station - Live Passenger Visualization")

    today_data = df[df["date"] == today]

    fig = go.Figure()
    for bus_id in df["bus_id"].unique():
        bus_df = today_data[today_data["bus_id"] == bus_id]
        y_values = [bus_id] * len(bus_df)
        x_values = list(range(1, len(bus_df) + 1))

        fig.add_trace(
            go.Scatter(
                x=x_values,
                y=y_values,
                mode="lines+markers",
                name=f"Bus {bus_id}",
                line=dict(shape="linear"),
                marker=dict(size=10)
            )
        )

    fig.update_layout(
        title="🚌 Buses with Current Passenger Counts (Dots per Passenger)",
        xaxis_title="Passenger Sequence",
        yaxis_title="Bus ID",
        yaxis=dict(type="category"),
        showlegend=True,
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)
    st.info("This chart shows the current passenger counts for each bus. Each dot represents a passenger.")
