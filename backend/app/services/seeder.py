import random
from typing import List, Dict, Any

SEED_SHUTTLES = [
    {
        "id": "SHUTTLE_1",
        "name": "Express Shuttle Alpha (S1)",
        "seat_capacity": 12,
        "start_location_name": "Silk Board Transit Hub",
        "start_lat": 12.9176,
        "start_lng": 77.6234,
        "status": "active"
    },
    {
        "id": "SHUTTLE_2",
        "name": "City Cruiser Beta (S2)",
        "seat_capacity": 14,
        "start_location_name": "BTM Depot Circle",
        "start_lat": 12.9140,
        "start_lng": 77.6100,
        "status": "active"
    },
    {
        "id": "SHUTTLE_3",
        "name": "Metro Shuttle Gamma (S3)",
        "seat_capacity": 12,
        "start_location_name": "Indiranagar Hub Depot",
        "start_lat": 12.9719,
        "start_lng": 77.6412,
        "status": "active"
    },
    {
        "id": "SHUTTLE_4",
        "name": "Tech Corridor Delta (S4)",
        "seat_capacity": 14,
        "start_location_name": "Whitefield Transit Center",
        "start_lat": 12.9815,
        "start_lng": 77.7289,
        "status": "active"
    },
    {
        "id": "SHUTTLE_5",
        "name": "Eco Transit Epsilon (S5)",
        "seat_capacity": 10,
        "start_location_name": "Electronic City Phase 1",
        "start_lat": 12.8450,
        "start_lng": 77.6650,
        "status": "active"
    }
]

NEIGHBORHOOD_CENTERS = [
    {"name": "HSR Layout Sector 1 & 2", "lat": 12.9121, "lng": 77.6446, "count": 12},
    {"name": "BTM Layout 2nd Stage", "lat": 12.9140, "lng": 77.6100, "count": 10},
    {"name": "Koramangala 4th Block", "lat": 12.9345, "lng": 77.6265, "count": 10},
    {"name": "Indiranagar 100ft Road", "lat": 12.9719, "lng": 77.6412, "count": 8},
    {"name": "Kadubeesanahalli / Bellandur", "lat": 12.9370, "lng": 77.6930, "count": 6},
    {"name": "Jayanagar 4th Block", "lat": 12.9290, "lng": 77.5830, "count": 4}
]

FIRST_NAMES = [
    "Aarav", "Aditi", "Rohan", "Priya", "Vikram", "Sneha", "Rahul", "Ananya", "Karthik", "Pooja",
    "Siddharth", "Neha", "Arjun", "Divya", "Varun", "Tanvi", "Gautam", "Isha", "Manish", "Riya",
    "Abhishek", "Meera", "Deepak", "Swati", "Suresh", "Kavita", "Nikhil", "Shreya", "Pranav", "Nandini",
    "Akash", "Anushka", "Harish", "Preeti", "Rajesh", "Simran", "Vikas", "Tara", "Sameer", "Geeta",
    "Kunal", "Alok", "Sunita", "Tarun", "Bhavna", "Hemant", "Ritu", "Mohit", "Shweta", "Sachin"
]

def generate_benchmark_50_dataset() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generates reproducible 50 employee pickup requests and 5 active shuttles."""
    random.seed(42) # Fixed seed for reproducible scientific evaluation
    
    requests = []
    emp_idx = 0

    for hood in NEIGHBORHOOD_CENTERS:
        for _ in range(hood["count"]):
            emp_name = f"{FIRST_NAMES[emp_idx % len(FIRST_NAMES)]} {chr(65 + (emp_idx % 26))}."
            # Jitter by ~50 to 200 meters (0.0005 to 0.002 degrees)
            jitter_lat = hood["lat"] + random.uniform(-0.0018, 0.0018)
            jitter_lng = hood["lng"] + random.uniform(-0.0018, 0.0018)

            requests.append({
                "id": f"REQ_{emp_idx + 1:03d}",
                "user_id": f"USER_{emp_idx + 1:03d}",
                "employee_name": emp_name,
                "pickup_lat": round(jitter_lat, 6),
                "pickup_lng": round(jitter_lng, 6),
                "pickup_location_name": f"{hood['name']} Area",
                "destination": "Central Tech Park Campus",
                "dest_lat": 12.9716,
                "dest_lng": 77.5946,
                "arrival_deadline": "09:00:00",
                "status": "pending"
            })
            emp_idx += 1

    return SEED_SHUTTLES, requests
