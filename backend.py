from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

# ========================
# Preloaded bus data
# ========================
buses = [
    {
        "bus_id": "BUS001",
        "route": "Nagercoil - Kanyakumari",
        "departure": "09:00",
        "arrival": "11:00",
        "current_lat": 8.1798,
        "current_lon": 77.4324,
        "status": "On Time",
        "stops": ["Kottar", "Suchindram", "Vadasery", "Kulasekaram", "Kanyakumari"]
    },
    {
        "bus_id": "BUS002",
        "route": "Nagercoil - Tirunelveli",
        "departure": "10:00",
        "arrival": "12:30",
        "current_lat": 8.1711,
        "current_lon": 77.4280,
        "status": "On Time",
        "stops": ["Nagercoil", "Aralvaimozhi", "Boothapandi", "Tirunelveli Junction", "Tirunelveli Bus Stand"]
    },
    {
        "bus_id": "BUS003",
        "route": "Nagercoil - Thuckalay",
        "departure": "08:30",
        "arrival": "09:30",
        "current_lat": 8.1780,
        "current_lon": 77.4500,
        "status": "On Time",
        "stops": ["Kottar", "Vadasery", "Asaripallam", "Marthandam", "Thuckalay"]
    },
    {
        "bus_id": "BUS004",
        "route": "Nagercoil - Colachel",
        "departure": "09:15",
        "arrival": "10:45",
        "current_lat": 8.1805,
        "current_lon": 77.4390,
        "status": "On Time",
        "stops": ["Nagercoil", "Kurunthancode", "Muttom", "Colachel Junction", "Colachel"]
    },
    {
        "bus_id": "BUS005",
        "route": "Nagercoil - Padmanabhapuram",
        "departure": "07:45",
        "arrival": "09:00",
        "current_lat": 8.1770,
        "current_lon": 77.4350,
        "status": "On Time",
        "stops": ["Nagercoil", "Vetturnimadam", "Kuzhithurai", "Thiruvattar", "Padmanabhapuram"]
    },
    {
        "bus_id": "BUS006",
        "route": "Nagercoil - Parvathipuram",
        "departure": "10:00",
        "arrival": "11:15",
        "current_lat": 8.1760,
        "current_lon": 77.4380,
        "status": "On Time",
        "stops": ["Nagercoil", "Vadasery", "Parvathipuram", "Erumbukadu", "Suchindram"]
    },
    {
        "bus_id": "BUS007",
        "route": "Nagercoil - Marthandam",
        "departure": "11:00",
        "arrival": "12:30",
        "current_lat": 8.1785,
        "current_lon": 77.4310,
        "status": "On Time",
        "stops": ["Nagercoil", "Thovalai", "Kulasekaram", "Marthandam Bus Stand", "Marthandam"]
    },
    {
        "bus_id": "BUS008",
        "route": "Nagercoil - Kuzhithurai",
        "departure": "07:00",
        "arrival": "08:00",
        "current_lat": 8.1790,
        "current_lon": 77.4360,
        "status": "On Time",
        "stops": ["Nagercoil", "Eathamozhi", "Kuzhithurai", "Marthandam", "Thuckalay"]
    },
    {
        "bus_id": "BUS009",
        "route": "Nagercoil - Eraniel",
        "departure": "08:45",
        "arrival": "10:00",
        "current_lat": 8.1750,
        "current_lon": 77.4320,
        "status": "On Time",
        "stops": ["Nagercoil", "Asaripallam", "Thingal Nagar", "Eraniel Junction", "Eraniel"]
    },
    {
        "bus_id": "BUS010",
        "route": "Nagercoil - Puthalam",
        "departure": "06:30",
        "arrival": "07:45",
        "current_lat": 8.1740,
        "current_lon": 77.4330,
        "status": "On Time",
        "stops": ["Nagercoil", "Meenakshipuram", "Puthalam", "Suchindram", "Kanyakumari"]
    }
]

# ========================
# Attendance records
# ========================
attendance = []

# ========================
# Data Models
# ========================
class AttendanceRecord(BaseModel):
    passenger_id: str
    bus_id: str
    stop_name: str
    gender: str
    timestamp: datetime
    status: str
    bus_lat: float
    bus_lon: float

class LocationUpdate(BaseModel):
    bus_id: str
    current_lat: float
    current_lon: float
    status: str

# ========================
# API Endpoints
# ========================

@app.get("/buses")
def get_buses():
    """
    Return the list of all buses with their details.
    """
    return buses

@app.post("/attendance")
def record_attendance(data: AttendanceRecord):
    """
    Record a new attendance entry.
    """
    attendance.append(data.dict())
    return {"message": "Attendance recorded successfully."}

@app.get("/attendance/{bus_id}")
def get_attendance(bus_id: str):
    """
    Retrieve attendance records for a specific bus.
    """
    bus_records = [r for r in attendance if r["bus_id"] == bus_id]
    return bus_records

@app.post("/update_location")
def update_location(data: LocationUpdate):
    """
    Update the current location and status of a bus.
    """
    for bus in buses:
        if bus["bus_id"] == data.bus_id:
            bus["current_lat"] = data.current_lat
            bus["current_lon"] = data.current_lon
            bus["status"] = data.status
            return {"message": "Location updated successfully."}
    return {"error": "Bus not found."}
@app.get("/")
def root():
    return {"message": "✅ TNSTC API is live and running!"}

