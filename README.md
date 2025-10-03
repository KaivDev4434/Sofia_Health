# Sofia Health - Healthcare Appointment Booking System

A minimal Django-based healthcare appointment booking platform with Stripe payment integration. Built as an MVP for a healthcare SaaS startup.

## 🎯 Features

- **Appointment Booking**: Simple form-based appointment creation
- **Payment Integration**: Stripe PaymentIntent integration (test mode)
- **Admin Dashboard**: Full Django admin interface for managing appointments
- **Responsive Design**: Mobile-friendly Bootstrap 5 interface
- **Healthcare Context**: Built with healthcare providers in mind

## 🏥 Business Model

**Target Users**: Healthcare providers (doctors, therapists, specialists, clinics)  
**End Users**: Patients booking appointments  
**Platform**: SaaS for appointment management and payment processing

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Stripe test account (free at [stripe.com](https://stripe.com))

### Installation

1. **Clone or navigate to the project directory**

```bash
cd "/Users/kaivalya/Desktop/1.Projects/Sofia Health assesment"
```

2. **Create and activate virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:

```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Stripe Settings (Get these from https://dashboard.stripe.com/test/apikeys)
STRIPE_PUBLISHABLE_KEY=pk_test_your_key_here
STRIPE_SECRET_KEY=sk_test_your_key_here

# Payment Amount (in cents)
APPOINTMENT_PRICE=5000
```

5. **Run migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser (for admin access)**

```bash
python manage.py createsuperuser
```

7. **Run the development server**

```bash
python manage.py runserver
```

8. **Access the application**

- Main app: http://127.0.0.1:8000/appointments/
- Admin panel: http://127.0.0.1:8000/admin/

## 🧪 Testing

### Stripe Test Cards

Use these test card numbers for payment testing:

- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- **Requires Auth**: `4000 0025 0000 3155`

**Expiry**: Any future date (e.g., 12/25)  
**CVC**: Any 3 digits (e.g., 123)

### Test Flow

1. Navigate to http://127.0.0.1:8000/appointments/create/
2. Fill in the appointment form with:
   - Provider name: "Dr. Sarah Johnson"
   - Future appointment time
   - Valid email address
   - Select appointment type
3. Click "Continue to Payment"
4. Review the mock payment interface
5. Click "Confirm Payment (Test)"
6. View success confirmation page

## 📁 Project Structure

```
sofia_health/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
├── plan.md
├── sofia_health/              # Main project settings
│   ├── settings.py
│   ├── urls.py
│   └── ...
└── appointments/              # Main app
    ├── models.py              # Appointment model
    ├── forms.py               # Appointment form
    ├── views.py               # Business logic
    ├── urls.py                # URL routing
    ├── admin.py               # Admin configuration
    └── templates/
        └── appointments/
            ├── base.html
            ├── create.html
            ├── payment.html
            └── success.html
```

## 💾 Database Schema

### Appointment Model

| Field | Type | Description |
|-------|------|-------------|
| `provider_name` | CharField | Healthcare provider name |
| `appointment_time` | DateTimeField | Scheduled date/time |
| `client_email` | EmailField | Patient's email |
| `is_paid` | BooleanField | Payment status |
| `amount_paid` | DecimalField | Payment amount |
| `stripe_payment_intent_id` | CharField | Stripe transaction ID |
| `appointment_type` | CharField | consultation/follow_up |
| `notes` | TextField | Patient notes |
| `created_at` | DateTimeField | Record creation time |
| `updated_at` | DateTimeField | Last update time |

## 🔒 Security Features

- CSRF protection (Django built-in)
- SQL injection protection (Django ORM)
- Environment variable configuration
- Input validation on all forms
- HTTPS ready for production

## 🎨 Tech Stack

- **Backend**: Django 5.0+
- **Database**: SQLite (development) - easily switch to PostgreSQL
- **Payment**: Stripe API
- **Frontend**: Bootstrap 5, HTML5
- **Environment**: python-decouple

## 📋 API Endpoints

| URL | Method | Description |
|-----|--------|-------------|
| `/appointments/` | GET | Redirects to create form |
| `/appointments/create/` | GET, POST | Create appointment form |
| `/appointments/<id>/payment/` | GET | Payment page |
| `/appointments/<id>/confirm-payment/` | POST | Confirm payment |
| `/appointments/<id>/success/` | GET | Success confirmation |
| `/admin/` | GET | Admin dashboard |

## 🛠️ Admin Interface

Access the admin panel at http://127.0.0.1:8000/admin/

**Features**:
- View all appointments
- Filter by payment status, appointment type, date
- Search by provider name or client email
- Edit appointment details
- View payment information

## 📧 Email Configuration

Currently configured to use console backend (emails print to terminal).

To use real emails in production:
1. Update `EMAIL_BACKEND` in settings.py
2. Configure SMTP settings or use services like SendGrid/AWS SES

## 🚀 Deployment

### Quick Deploy Options

**Heroku**:
```bash
heroku create sofia-health
heroku config:set SECRET_KEY=your-secret
heroku config:set STRIPE_SECRET_KEY=sk_test_xxx
git push heroku main
```

**Railway**:
- Connect GitHub repository
- Set environment variables
- Deploy automatically

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Update `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set up HTTPS/SSL
- [ ] Configure real email backend
- [ ] Set up Stripe webhooks
- [ ] Enable proper logging
- [ ] Configure static files serving

## 🔮 Future Enhancements

See `plan.md` for detailed scaling roadmap including:

- Multi-provider platform
- Provider dashboards
- Patient portal
- HIPAA compliance
- Telehealth integration
- EHR/EMR integration
- Advanced scheduling
- Mobile applications

## 📝 License

This is an MVP project for evaluation purposes.

## 👥 Support

For questions or issues:
- Email: support@sofiahealth.com
- Review the `plan.md` for product roadmap

## 🧑‍💻 Development

### Running Tests
```bash
python manage.py test
```

### Making Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Creating Sample Data
Use Django admin or shell:
```bash
python manage.py shell
```

---

**Built with ❤️ for healthcare providers**

