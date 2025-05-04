# file: make_fake_data.py
import random, csv, hashlib
from datetime import datetime, timedelta
from faker import Faker
fake = Faker()

N_LOCATIONS   = 50
N_VEHICLES    = 120
N_PEOPLE      = 2_000
N_PASSENGERS  = 1_600      # subset of people
N_SUPPORT     =   200      # another subset of people
N_RESERV      = 8_000
N_TICKETS     = 10_000
N_PAYMENTS    =  7_500
N_REPORTS     =  1_000
SEAT_COUNT    = 3000

out = open("fake_data.sql", "w", encoding="utf8")
w = out.write

def clean(s):                  # escape single‑quotes
    return s.replace("'", "''")

# ---------- 1. location ----------
for i in range(1, N_LOCATIONS+1):
    title = clean(fake.city())
    w(f"INSERT INTO location (location_id,title) VALUES ({i},'{title}');\n")

# ---------- 2. vehicle & sub‑types ----------
for vid in range(1, N_VEHICLES+1):
    cap = random.randint(40, 300)
    brand = random.choice(['Volvo','MAN','Boeing','Airbus','Bombardier'])
    model = fake.bothify(text='??-###')
    w(f"INSERT INTO vehicle (vehicle_id,capacity,brand,model) VALUES "
      f"({vid},{cap},'{brand}','{model}');\n")
    subtype = random.choice(['bus','plane','train'])
    if subtype == 'bus':
        w(f"INSERT INTO bus (vehicle_id,bus_type,bus_company) VALUES "
          f"({vid},'Coach','{fake.company()}');\n")
    elif subtype == 'plane':
        w(f"INSERT INTO plane (vehicle_id,airline_name,plane_type,flight_number,"
          f"destination_airport,departure_airport) VALUES "
          f"({vid},'{fake.company()}','Jet','{fake.bothify(text='??####')}',"
          f"'{fake.city()}','{fake.city()}');\n")
    else:
        w(f"INSERT INTO train (vehicle_id,train_type,wagon_count,star) VALUES "
          f"({vid},'IC', {random.randint(8,15)}, {random.randint(1,3)});\n")

# ---------- 3. person ----------
for pid in range(1, N_PEOPLE+1):
    fn, ln = clean(fake.first_name()), clean(fake.last_name())
    email   = f"user{pid}@example.com"
    phone   = fake.msisdn()[:15]
    city    = clean(fake.city())
    pwdhash = hashlib.sha256(f"pw{pid}".encode()).hexdigest()
    w(f"INSERT INTO person "
      f"(person_id,first_name,last_name,email,phone_number,city,password_hashed) "
      f"VALUES ({pid},'{fn}','{ln}','{email}','{phone}','{city}','{pwdhash}');\n")

# --- 4. passenger & support (sub‑types) ---
passenger_ids = random.sample(range(1, N_PEOPLE+1), N_PASSENGERS)
support_ids   = random.sample([p for p in range(1, N_PEOPLE+1)
                               if p not in passenger_ids], N_SUPPORT)

for pid in passenger_ids:
    w(f"INSERT INTO passenger (person_id,loyalty_point,passenger_type) "
      f"VALUES ({pid},{random.randint(0,5000)},'NORMAL');\n")

for pid in support_ids:
    w(f"INSERT INTO support (person_id,work_position,staff_number,department) "
      f"VALUES ({pid},'Agent','SUP{pid}','Customer Care');\n")

# ---------- 5. seat ----------
for sid in range(1, SEAT_COUNT + 1):
    unit = f"W{random.randint(1,20)}"
    num  = f"{random.randint(1,60)}"
    w(f"INSERT INTO seat (seat_id,unit_number,seat_number) "
      f"VALUES ({sid},'{unit}','{num}');\n")

# ---------- 6. reservation ----------
for rid in range(1, N_RESERV+1):
    pid = random.choice(passenger_ids)
    status = random.choice(['CONFIRMED','PENDING','CANCELLED'])
    expiry = datetime.utcnow() + timedelta(days=random.randint(-30,30))
    w(f"INSERT INTO reservation (reservation_id,passenger_id,status,expiry_time)"
      f" VALUES ({rid},{pid},'{status}','{expiry:%Y-%m-%d %H:%M:%S}');\n")

# ---------- 7. ticket ----------
for tid in range(1, N_TICKETS+1):
    rid  = random.randint(1, N_RESERV)
    vid  = random.randint(1, N_VEHICLES)
    src  = random.randint(1, N_LOCATIONS)
    dst  = random.randint(1, N_LOCATIONS)
    while dst == src:
        dst = random.randint(1, N_LOCATIONS)
    dep  = datetime.utcnow() + timedelta(days=random.randint(-60,60),
                                         hours=random.randint(0,23))
    arr  = dep + timedelta(hours=random.randint(2,12))
    price = round(random.uniform(9, 399), 2)
    seat  = random.randint(1, SEAT_COUNT)
    w(f"INSERT INTO ticket (ticket_id,reservation_id,vehicle_id,source,destination,"
      f"departure_time,arrival_time,price,seat_id) VALUES "
      f"({tid},{rid},{vid},{src},{dst},"
      f"'{dep:%Y-%m-%d %H:%M:%S}','{arr:%Y-%m-%d %H:%M:%S}',{price},{seat});\n")

# ---------- 8. payment (70‑75 % of tickets) ----------
pay_ticket_ids = random.sample(range(1, N_TICKETS+1), N_PAYMENTS)
for payid, tid in enumerate(pay_ticket_ids, 1):
    rid = f"(SELECT reservation_id FROM ticket WHERE ticket_id={tid})"
    amt = round(random.uniform(10, 500), 2)
    paytime = datetime.utcnow() - timedelta(days=random.randint(0,60))
    ref = fake.uuid4()
    w(f"INSERT INTO payment (payment_id,reservation_id,amount,payment_method,"
      f"payment_time,status,transaction_reference) VALUES "
      f"({payid},{rid},{amt},'CARD','{paytime:%Y-%m-%d %H:%M:%S}',"
      f"'PAID','{ref}');\n")

# ---------- 9. report (optional) ----------
for repid in range(1, N_REPORTS+1):
    pid = random.randint(1, N_PEOPLE)
    typ = random.choice(['COMPLAINT','QUESTION','APP'])
    txt = clean(fake.sentence(nb_words=12))
    w(f"INSERT INTO report (report_id,person_id,report_type,report_text,status)"
      f" VALUES ({repid},{pid},'{typ}','{txt}','OPEN');\n")

out.close()
print("fake_data.sql created!")
