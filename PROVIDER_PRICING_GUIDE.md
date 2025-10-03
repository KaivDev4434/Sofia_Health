# Provider-Based Dynamic Pricing System

## 🎯 Overview

The Sofia Health platform now features a **Provider-Based Dynamic Pricing System** that allows administrators to:
- Manage multiple healthcare providers
- Set custom pricing per provider and appointment type
- Automatically calculate appointment costs based on provider and type selection

## ✨ Key Features

### 1. **Healthcare Provider Management**
- Create and manage multiple healthcare providers
- Set individual pricing for each provider
- Different rates for consultation vs. follow-up appointments
- Provider specialties and contact information
- Active/inactive status control

### 2. **Dynamic Pricing**
- Automatic price calculation based on:
  - Selected provider
  - Appointment type (Consultation/Follow-up)
- Real-time price display on booking form
- No manual price entry required

### 3. **Admin Customization**
- Full control over provider pricing
- Provider statistics and revenue tracking
- Filter appointments by provider
- Search across provider details

---

## 📋 **Provider Model Fields**

| Field | Type | Description |
|-------|------|-------------|
| `name` | CharField | Provider's full name |
| `specialty` | CharField | Medical specialty (dropdown) |
| `email` | EmailField | Provider's email for notifications |
| `phone` | CharField | Contact phone number |
| `consultation_price` | DecimalField | Price for consultation appointments |
| `follow_up_price` | DecimalField | Price for follow-up appointments |
| `is_active` | BooleanField | Whether accepting appointments |
| `bio` | TextField | Provider biography/description |

---

## 🏥 **Available Specialties**

- General Practitioner
- Cardiology
- Dermatology
- Pediatrics
- Psychiatry
- Orthopedics
- Neurology
- Other

---

## 💰 **How Pricing Works**

### Automatic Calculation

When a patient books an appointment:

1. **Selects Provider** → System loads provider pricing
2. **Selects Appointment Type** → System calculates final price
3. **Price Displayed** → Real-time update on booking form
4. **Payment Created** → Stripe PaymentIntent with exact amount

### Price Formula

```
IF appointment_type == 'consultation':
    price = provider.consultation_price
ELSE IF appointment_type == 'follow_up':
    price = provider.follow_up_price
```

---

## 🛠️ **Admin Management**

### Adding a New Provider

1. **Navigate to Admin**: http://127.0.0.1:8000/admin/
2. **Go to "Healthcare Providers"**
3. **Click "Add Provider"**
4. **Fill in Details**:
   - Name: e.g., "Dr. Sarah Johnson"
   - Specialty: Select from dropdown
   - Email & Phone (optional)
   - **Consultation Price**: e.g., $75.00
   - **Follow-up Price**: e.g., $45.00
   - Is Active: ✓ (checked)
   - Bio: Provider description
5. **Save**

### Updating Provider Pricing

1. **Go to "Healthcare Providers"**
2. **Click on provider name**
3. **Update Pricing**:
   - Consultation Price
   - Follow-up Price
4. **Save**
5. **Future appointments** will use new prices
6. **Existing appointments** retain original price

### Provider Statistics

Each provider shows:
- **Total Appointments**: Number of bookings
- **Total Revenue**: Sum of paid appointments
- **Appointment Count**: Real-time statistics

---

## 👥 **Sample Providers Created**

The system comes with 5 sample providers:

| Provider | Specialty | Consultation | Follow-up |
|----------|-----------|--------------|-----------|
| Default Provider | General Practitioner | $50.00 | $30.00 |
| Dr. Sarah Johnson | General Practitioner | $75.00 | $45.00 |
| Dr. Michael Chen | Cardiology | $150.00 | $100.00 |
| Dr. Emily Rodriguez | Dermatology | $100.00 | $60.00 |
| Dr. James Wilson | Pediatrics | $80.00 | $50.00 |

---

## 🎨 **User Experience**

### Patient Booking Flow

1. **Select Provider**
   - Dropdown shows all active providers
   - Provider info displayed (name + specialty)

2. **Select Appointment Type**
   - Consultation
   - Follow-up

3. **See Dynamic Price**
   - Price updates automatically
   - Shows both provider's rates
   - Clear price display

4. **Complete Booking**
   - Price locked for this appointment
   - Payment amount matches selected rate

### Visual Features

- **Provider Info Card**: Shows selected provider details
- **Price Display**: Large, prominent price display
- **Price Badges**: Shows both consultation and follow-up rates
- **Real-time Updates**: JavaScript-powered price calculation

---

## 📊 **Admin Interface Features**

### Provider List View

- **Columns Displayed**:
  - ID
  - Name
  - Specialty
  - Consultation Price
  - Follow-up Price
  - Active Status
  - Appointment Count
  - Created Date

- **Filters**:
  - Active/Inactive
  - Specialty
  - Creation Date

- **Search**:
  - Provider name
  - Email
  - Specialty

### Appointment List View (Updated)

- **New Features**:
  - Provider dropdown filter
  - Search by provider name
  - Shows provider (not text field)
  - Color-coded pricing

---

## 🔄 **Migration from Old System**

### What Changed

**Before**: 
- `provider_name` (text field)
- Fixed pricing ($50)

**After**:
- `provider` (dropdown with ForeignKey)
- Dynamic pricing per provider/type
- `provider_name` kept for backward compatibility

### Backward Compatibility

- Old `provider_name` field still exists
- Existing appointments preserved
- New appointments use provider dropdown
- Both fields displayed in templates

---

## 💡 **Use Cases**

### 1. Multi-Provider Clinic

```
Dr. Smith (General) - $60 consultation, $35 follow-up
Dr. Jones (Specialist) - $120 consultation, $80 follow-up
Nurse Practitioner - $40 consultation, $25 follow-up
```

### 2. Tiered Pricing

```
Junior Doctor - $50/30
Senior Doctor - $75/45
Specialist - $150/100
```

### 3. Service-Based Pricing

```
Therapy Session - $100/80
Medical Checkup - $75/50
Specialist Consult - $200/150
```

---

## 🚀 **Best Practices**

### For Administrators

1. **Set Clear Pricing**
   - Consistent pricing structure
   - Competitive rates
   - Clear consultation vs. follow-up difference

2. **Keep Providers Updated**
   - Mark inactive providers as inactive
   - Update contact information
   - Maintain accurate specialties

3. **Monitor Revenue**
   - Check provider statistics
   - Track popular providers
   - Analyze pricing effectiveness

4. **Regular Reviews**
   - Review pricing quarterly
   - Adjust based on demand
   - Compare with market rates

### For Developers

1. **Price Calculation**
   - Always use `appointment.calculate_price()`
   - Price set automatically on save
   - Don't override manually

2. **Provider Selection**
   - Only show active providers
   - Validate provider availability
   - Handle deleted providers gracefully

3. **Future Enhancements**
   - Time-based pricing (peak hours)
   - Insurance integration
   - Bulk pricing updates
   - Historical price tracking

---

## 🔧 **Customization**

### Adding New Specialty

Edit `appointments/models.py`:

```python
SPECIALTY_CHOICES = [
    ('general', 'General Practitioner'),
    ('cardiology', 'Cardiology'),
    # Add new specialty:
    ('oncology', 'Oncology'),
]
```

### Adding Third Appointment Type

1. Update `APPOINTMENT_TYPE_CHOICES` in models
2. Add price field to Provider model (e.g., `emergency_price`)
3. Update `get_price_for_appointment_type()` method
4. Update form and templates

### Custom Pricing Logic

Override `calculate_price()` in Appointment model:

```python
def calculate_price(self):
    base_price = self.provider.get_price_for_appointment_type(self.appointment_type)
    
    # Add custom logic:
    if self.is_weekend():
        base_price *= 1.2  # 20% weekend surcharge
    
    return base_price
```

---

## 📈 **Analytics Integration**

### Provider Performance Metrics

- Appointments per provider
- Revenue per provider
- Average appointment value
- Consultation vs. follow-up ratio

### Revenue Tracking

- Total revenue by provider
- Monthly revenue trends
- Price effectiveness analysis
- Popular specialties

---

## ⚙️ **Technical Details**

### Database Schema

**Provider Table**:
```sql
CREATE TABLE provider (
    id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    specialty VARCHAR(50),
    email VARCHAR(254),
    phone VARCHAR(20),
    consultation_price DECIMAL(10,2),
    follow_up_price DECIMAL(10,2),
    is_active BOOLEAN,
    bio TEXT,
    created_at DATETIME,
    updated_at DATETIME
);
```

**Appointment Table (Updated)**:
```sql
ALTER TABLE appointment 
ADD COLUMN provider_id INTEGER REFERENCES provider(id),
ALTER COLUMN provider_name SET NULL;
```

### API Response (Future)

```json
{
    "provider": {
        "id": 1,
        "name": "Dr. Sarah Johnson",
        "specialty": "general",
        "consultation_price": "75.00",
        "follow_up_price": "45.00"
    },
    "appointment_type": "consultation",
    "calculated_price": "75.00"
}
```

---

## 🐛 **Troubleshooting**

### Provider Not Showing in Dropdown

**Cause**: Provider marked as inactive  
**Solution**: Set `is_active = True` in admin

### Price Not Updating

**Cause**: JavaScript not loading  
**Solution**: Clear cache, check browser console

### Wrong Price Calculated

**Cause**: Price cached from old selection  
**Solution**: Refresh page, reselect provider

### Migration Errors

**Cause**: Existing appointments without provider  
**Solution**: Run `migrate_to_providers.py` script first

---

## 📚 **Related Documentation**

- `ADMIN_ANALYTICS_GUIDE.md` - Admin dashboard features
- `EMAIL_CALENDAR_FEATURES.md` - Email and calendar integration
- `README.md` - General setup and usage
- `plan.md` - Future roadmap

---

**The Provider-Based Pricing System transforms Sofia Health into a flexible, multi-provider healthcare platform with customizable pricing!** 💰🏥


