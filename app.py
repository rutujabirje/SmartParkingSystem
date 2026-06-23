from flask import Flask, render_template, request, redirect, url_for
import time
import random

app = Flask(__name__)

# Core Shared Data State Simulating IoT Parking Sensors
TOTAL_SPOTS = 12
PARKING_SPOTS = {i: {"status": "Available", "car_no": None, "entry_time": None} for i in range(1, TOTAL_SPOTS + 1)}

# Populate initial random traffic data simulation
for i in range(1, 6):
    PARKING_SPOTS[i] = {
        "status": "Occupied",
        "car_no": f"MH-12-AB-{random.randint(1000, 9999)}",
        "entry_time": time.time() - random.randint(600, 3600)
    }

@app.route('/')
def dashboard():
    occ = sum(1 for spot in PARKING_SPOTS.values() if spot["status"] == "Occupied")
    avail = TOTAL_SPOTS - occ
    msg = request.args.get('msg', '')
    # Flask looks inside the /templates folder for index.html automatically
    return render_template('index.html', spots=PARKING_SPOTS, occ=occ, avail=avail, msg=msg)

@app.route('/park', methods=['POST'])
def park_vehicle():
    car_no = request.form.get('car_no', '').strip().upper()
    allocated_spot = None
    
    for spot_id, data in PARKING_SPOTS.items():
        if data["status"] == "Available":
            allocated_spot = spot_id
            break

    if allocated_spot:
        PARKING_SPOTS[allocated_spot] = {"status": "Occupied", "car_no": car_no, "entry_time": time.time()}
        return redirect(url_for('dashboard', msg=f"Success: Vehicle checked into Bay {allocated_spot:02d}"))
    return redirect(url_for('dashboard', msg="Error: Parking structure is completely full!"))

@app.route('/checkout', methods=['POST'])
def checkout_vehicle():
    spot_id = int(request.form.get('spot_id', 0))
    if spot_id in PARKING_SPOTS and PARKING_SPOTS[spot_id]["status"] == "Occupied":
        spot_data = PARKING_SPOTS[spot_id]
        duration = int(time.time() - spot_data["entry_time"])
        fare = 10.00 + (duration * 0.05)
        
        # Clear out structural memory data back to the empty state pool
        PARKING_SPOTS[spot_id] = {"status": "Available", "car_no": None, "entry_time": None}
        return redirect(url_for('dashboard', msg=f"Invoice generated for {spot_data['car_no']}: Duration: {duration} mins, Total Bill: ${fare:.2f}. Bay {spot_id:02d} is now vacant."))
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
