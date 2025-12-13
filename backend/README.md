# 🔐 Backend - RealTerrain Studio

This is the backend component of RealTerrain Studio, powered by Supabase. It handles user authentication, licensing, payments, and data storage.

---

## 📁 Folder Structure

```
backend/
├── supabase/
│   ├── migrations/              ← Database schema migrations
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_add_licenses.sql
│   │   └── 003_add_activations.sql
│   │
│   ├── functions/               ← Edge Functions (serverless)
│   │   ├── validate-license/
│   │   │   └── index.ts
│   │   ├── create-checkout/
│   │   │   └── index.ts
│   │   └── webhook-stripe/
│   │       └── index.ts
│   │
│   └── config.toml              ← Supabase configuration
│
├── config/
│   ├── .env.example            ← Environment variables template
│   └── stripe-products.json    ← Stripe product definitions
│
└── README.md                    ← This file
```

---

## 🗄️ Database Schema

### Tables

**`users`** (managed by Supabase Auth)
- Handles user authentication
- Email/password or OAuth
- Email verification

**`profiles`**
- User profile information
- Links to Supabase Auth user
```sql
id              UUID PRIMARY KEY (references auth.users)
email           TEXT NOT NULL
full_name       TEXT
company         TEXT
created_at      TIMESTAMP
updated_at      TIMESTAMP
```

**`licenses`**
- User licenses and subscriptions
```sql
id              UUID PRIMARY KEY
user_id         UUID REFERENCES profiles(id)
license_key     TEXT UNIQUE NOT NULL
plan_type       TEXT NOT NULL (free, pro, enterprise)
status          TEXT NOT NULL (active, expired, cancelled)
max_activations INT NOT NULL
created_at      TIMESTAMP
expires_at      TIMESTAMP
```

**`hardware_activations`**
- Track which machines have activated licenses
```sql
id              UUID PRIMARY KEY
license_id      UUID REFERENCES licenses(id)
hardware_id     TEXT NOT NULL
machine_name    TEXT
activated_at    TIMESTAMP
last_seen       TIMESTAMP
is_active       BOOLEAN DEFAULT TRUE
```

**`exports`**
- Track user exports for quota management
```sql
id              UUID PRIMARY KEY
user_id         UUID REFERENCES profiles(id)
area_km2        FLOAT NOT NULL
created_at      TIMESTAMP
file_size_mb    FLOAT
```

**`payments`**
- Payment history
```sql
id                  UUID PRIMARY KEY
user_id             UUID REFERENCES profiles(id)
stripe_payment_id   TEXT UNIQUE
amount              INT NOT NULL (cents)
currency            TEXT DEFAULT 'usd'
status              TEXT NOT NULL
created_at          TIMESTAMP
```

---

## 🚀 Setup

### Prerequisites
- Supabase account (free tier works for development)
- Stripe account (for payments)
- Node.js 18+ (for Edge Functions)

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Click "New Project"
3. Fill in:
   - Project name: `realterrain-studio`
   - Database password: (save this!)
   - Region: Choose closest to your users
4. Wait for project to initialize (~2 minutes)

### Step 2: Get API Keys

1. In Supabase Dashboard, go to **Settings** → **API**
2. Copy these values:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (keep secret!)

### Step 3: Configure Environment

1. Copy `.env.example` to `.env`:
```bash
cd backend/config
cp .env.example .env
```

2. Edit `.env` and add your keys:
```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
```

### Step 4: Run Migrations

Run SQL migrations to create database tables:

1. In Supabase Dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy contents of `migrations/001_initial_schema.sql`
4. Click **Run**
5. Repeat for each migration file in order

Or use Supabase CLI:
```bash
# Install Supabase CLI
npm install -g supabase

# Login
supabase login

# Link to your project
supabase link --project-ref your-project-id

# Run migrations
supabase db push
```

### Step 5: Deploy Edge Functions

```bash
# Install dependencies
cd backend/supabase/functions/validate-license
npm install

# Deploy function
supabase functions deploy validate-license

# Repeat for other functions
```

---

## 🔐 Authentication Flow

### User Registration
```typescript
// In QGIS Plugin or Website
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password'
})
```

### User Login
```typescript
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'secure-password'
})
```

### License Validation (in QGIS Plugin)
```typescript
// Call Edge Function
const { data, error } = await supabase.functions.invoke('validate-license', {
  body: {
    licenseKey: 'RT-XXXX-XXXX-XXXX',
    hardwareId: getHardwareId()
  }
})
```

---

## 💳 Payment Flow

### 1. User wants to upgrade
User clicks "Upgrade to Pro" on website

### 2. Create Stripe Checkout Session
```typescript
// Edge Function: create-checkout
const session = await stripe.checkout.sessions.create({
  customer_email: user.email,
  line_items: [{ price: 'price_pro_monthly', quantity: 1 }],
  mode: 'subscription',
  success_url: 'https://yoursite.com/success',
  cancel_url: 'https://yoursite.com/cancel'
})
```

### 3. User completes payment
Stripe redirects to success page

### 4. Webhook creates license
```typescript
// Edge Function: webhook-stripe
// Stripe sends event to webhook
// Create license in database
const license = await supabase.from('licenses').insert({
  user_id: userId,
  license_key: generateLicenseKey(),
  plan_type: 'pro',
  status: 'active',
  max_activations: 3
})
```

---

## 🛡️ Row Level Security (RLS)

Supabase uses RLS to ensure users can only access their own data:

```sql
-- Users can only read their own profile
CREATE POLICY "Users can view own profile"
ON profiles FOR SELECT
USING (auth.uid() = id);

-- Users can only view their own licenses
CREATE POLICY "Users can view own licenses"
ON licenses FOR SELECT
USING (auth.uid() = user_id);

-- Service role can do anything (for admin)
-- No RLS policy needed, service_role bypasses RLS
```

---

## 📊 API Endpoints

### Edge Functions

**`validate-license`**
- **Method**: POST
- **Body**: `{ licenseKey, hardwareId }`
- **Returns**: `{ valid: boolean, plan: string, expiresAt: date }`

**`create-checkout`**
- **Method**: POST
- **Body**: `{ planType: 'pro' | 'enterprise' }`
- **Returns**: `{ sessionId, url }`

**`webhook-stripe`**
- **Method**: POST
- **Body**: Stripe webhook event
- **Returns**: `{ received: true }`

---

## 🧪 Testing

### Test License Validation
```bash
curl -X POST https://xxxxx.supabase.co/functions/v1/validate-license \
  -H "Authorization: Bearer YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "licenseKey": "RT-TEST-1234-5678",
    "hardwareId": "test-machine-id"
  }'
```

### Test locally with Supabase CLI
```bash
# Start local Supabase
supabase start

# Function runs on http://localhost:54321
```

---

## 🔧 Configuration

### Subscription Plans

Edit `config/stripe-products.json`:
```json
{
  "free": {
    "name": "Free Tier",
    "quota_km2_per_month": 10,
    "max_activations": 1,
    "features": ["Basic export", "10km² per month"]
  },
  "pro": {
    "name": "Pro",
    "price_monthly": 29.99,
    "price_annual": 299.99,
    "quota_km2_per_month": -1,
    "max_activations": 3,
    "features": ["Unlimited exports", "3 machines", "Priority support"]
  }
}
```

---

## 🐛 Troubleshooting

### Can't connect to Supabase
- Check Project URL is correct
- Verify API key is correct
- Check internet connection
- Check Supabase status page

### Migrations fail
- Run migrations in order
- Check for syntax errors
- Verify you have write permissions
- Check database is not in read-only mode

### Edge Functions not working
- Check function is deployed
- Verify function logs in Supabase Dashboard
- Test with curl first
- Check CORS settings

---

## 🆘 Support

- Supabase Docs: [supabase.com/docs](https://supabase.com/docs)
- Stripe Docs: [stripe.com/docs](https://stripe.com/docs)
- Email: support@realterrainstudio.com

---

**Built with Supabase + PostgreSQL + Edge Functions + Stripe**
