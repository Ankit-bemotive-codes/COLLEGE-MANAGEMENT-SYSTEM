# College Management System

A Django + MySQL college management system with role-based access
(Admin / Teacher / Student), department-based student & subject
organization, attendance tracking, exam results and report cards, and
fee invoicing with **Razorpay** payment integration (including
signature-verified webhooks).

## Tech stack

- Django 5.x
- MySQL (via `mysqlclient`)
- Razorpay Checkout.js + Razorpay Python SDK
- Server-rendered templates (no frontend framework)

## Features

- **Accounts** — custom `User` model with `admin` / `teacher` / `student`
  roles, role-based view access via a `@role_required` decorator.
- **Academics** — Departments (e.g. Computer Science, Mechanical), Subjects
  per department/semester, teacher/student profiles, daily attendance
  marking and per-student attendance percentage.
- **Exams** — exams per department/semester, per-subject marks entry,
  auto-generated report cards with grade calculation.
- **Fees** — fee structures per department/semester, bulk invoice
  generation via a management command, Razorpay Checkout integration,
  **webhook-verified** payment confirmation (the source of truth — not
  just the browser redirect), auto-emailed receipts.
- **Dashboard** — role-specific landing pages with aggregate stats (fee
  collection rate, attendance %, etc.).

## Project structure

```
college_management/
├── config/          # settings, root urls
├── accounts/         # custom User model, auth, role decorator
├── academics/        # Department, Subject, TeacherProfile, StudentProfile, Attendance
├── exams/             # exams, results, report cards
├── fees/              # invoices, Razorpay integration, webhooks
├── dashboard/         # role-based dashboards
├── templates/         # shared base.html + navbar
└── static/css/        # styles.css
```

## Data model note

There's no "Class + Section" split like a school — a college is organized
by **Department**. A student and a subject each belong to one
`Department`, with a `semester` field (1-8) for organizing progress
within it. `TeacherProfile` can optionally belong to a department too,
and a department can have a `head_of_department`.

## Setup

### 1. Clone and create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create the MySQL database

```sql
CREATE DATABASE college_management CHARACTER SET utf8mb4;
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials and a real `SECRET_KEY`. You can
generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### 4. Get Razorpay test keys

Sign up at razorpay.com, switch to **Test Mode**, and grab your Key ID /
Key Secret from Settings -> API Keys. Put them in `.env` as
`RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`.

For the webhook secret: in the Razorpay dashboard go to
Settings -> Webhooks -> Add New Webhook, point it at
`https://<your-domain>/fees/webhook/razorpay/`, subscribe to
`payment.captured` and `payment.failed`, and copy the secret it gives you
into `RAZORPAY_WEBHOOK_SECRET`. (For local testing, use a tool like
`ngrok` to expose your dev server so Razorpay can reach the webhook URL.)

### 5. Migrate and create a superuser

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Run the server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` and log in with your superuser - set
its `role` to `admin` there (the createsuperuser command doesn't ask for
custom fields). From there:

1. Add `Department` and `Subject` records.
2. Create teacher/student login accounts via **Accounts -> Create User**
   in the app (or Django admin), then link each to a `TeacherProfile` /
   `StudentProfile` in the Django admin.
3. Add a `FeeStructure` for a department/semester, then generate invoices:
   ```bash
   python manage.py generate_invoices <fee_structure_id>
   ```

## Testing payments

Razorpay's test mode accepts card `4111 1111 1111 1111`, any future
expiry date, any CVV, and any name. No real money moves.

## What to highlight in an interview

- The **webhook handler** (`fees/views.py::razorpay_webhook`) is the
  real source of truth for payment status - the browser redirect
  (`payment_success`) is just UX. Both paths independently verify the
  Razorpay signature before trusting anything.
- `fees/gateway.py` isolates all Razorpay SDK calls behind a small
  interface, so swapping payment providers later only touches one file.
- Role-based access is enforced at the view layer via a reusable
  `@role_required(...)` decorator, not scattered `if` checks.
- The data model deliberately maps to how a college is actually
  organized (Department, not Class/Section), rather than reusing a
  school-shaped schema.

## Next steps / possible extensions

- REST API layer with Django REST Framework for a future mobile app
- Automated recurring invoice generation (cron / Celery)
- Bulk CSV import for student rosters
- PDF report cards and receipts (e.g. via WeasyPrint)
