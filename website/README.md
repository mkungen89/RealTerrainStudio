# 🌐 Website - RealTerrain Studio

This is the marketing website and user portal for RealTerrain Studio, built with Next.js 14, React, and TypeScript.

---

## 📁 Folder Structure

```
website/
├── src/
│   ├── app/                     ← Next.js 14 App Router
│   │   ├── page.tsx            ← Homepage
│   │   ├── layout.tsx          ← Root layout
│   │   ├── pricing/
│   │   │   └── page.tsx        ← Pricing page
│   │   ├── dashboard/
│   │   │   └── page.tsx        ← User dashboard
│   │   ├── docs/
│   │   │   └── page.tsx        ← Documentation
│   │   └── api/                ← API routes
│   │       └── webhook/
│   │
│   ├── components/              ← React components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── PricingCard.tsx
│   │   └── LicenseManager.tsx
│   │
│   └── lib/                     ← Utilities & helpers
│       ├── supabase.ts         ← Supabase client
│       ├── stripe.ts           ← Stripe client
│       └── utils.ts            ← Helper functions
│
├── public/                      ← Static assets
│   ├── images/
│   ├── icons/
│   └── favicon.ico
│
├── .env.local                   ← Environment variables (gitignored)
├── .env.example                 ← Environment template
├── package.json                 ← Dependencies
├── tsconfig.json                ← TypeScript config
├── next.config.js               ← Next.js config
├── tailwind.config.js           ← Tailwind CSS config
└── README.md                    ← This file
```

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- npm or yarn or pnpm
- Supabase project (from backend setup)
- Stripe account (for payments)

### Installation

1. **Install dependencies:**
```bash
cd website
npm install
```

2. **Setup environment variables:**
```bash
cp .env.example .env.local
```

Edit `.env.local` with your keys:
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
```

3. **Run development server:**
```bash
npm run dev
```

4. **Open browser:**
Navigate to [http://localhost:3000](http://localhost:3000)

---

## 🎨 Tech Stack

### Core
- **Next.js 14** - React framework with App Router
- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling

### Backend Integration
- **Supabase** - Authentication & database
- **Stripe** - Payments
- **Edge Functions** - Serverless API

### UI Components
- **Radix UI** - Accessible components
- **Lucide Icons** - Icon library
- **Framer Motion** - Animations

---

## 📄 Pages

### Public Pages

**Homepage (`/`)**
- Hero section with product overview
- Feature showcase
- Pricing comparison
- Call-to-action buttons

**Pricing (`/pricing`)**
- Free, Pro, Enterprise plans
- Feature comparison table
- Stripe checkout integration

**Documentation (`/docs`)**
- User guides
- API reference
- Video tutorials
- Troubleshooting

**About (`/about`)**
- Company information
- Team
- Contact form

### Protected Pages (Require Login)

**Dashboard (`/dashboard`)**
- User profile
- License information
- Usage statistics
- Recent exports

**Licenses (`/dashboard/licenses`)**
- View license keys
- Manage activations
- Upgrade/downgrade plans

**Billing (`/dashboard/billing`)**
- Payment history
- Invoices
- Update payment method

---

## 🔐 Authentication

Uses Supabase Auth with multiple methods:

### Email/Password
```typescript
// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'secure-password'
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'secure-password'
})
```

### OAuth Providers
- Google
- GitHub
- Microsoft

```typescript
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google'
})
```

### Magic Link
```typescript
const { data, error } = await supabase.auth.signInWithOtp({
  email: 'user@example.com'
})
```

---

## 💳 Payment Integration

### Checkout Flow

1. **User clicks "Upgrade to Pro"**
2. **Call API route to create checkout session:**
```typescript
const response = await fetch('/api/create-checkout', {
  method: 'POST',
  body: JSON.stringify({ planType: 'pro' })
})
const { sessionId } = await response.json()
```

3. **Redirect to Stripe Checkout:**
```typescript
const stripe = await loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY)
await stripe.redirectToCheckout({ sessionId })
```

4. **Stripe handles payment**
5. **Webhook creates license**
6. **User redirected to success page**

---

## 🎨 Styling

Uses Tailwind CSS for styling:

### Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#0070f3',
        secondary: '#ff4081'
      }
    }
  }
}
```

### Usage
```tsx
<div className="bg-primary text-white p-4 rounded-lg shadow-lg">
  RealTerrain Studio
</div>
```

---

## 🧪 Testing

### Unit Tests
```bash
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```

### Type Checking
```bash
npm run type-check
```

### Linting
```bash
npm run lint
```

---

## 📦 Building for Production

### Build
```bash
npm run build
```

### Start production server
```bash
npm start
```

### Static export (if needed)
```bash
npm run export
```

---

## 🚀 Deployment

### Vercel (Recommended)

1. **Push to GitHub**
2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Import GitHub repository
   - Vercel auto-detects Next.js
3. **Add environment variables** in Vercel dashboard
4. **Deploy!**

### Other Platforms
- **Netlify**: Similar to Vercel
- **AWS Amplify**: Good for AWS ecosystem
- **Docker**: Use included Dockerfile

---

## 🔧 Configuration

### Next.js Config
```javascript
// next.config.js
module.exports = {
  images: {
    domains: ['supabase.co', 'stripe.com']
  },
  reactStrictMode: true
}
```

### TypeScript Config
```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "es2015"],
    "jsx": "preserve",
    "strict": true,
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

---

## 📊 Analytics

### Vercel Analytics
```tsx
import { Analytics } from '@vercel/analytics/react'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        {children}
        <Analytics />
      </body>
    </html>
  )
}
```

### Google Analytics
```tsx
// Add to layout.tsx
<Script
  src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"
  strategy="afterInteractive"
/>
```

---

## 🐛 Troubleshooting

### Hot reload not working
- Check file watcher limits on Linux
- Restart dev server

### Build fails
- Clear `.next` folder: `rm -rf .next`
- Clear node_modules: `rm -rf node_modules && npm install`

### Environment variables not loading
- Ensure `.env.local` exists
- Restart dev server after changing env vars
- Use `NEXT_PUBLIC_` prefix for client-side vars

---

## 🆘 Support

- Next.js Docs: [nextjs.org/docs](https://nextjs.org/docs)
- React Docs: [react.dev](https://react.dev)
- Email: support@realterrainstudio.com

---

**Built with Next.js + React + TypeScript + Tailwind CSS**
