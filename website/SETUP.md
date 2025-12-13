# 🌐 RealTerrain Studio Website - Setup Guide

Complete guide to setting up and running the RealTerrain Studio website locally.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **npm 9+** (comes with Node.js)
- **Git** (for cloning the repository)

You'll also need:
- **Supabase account** - [Sign up here](https://supabase.com)
- **Stripe account** - [Sign up here](https://stripe.com)

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd website
npm install
```

This will install all required packages including:
- Next.js 14
- React 18
- Tailwind CSS
- Supabase client
- Stripe integration
- UI components (Radix UI, Lucide icons)

### Step 2: Configure Environment Variables

1. **Copy the example environment file:**

```bash
cp .env.example .env.local
```

2. **Fill in your environment variables:**

Open `.env.local` and add your actual values:

```env
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Application Settings
NEXT_PUBLIC_APP_URL=http://localhost:3000
NODE_ENV=development
```

### Step 3: Run the Development Server

```bash
npm run dev
```

The website will be available at: **http://localhost:3000**

---

## 🔧 Detailed Configuration

### Supabase Setup

1. **Create a Supabase project** at [supabase.com](https://supabase.com)

2. **Get your credentials:**
   - Go to Project Settings → API
   - Copy the `Project URL` (NEXT_PUBLIC_SUPABASE_URL)
   - Copy the `anon public` key (NEXT_PUBLIC_SUPABASE_ANON_KEY)

3. **Database setup:**
   - The database tables should already be created if you followed the backend setup
   - Required tables: `users`, `licenses`, `activations`, `exports`
   - Refer to `backend/supabase/migrations/` for the schema

4. **Authentication setup:**
   - Go to Authentication → Settings
   - Enable Email/Password provider
   - (Optional) Enable OAuth providers (Google, GitHub, etc.)
   - Add `http://localhost:3000/auth/callback` to allowed redirect URLs

### Stripe Setup

1. **Create a Stripe account** at [stripe.com](https://stripe.com)

2. **Get your API keys:**
   - Go to Developers → API keys
   - Copy the Publishable key (starts with `pk_test_`)
   - Copy the Secret key (starts with `sk_test_`)

3. **Create products and prices:**

You need to create products in Stripe for each plan:

**Hobby Plan:**
- Monthly: $29
- Yearly: $249

**Professional Plan:**
- Monthly: $99
- Yearly: $849

For each product:
1. Go to Products → Add Product
2. Set the name and pricing
3. Create a recurring subscription
4. Copy the Price ID
5. Add Price IDs to `.env.local`:

```env
STRIPE_HOBBY_MONTHLY_PRICE_ID=price_xxx
STRIPE_HOBBY_YEARLY_PRICE_ID=price_xxx
STRIPE_PRO_MONTHLY_PRICE_ID=price_xxx
STRIPE_PRO_YEARLY_PRICE_ID=price_xxx
```

4. **Setup Webhooks:**

For local development:
```bash
# Install Stripe CLI
# Windows: scoop install stripe
# Mac: brew install stripe/stripe-cli/stripe
# Linux: https://stripe.com/docs/stripe-cli

# Login to Stripe
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:3000/api/webhook
```

This will give you a webhook signing secret. Copy it to `STRIPE_WEBHOOK_SECRET` in `.env.local`.

For production:
1. Go to Developers → Webhooks
2. Add endpoint: `https://your-domain.com/api/webhook`
3. Select events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`
4. Copy the signing secret to your production environment

---

## 📁 Project Structure

```
website/
├── src/
│   ├── app/                      # Next.js 14 App Router
│   │   ├── page.tsx             # Homepage
│   │   ├── layout.tsx           # Root layout
│   │   ├── globals.css          # Global styles
│   │   ├── pricing/             # Pricing page
│   │   ├── login/               # Login page
│   │   ├── signup/              # Signup page
│   │   ├── dashboard/           # User dashboard
│   │   ├── docs/                # Documentation
│   │   ├── api/                 # API routes
│   │   │   ├── create-checkout/ # Stripe checkout
│   │   │   ├── webhook/         # Stripe webhooks
│   │   │   └── validate-license/# License validation
│   │   └── auth/                # Auth callback
│   │
│   ├── components/              # React components
│   │   ├── Header.tsx           # Site header
│   │   ├── Footer.tsx           # Site footer
│   │   ├── PricingCard.tsx      # Pricing card component
│   │   └── ui/                  # Reusable UI components
│   │       ├── button.tsx
│   │       └── card.tsx
│   │
│   └── lib/                     # Utilities
│       ├── supabase.ts          # Supabase client
│       ├── stripe.ts            # Stripe client
│       └── utils.ts             # Helper functions
│
├── public/                      # Static assets
├── .env.local                   # Environment variables (not in git)
├── .env.example                 # Environment template
├── package.json                 # Dependencies
├── tsconfig.json                # TypeScript config
├── tailwind.config.js           # Tailwind CSS config
├── next.config.js               # Next.js config
└── README.md                    # This file
```

---

## 🎨 Available Scripts

```bash
# Development
npm run dev              # Start dev server (http://localhost:3000)

# Production
npm run build            # Build for production
npm start                # Start production server

# Code Quality
npm run lint             # Run ESLint
npm run type-check       # Check TypeScript types
npm run format           # Format code with Prettier

# Testing
npm test                 # Run unit tests
npm run test:watch       # Run tests in watch mode
npm run test:e2e         # Run end-to-end tests
```

---

## 🌍 Pages

### Public Pages

- **/** - Homepage with hero, features, and CTA
- **/pricing** - Pricing plans with Stripe integration
- **/docs** - Documentation and guides
- **/login** - User login
- **/signup** - User registration

### Protected Pages (Require Login)

- **/dashboard** - User dashboard with license info
- **/dashboard/billing** - Billing and subscription management

### API Routes

- **POST /api/create-checkout** - Create Stripe checkout session
- **POST /api/webhook** - Handle Stripe webhooks
- **POST /api/validate-license** - Validate license keys
- **GET /api/auth/callback** - OAuth callback handler

---

## 🔒 Security Notes

### Important:

1. **Never commit `.env.local` to git** - It contains sensitive keys
2. **Use test keys in development** - Use `pk_test_` and `sk_test_` keys
3. **Validate all inputs** - API routes validate user input
4. **Use server-side secrets** - Only `NEXT_PUBLIC_*` variables are exposed to the browser
5. **HTTPS in production** - Always use HTTPS for the production site

### Environment Variable Naming:

- `NEXT_PUBLIC_*` - Exposed to the browser (safe for client-side)
- Without prefix - Server-side only (secure, not exposed)

---

## 🚢 Deployment

### Deploy to Vercel (Recommended)

Vercel is the easiest way to deploy Next.js apps:

1. **Push to GitHub:**
```bash
git add .
git commit -m "Initial website setup"
git push origin main
```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your GitHub repository
   - Vercel auto-detects Next.js

3. **Add environment variables:**
   - Go to Project Settings → Environment Variables
   - Add all variables from `.env.local`
   - **Important:** Use production keys for Supabase and Stripe

4. **Deploy:**
   - Vercel automatically builds and deploys
   - Your site will be live at `your-project.vercel.app`

5. **Setup custom domain (optional):**
   - Go to Project Settings → Domains
   - Add your custom domain
   - Update DNS records as instructed

### Other Deployment Options

**Netlify:**
```bash
npm run build
# Deploy the .next folder
```

**Docker:**
```bash
docker build -t realterrain-website .
docker run -p 3000:3000 realterrain-website
```

**AWS Amplify:**
- Connect GitHub repo
- Auto-detects Next.js
- Add environment variables

---

## 🧪 Testing

### Unit Tests

```bash
npm test
```

Tests are located in `__tests__/` folders next to components.

### End-to-End Tests

```bash
npm run test:e2e
```

E2E tests use Playwright to test user flows:
- User registration
- Login/logout
- Purchasing a license
- Viewing dashboard

### Manual Testing Checklist

- [ ] Homepage loads correctly
- [ ] Navigation works on all pages
- [ ] Login/signup flow works
- [ ] Pricing page displays correctly
- [ ] Stripe checkout flow works
- [ ] Dashboard shows user data
- [ ] License keys can be copied
- [ ] API routes return correct responses
- [ ] Mobile responsive design works
- [ ] OAuth login works (if enabled)

---

## 🐛 Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**2. Environment variables not loading**
```bash
# Ensure .env.local exists
# Restart dev server after changing env vars
npm run dev
```

**3. Supabase connection fails**
- Check that your Supabase URL and anon key are correct
- Verify your Supabase project is active
- Check network connection

**4. Stripe checkout not working**
- Verify Stripe keys are correct
- Check that products and prices are created
- Ensure webhook secret is set (for local testing)

**5. Build fails**
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

**6. TypeScript errors**
```bash
# Check types
npm run type-check

# Fix with ESLint
npm run lint -- --fix
```

---

## 📚 Additional Resources

- **Next.js Documentation:** https://nextjs.org/docs
- **Supabase Documentation:** https://supabase.io/docs
- **Stripe Documentation:** https://stripe.com/docs
- **Tailwind CSS:** https://tailwindcss.com/docs
- **Radix UI:** https://www.radix-ui.com/

---

## 🆘 Getting Help

If you encounter issues:

1. **Check the documentation** in `/docs`
2. **Review error messages** in the browser console
3. **Check server logs** in the terminal
4. **Review Supabase logs** in the Supabase dashboard
5. **Review Stripe logs** in the Stripe dashboard

---

## ✅ Next Steps

After setup is complete:

1. **Test the website** - Go through all pages and features
2. **Customize branding** - Update colors, logos, and text
3. **Connect to backend** - Ensure Supabase is properly configured
4. **Test payments** - Use Stripe test cards to verify checkout
5. **Deploy to production** - Follow deployment guide above
6. **Monitor analytics** - Set up Google Analytics or Vercel Analytics
7. **Setup error tracking** - Consider Sentry for error monitoring

---

**Last Updated:** December 13, 2024
**For:** RealTerrain Studio Website v0.1.0

🌍 **From Earth to Engine** 🎮
