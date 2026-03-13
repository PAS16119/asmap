# ASMaP — Adombra School Management & Payment System
### v1.0 | Smart School Monitoring for Better Education

---

## WHAT IS ASMaP?

ASMaP is a web-based school management platform focused on:

- **Class Payment Management** — collect, confirm and report student payments by purpose and class
- **Teacher Monitoring** — record teacher attendance with session type (Normal/Extended), time-in, and punctuality tracking
- **Teacher Evaluation** — compare Normal vs Extended teaching sessions for remuneration analysis
- **Academic Year Management** — reusable every year; historical data never deleted
- **Role-Based Access** — Admin, Coordinator, Supervisor

---

## SYSTEM REQUIREMENTS

### Backend (Python)
- Python 3.11+
- pip
- SQLite (local development) — no setup needed
- PostgreSQL (production) — free tier available on Render

### Frontend (HTML)
- Any web server or static hosting (Netlify, Vercel, GitHub Pages)
- Modern web browser (Chrome, Firefox, Edge, Safari)

---

## FILE STRUCTURE

```
asmap/
├── backend/
│   ├── app.py              ← Flask application factory
│   ├── config.py           ← Dev/Production config
│   ├── models.py           ← Database models
│   ├── requirements.txt    ← Python dependencies
│   ├── render.yaml         ← Render.com deployment config
│   ├── Procfile            ← Railway/Heroku config
│   ├── runtime.txt         ← Python version
│   ├── .env.example        ← Environment variable template
│   └── routes/
│       ├── auth.py         ← Login, profile, change password
│       ├── admin.py        ← Admin endpoints (all management)
│       ├── coordinator.py  ← Payment recording (coordinator)
│       └── supervisor.py   ← Monitoring recording (supervisor)
│
└── frontend/
    ├── login.html          ← Login page (all roles)
    ├── admin.html          ← Admin dashboard
    ├── coordinator.html    ← Coordinator dashboard
    ├── supervisor.html     ← Supervisor dashboard
    ├── netlify.toml        ← Netlify deployment config
    └── assets/
        ├── style.css       ← Design system
        └── api.js          ← Shared JS utilities
```

---

## QUICK START — LOCAL DEVELOPMENT

### Step 1: Set Up the Backend

Open a terminal. Navigate to the backend folder:

```bash
cd asmap/backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment:

```bash
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

Open `.env` in a text editor. For local testing, the defaults work fine — no changes needed.

### Step 2: Initialize the Database

This creates all tables and seeds:
- Default admin account
- All 46 subjects for Oguaa SHS Tech (editable)
- Default school settings

```bash
flask --app app init-db
```

You will see:
```
✓ Tables created
✓ Default admin → username: admin | password: Admin@1234
✓ Subjects: 46 new, 0 already existed
✓ Default school settings created

✅ ASMaP database initialized successfully
   ⚠  Change the admin password after first login!
```

### Step 3: Run the Backend

```bash
flask --app app run
```

The backend is now running at: **http://localhost:5000**

Test it: open http://localhost:5000/api/health — you should see `{"status":"ok","system":"ASMaP"}`

### Step 4: Open the Frontend

Open `asmap/frontend/login.html` in your web browser.

Log in with:
- **Username:** `admin`
- **Password:** `Admin@1234`

> ⚠️ **Change the admin password immediately after first login!**

---

## FIRST-TIME SETUP CHECKLIST

After logging in as admin, complete these steps in order:

### 1. Set School Information
Go to **Settings → School Identity**
- Enter your school's full name, short name, and motto
- Upload your school crest/logo (PNG recommended)

### 2. Set Session Times
Go to **Settings → Session Times**
- Set the normal class start time (e.g. 07:30)
- Set the extended teaching start time (e.g. 15:30)
These times are used to automatically determine if a teacher is on time or late.

### 3. Create Academic Year
Go to **Settings → Academic Year**
- Click "Create New Year" and enter e.g. `2025/2026`
- Click "Set Active" on the new year
All data will now be linked to this year.

### 4. Add Classes
Go to **System Setup → Classes**
Add all your school classes, e.g.:
- SHS1A, SHS1B, SHS1C
- SHS2A, SHS2B, SHS2C
- SHS3A, SHS3B, SHS3C

### 5. Add Teachers
Go to **System Setup → Teachers**
Add each teacher with their main subject (selected from dropdown).

### 6. Verify Subjects
Go to **System Setup → Subjects**
All 46 subjects are pre-loaded. Add or delete as needed for your school.

### 7. Add Users
Go to **Users → New User**
Create coordinator and supervisor accounts.

### 8. Assign Coordinators to Classes
Go to **System Setup → Coordinator Assignments**
Assign each coordinator to their class(es).

### 9. Import Students
Go to **Students → Import**
Download the template, fill it in, and upload.
Columns required: Student Name | Class

---

## USER ROLES

| Role        | What They Can Do |
|-------------|-----------------|
| **Admin**   | Full access — manage everything, confirm payments, view all reports, teacher evaluation, school settings |
| **Coordinator** | Record payments for their assigned classes. View payment history. Cannot see other classes. |
| **Supervisor** | Record class monitoring (teacher attendance, session type, time-in). View own records and teacher summary. |

---

## TEACHER MONITORING — KEY CONCEPTS

### Session Types
- **Normal** — Regular class periods during the school day
- **Extended** — Extra/evening teaching sessions (these are what extended teaching fees cover)

### Punctuality Tracking
When a supervisor records monitoring, they enter the teacher's **Time In**. The system automatically compares this against the configured session start time and marks the teacher as:
- ✓ **On time** — arrived at or before the start time
- ✗ **Late** — arrived after the start time
- **—** — time not recorded

### Teacher Evaluation Report (Admin)
Admin can view a side-by-side comparison per teacher:
- Normal sessions: total, on-time count, late count
- Extended sessions: total, on-time count, late count
- Grand total

This powers remuneration decisions — you can clearly see which teachers did extended teaching and whether they were punctual.

---

## PAYMENT PURPOSES

The four standard payment categories:
1. **Extended Teaching Fees** — Payment for extra classes
2. **Teacher Motivation Levy** — Teacher welfare contributions
3. **Project Levy** — School project contributions
4. **Others** — Miscellaneous

### Confirmation Workflow
1. **Coordinator** records a payment → status is "Pending"
2. **Admin** confirms it → status becomes "Confirmed"
3. Admin can also record payments directly (auto-confirmed)

---

## PRODUCTION DEPLOYMENT

### Backend → Render.com (Free)

**Step 1:** Create a free account at https://render.com

**Step 2:** Create a new **Web Service**
- Connect your GitHub repository (push the backend folder)
- Or use "Deploy from Repository"

**Step 3:** Configure:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn "app:create_app('production')" --bind 0.0.0.0:$PORT --workers 2`
- **Environment:** Python 3.11

**Step 4:** Add Environment Variables in Render dashboard:
```
FLASK_ENV = production
SECRET_KEY = (click "Generate" for a random value)
JWT_SECRET_KEY = (click "Generate" for another random value)
DATABASE_URL = (Render provides this automatically if you add a PostgreSQL database)
```

**Step 5:** Add a PostgreSQL database
- In Render dashboard → New → PostgreSQL → Free plan
- Render will automatically set DATABASE_URL in your web service

**Step 6:** After first deploy, run the init command
In Render Shell or via a one-off job:
```bash
flask --app app init-db
```

**Your backend URL will be:** `https://asmap-backend.onrender.com`

---

### Frontend → Netlify (Free)

**Step 1:** Create a free account at https://netlify.com

**Step 2:** Drag and drop the `frontend/` folder onto the Netlify deploy area

OR connect your GitHub repository.

**Step 3:** Update the API URL
Open `frontend/assets/api.js` and change:
```javascript
const API_BASE = window.API_BASE || 'http://localhost:5000/api';
```
To:
```javascript
const API_BASE = window.API_BASE || 'https://your-asmap-backend.onrender.com/api';
```
Replace `your-asmap-backend` with your actual Render URL.

**Step 4:** Redeploy the frontend

**Your frontend URL will be:** `https://asmap-school.netlify.app`

---

### Alternative: Run Everything on One VPS (Advanced)

If you have a Linux server (Ubuntu), you can run both frontend and backend together:

```bash
# Install dependencies
sudo apt update && sudo apt install python3-pip nginx

# Backend
cd asmap/backend
pip install -r requirements.txt
flask --app app init-db

# Run with gunicorn as a service
# (Create /etc/systemd/system/asmap.service)

# Serve frontend with nginx
# Point nginx to the frontend/ folder
# Proxy /api/ to gunicorn on port 5000
```

---

## STARTING A NEW ACADEMIC YEAR

**Do NOT delete old data.** Instead:

1. Go to Admin → **Settings → Academic Year**
2. Click "Create New Year" — enter e.g. `2026/2027`
3. Click "Set Active"
4. Import students for the new year (or add manually)
5. All old data remains accessible by changing the year filter

---

## API REFERENCE (for developers)

### Authentication
```
POST /api/auth/login          { username, password }  → { access_token, user }
GET  /api/auth/profile        (JWT required)
POST /api/auth/change-password { current_password, new_password }
```

### Admin — Settings
```
GET  /api/admin/settings/public    (public — no auth)
GET  /api/admin/settings           (admin)
PUT  /api/admin/settings           (admin)
POST /api/admin/settings/logo      (admin, multipart)
```

### Admin — Academic Years
```
GET  /api/admin/years
GET  /api/admin/years/active
POST /api/admin/years              { label }
POST /api/admin/years/:id/activate
```

### Admin — Data
```
GET/POST /api/admin/teachers
GET/POST /api/admin/subjects
GET/POST /api/admin/classes
GET/POST /api/admin/students
POST     /api/admin/students/import    (multipart Excel)
GET      /api/admin/students/template  (Excel download)
GET      /api/admin/students/export    (Excel download)
```

### Admin — Payments
```
GET  /api/admin/payments               ?year_id&class_id&confirmed
POST /api/admin/payments               { student_id, amount, purpose }
POST /api/admin/payments/:id/confirm
GET  /api/admin/payments/student/:id   ?year_id
```

### Admin — Reports
```
GET /api/admin/dashboard              ?year_id
GET /api/admin/reports/payments       ?year_id
GET /api/admin/reports/payments/export  (Excel)
GET /api/admin/reports/teachers       ?year_id  ← evaluation
GET /api/admin/monitoring             ?year_id&teacher_id&class_id&session_type
GET /api/admin/monitoring/teacher-summary  ?year_id
```

### Coordinator
```
GET  /api/coordinator/classes
GET  /api/coordinator/students/:class_id
POST /api/coordinator/payments
GET  /api/coordinator/payments         ?class_id
GET  /api/coordinator/payments/student/:id
```

### Supervisor
```
POST   /api/supervisor/monitoring      { teacher_id, subject_id, class_id, attendance_date, students_present, session_type, time_in, period, notes }
GET    /api/supervisor/monitoring      ?date_from&date_to&session_type
PUT    /api/supervisor/monitoring/:id
DELETE /api/supervisor/monitoring/:id
GET    /api/supervisor/teacher-summary  ?year_id
```

---

## TROUBLESHOOTING

### "CORS error" in browser
- Make sure the backend is running
- Check that `API_BASE` in `api.js` matches your backend URL exactly (no trailing slash)

### "Internal Server Error" on first start
- Run `flask --app app init-db` first
- Check that all dependencies are installed: `pip install -r requirements.txt`

### Login fails with correct credentials
- Confirm the database was initialized: `flask --app app init-db`
- Default credentials: `admin` / `Admin@1234`

### Students not showing after import
- Ensure an academic year is active (Admin → Settings → Academic Year → Set Active)
- Check the Excel has exactly two columns: Student Name, Class

### Teachers not found in supervisor search
- Admin must first add teachers in **System Setup → Teachers**

### Backend works but frontend shows blank
- Check browser console for errors (F12)
- Verify `API_BASE` URL in `assets/api.js`
- Make sure the backend CORS allows your frontend domain

---

## SECURITY NOTES

- All passwords are hashed with bcrypt — never stored in plain text
- JWT tokens expire after 12 hours
- Coordinators can only see their assigned classes — enforced server-side
- Admin-only routes are enforced at the API level (not just frontend)
- Upload size limit: 5MB for data files, 2MB for logos
- Change the default admin password immediately after first login

---

## FUTURE ROADMAP (v2)

- Individual student attendance tracking
- SMS/WhatsApp notifications for parents
- WAEC results integration
- Full financial accounting module
- Android mobile app
- Automated Excel/PDF report scheduling
- Multi-campus support

---

## CREDITS

**ASMaP — Adombra School Management & Payment System**  
Built for Oguaa Senior High Technical School  
"Vision and Victory"

*Smart School Monitoring for Better Education*
