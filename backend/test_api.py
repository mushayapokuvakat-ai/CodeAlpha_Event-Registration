import json
import urllib.request
import urllib.error
import random
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"

def send_request(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req_data = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=req_data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8")), response.status
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        return json.loads(error_body) if error_body else {"error": e.reason}, e.code

print("Starting test data seeding")

# 1. Create Organizer
org_data = {
    "username": "tech_conference_admin",
    "email": "admin.techcon@test.com",
    "password": "AdminPass#2026",
    "password_confirm": "AdminPass#2026",
    "role": "ORGANIZER"
}
send_request("/api/auth/register/", "POST", org_data)
res, _ = send_request("/api/auth/login/", "POST", {"email": "admin.techcon@test.com", "password": "AdminPass#2026"})
org_token = res["tokens"]["access"]
print("Organizer account created and authenticated")

# 2. Create 10 Events
event_templates = [
    ("PyData Global Conference 2026", "Data science and machine learning with Python", "Software Development"),
    ("Vue.js Live Summit", "Modern frontend development with Vue 3", "Software Development"),
    ("DevSecOps Workshop", "Security integration in CI/CD pipelines", "Software Development"),
    ("Go Lang Performance Bootcamp", "High performance backend development with Go", "Software Development"),
    ("Industrial Robotics Expo", "Automation and industrial robot programming", "Robotics"),
    ("Autonomous Vehicle Systems Conference", "Self driving car software and sensors", "Robotics"),
    ("Robotics Education Forum", "Teaching robotics in schools and universities", "Robotics"),
    ("CleanTech Innovation Summit", "Sustainable technology and green startups", "Innovation"),
    ("Fintech Disruption Forum", "Blockchain and digital finance solutions", "Innovation"),
    ("HealthTech Innovation Lab", "Digital health and medical device software", "Innovation")
]

event_ids = []
base_date = datetime.now() + timedelta(days=21)

for i, (name, desc, category) in enumerate(event_templates):
    event_date = (base_date + timedelta(days=i*2)).strftime("%Y-%m-%dT18:00:00Z")
    event_data = {
        "name": name,
        "description": f"{desc} | Category: {category}",
        "date": event_date,
        "location": "Cape Town International Convention Centre",
        "capacity": 200
    }
    res, code = send_request("/api/events/create/", "POST", event_data, org_token)
    event_ids.append(res["id"])
    print(f"Event {i+1} created: {name} with status code {code}")

# 3. Create 40 Users
first_names = ["Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Jamie", "Avery",
               "Cameron", "Blake", "Drew", "Logan", "Skyler", "Reese", "Rowan", "Quinn",
               "Elliot", "Finley", "Parker", "Sage", "Hayden", "River", "Emerson", "Dakota",
               "Charlie", "Remy", "Spencer", "Ashton", "Dylan", "Kendall", "Peyton", "Reagan",
               "Sawyer", "Wren", "Arden", "Callum", "Griffin", "Nolan", "Silas", "Theo"]

last_names = ["Adams", "Baker", "Clark", "Evans", "Foster", "Green", "Hill", "King",
              "Lee", "Lewis", "Mitchell", "Nelson", "Parker", "Roberts", "Scott", "Turner",
              "Walker", "White", "Wood", "Young"]

users = []

for i in range(40):
    fname = first_names[i]
    lname = last_names[i % len(last_names)]
    username = f"{fname.lower()}_{lname.lower()}_{i+100}"
    email = f"{username}@examplemail.com"

    user_data = {
        "username": username,
        "email": email,
        "password": "UserPass#2026",
        "password_confirm": "UserPass#2026",
        "role": "USER"
    }
    send_request("/api/auth/register/", "POST", user_data)

    res, _ = send_request("/api/auth/login/", "POST", {"email": email, "password": "UserPass#2026"})
    users.append({"token": res["tokens"]["access"], "email": email, "username": username})

    if (i+1) % 10 == 0:
        print(f"Created {i+1} user accounts")

print("All 40 user accounts created and authenticated")

# 4. Register users for events randomly
print("Registering users for events")
registration_data = []

for user in users:
    num_events = random.randint(1, 4)
    chosen_events = random.sample(event_ids, num_events)

    for event_id in chosen_events:
        res, code = send_request("/api/registrations/register/", "POST",
                                 {"event_id": event_id}, user["token"])
        if code in [200, 201]:
            registration_data.append({
                "reg_id": res["registration_id"],
                "token": user["token"],
                "email": user["email"],
                "username": user["username"]
            })

print(f"Total registrations created: {len(registration_data)}")

# 5. Cancel 25% of registrations randomly
cancel_count = int(len(registration_data) * 0.25)
to_cancel = random.sample(registration_data, cancel_count)

print(f"Cancelling {cancel_count} registrations")
cancelled = 0
for reg in to_cancel:
    res, code = send_request(f"/api/registrations/{reg['reg_id']}/cancel/", "DELETE", token=reg["token"])
    if code in [200, 204]:
        cancelled += 1
        print(f"Cancelled registration {reg['reg_id']} for user {reg['username']} with status code {code}")

# 6. Verify active registrations for a sample user
res, code = send_request("/api/registrations/my/", "GET", token=users[0]["token"])
print(f"Verification: User {users[0]['username']} has {len(res)} active registrations. Status code {code}")

print(f"Seeding complete. Events: 10, Users: 40, Registrations: {len(registration_data)}, Cancelled: {cancelled}")
print("Check Django admin at http://localhost:8000/admin/ to verify data")
