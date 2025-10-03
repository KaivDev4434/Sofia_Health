# Sofia Health - Healthcare Appointment Booking Platform

Django-based healthcare appointment booking system with Stripe payments, email notifications, calendar integration, and provider management. Built as a SaaS MVP for healthcare providers.

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up .env file (copy from env.sample)
cp env.sample .env
# Add your Stripe test keys from https://dashboard.stripe.com/test/apikeys

# 3. Run migrations
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. Start server
python manage.py runserver
```

**Access**: 
- Main App: http://127.0.0.1:8000/appointments/
- Admin Panel: http://127.0.0.1:8000/admin/
- Analytics: http://127.0.0.1:8000/appointments/admin-dashboard/

**Test Payment**: Use card `4242 4242 4242 4242`, any future expiry, any CVC

## ✨ Key Features

### For Patients
- **Provider Selection**: Choose from active healthcare providers
- **Dynamic Pricing**: Automatic pricing based on provider and appointment type
- **Secure Payments**: Stripe integration (test mode)
- **Email Confirmations**: Professional HTML emails with appointment details
- **Calendar Integration**: Add to Google Calendar or download .ics file
- **Mobile Responsive**: Works on all devices

### For Admins
- **Provider Management**: Add providers with custom pricing (consultation/follow-up)
- **Analytics Dashboard**: Real-time metrics, revenue tracking, conversion rates
- **Appointment Management**: Filter by provider, payment status, email/calendar sync
- **Email Tracking**: Monitor confirmation and reminder delivery
- **Statistics**: Per-provider revenue and appointment counts

## 💰 Provider-Based Pricing

Each provider has customizable rates:
- **Consultation Price**: e.g., $75 (General), $150 (Specialist)
- **Follow-up Price**: e.g., $45 (General), $100 (Specialist)
- **8 Specialties**: General, Cardiology, Dermatology, Pediatrics, etc.

Price automatically calculated on booking: `provider.consultation_price` or `provider.follow_up_price`

## 🎨 Tech Stack

- **Backend**: Django 5.0+, Python 3.8+
- **Database**: SQLite (dev) → PostgreSQL (production)
- **Payment**: Stripe API
- **Email**: Django email (console in dev, SMTP in production)
- **Calendar**: Google Calendar API + ICS export
- **Frontend**: Bootstrap 5, vanilla JavaScript
- **Dependencies**: stripe, python-decouple, google-api-python-client

## 📊 Core Models

**Provider**: Healthcare provider with pricing
- Fields: name, specialty, email, phone, consultation_price, follow_up_price, is_active

**Appointment**: Patient booking
- Fields: provider (FK), appointment_time, client_email, appointment_type, amount_paid, is_paid
- Tracking: confirmation_sent, reminder_sent, calendar_synced, stripe_payment_intent_id

## 🛠️ Admin Features

**Provider Management** (`/admin/appointments/provider/`)
- Add/edit providers with custom pricing
- View appointment count and revenue per provider
- Filter by specialty, active status

**Analytics Dashboard** (`/appointments/admin-dashboard/`)
- Total appointments, revenue, payment success rate
- Today/week/month statistics
- Email & calendar conversion rates
- Upcoming appointments, recent bookings
- Top providers, appointment type breakdown

**Appointment List** (`/admin/appointments/appointment/`)
- Filter: provider, payment status, email sent, calendar sync
- Search: provider name, client email, transaction ID
- Color-coded status indicators

## 📧 Email System

**Automated Emails**:
- ✅ Confirmation email (on payment)
- ✅ Reminder email (24h before, scheduled)
- ✅ Provider notification (on new booking)

**Configuration**: 
- Dev: Console backend (prints to terminal)
- Prod: Configure SMTP in `.env` (Gmail, SendGrid, AWS SES)

## 📅 Calendar Integration

**Google Calendar**:
- OAuth flow for patient authorization
- Creates event with appointment details
- Automatic reminders (24h, 30min before)

**ICS Export**:
- Universal .ics file download
- Works with Apple Calendar, Outlook, etc.

## 🔒 Security

- CSRF protection (Django built-in)
- SQL injection protection (Django ORM)
- XSS prevention (template escaping)
- Environment variables for secrets
- HTTPS ready for production
- Stripe PCI compliance

## 📚 Documentation

- **QUICKSTART.txt** - Fast setup guide
- **PROVIDER_PRICING_GUIDE.md** - Provider management & pricing
- **ADMIN_ANALYTICS_GUIDE.md** - Admin dashboard features
- **EMAIL_CALENDAR_FEATURES.md** - Email & calendar integration
- **plan.md** - Product roadmap & scaling strategy

## 🚀 Deployment

**Production Checklist**:
- Set `DEBUG=False` in `.env`
- Use PostgreSQL instead of SQLite
- Configure SMTP for real emails
- Set up Stripe webhooks
- Enable HTTPS/SSL
- Configure static files (S3/CDN)

**Deploy To**:
- Heroku, Railway, DigitalOcean, AWS (instructions in docs)

## 🧪 Testing

```bash
# Test appointment booking
1. Go to /appointments/create/
2. Select provider (e.g., "Dr. Michael Chen - Cardiology")
3. Choose appointment type (Consultation or Follow-up)
4. See price update ($150 for consultation)
5. Complete booking, test payment with 4242 4242 4242 4242
6. Check email in terminal (console backend)
7. Download .ics file from success page
```

## 📈 Sample Data

**5 Pre-loaded Providers**:
- Default Provider (General) - $50/$30
- Dr. Sarah Johnson (General) - $75/$45
- Dr. Michael Chen (Cardiology) - $150/$100
- Dr. Emily Rodriguez (Dermatology) - $100/$60
- Dr. James Wilson (Pediatrics) - $80/$50

## 🔮 Future Roadmap

**Phase 2**: Multi-provider dashboards, patient portal  
**Phase 3**: HIPAA compliance, telehealth, EHR integration  
**Phase 4**: Multi-tenancy, insurance verification, API  
**Phase 5**: AI scheduling, mobile apps, analytics

See `plan.md` for detailed roadmap.

## 💡 Key Highlights

✅ **Production-ready** MVP architecture  
✅ **Scalable** provider management  
✅ **Flexible** pricing system  
✅ **Professional** email templates  
✅ **Comprehensive** admin analytics  
✅ **Clean** codebase (PEP 8)  
✅ **Well-documented** with guides  
✅ **Healthcare-focused** design  

---

**Built for healthcare providers** | [Documentation](./QUICKSTART.txt) | [Roadmap](./plan.md)
