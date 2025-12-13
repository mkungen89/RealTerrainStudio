# 🚀 Vercel Monorepo Setup Guide

## The Problem

You're getting a 404 error because Vercel is trying to build from the **root** of your repository, but your Next.js website is in the **`website/`** subdirectory.

Your repo structure:
```
RealTerrainStudio/
├── backend/           ← Not needed for website
├── qgis-plugin/       ← Not needed for website
├── ue5-plugin/        ← Not needed for website
├── website/           ← THIS is what Vercel needs!
│   ├── src/
│   ├── package.json
│   └── next.config.js
└── vercel.json        ← Configuration file
```

---

## ✅ Solution: Configure Vercel for Monorepo

I've added a `vercel.json` file at the root that tells Vercel to build from the `website/` folder.

---

## 🔧 Manual Configuration in Vercel Dashboard

**You need to configure Vercel to use the website directory:**

### Step 1: Go to Project Settings

1. Open your Vercel dashboard
2. Select your **RealTerrainStudio** project
3. Click **Settings**

### Step 2: Configure Root Directory

1. Scroll to **Build & Development Settings**
2. Find **Root Directory**
3. Click **Edit**
4. Enter: `website`
5. Click **Save**

### Step 3: Configure Build Settings

Verify these settings:

**Framework Preset:** Next.js

**Build Command:**
```bash
npm run build
```

**Output Directory:**
```bash
.next
```

**Install Command:**
```bash
npm install
```

**Root Directory:**
```bash
website
```

### Step 4: Add Environment Variables

Still in Settings, go to **Environment Variables**:

Add these:
```
NEXT_PUBLIC_SUPABASE_URL=https://evxlknlcsjslqbhyjrud.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
```

Optional (for payments):
```
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### Step 5: Redeploy

1. Go to **Deployments**
2. Click **Redeploy** on the latest deployment
3. Wait for build to complete

---

## 📊 What Should Happen

**Before:**
```
❌ 404: NOT_FOUND
❌ Vercel looking at root package.json (doesn't exist)
❌ Build failing
```

**After:**
```
✅ Vercel builds from website/ folder
✅ Finds website/package.json
✅ Runs npm install in website/
✅ Builds Next.js site
✅ Deployment succeeds
```

---

## 🎯 Alternative: Use Vercel CLI

If the dashboard isn't working, use the Vercel CLI:

### Install Vercel CLI
```bash
npm install -g vercel
```

### Login
```bash
vercel login
```

### Link Project
```bash
cd C:\RealTerrainStudio
vercel link
```

### Configure
```bash
vercel --cwd website
```

This tells Vercel to use the `website` directory.

---

## 🔍 Debugging

### Check Build Logs

1. Go to Vercel dashboard
2. Click on failed deployment
3. Click **Building**
4. Look for errors like:
   - ❌ "No package.json found"
   - ❌ "Next.js not detected"
   - ✅ Should say "Detected Next.js"

### Verify Root Directory

In build logs, you should see:
```
Using root directory: website
Building in: /vercel/path0/website
```

If you see:
```
Building in: /vercel/path0
```

Then the root directory is **NOT** set correctly.

---

## 📁 Files Created/Modified

| File | Purpose |
|------|---------|
| `vercel.json` (root) | Tells Vercel to build from website/ |
| `website/package.json` | Dependencies and scripts |
| `website/next.config.js` | Next.js configuration |

---

## ✅ Verification Steps

After redeploying:

1. **Check Deployment URL**
   - Visit your-project.vercel.app
   - Should see homepage ✅

2. **Test Routes**
   - `/` - Homepage
   - `/pricing` - Pricing page
   - `/login` - Login page
   - `/signup` - Signup page
   - `/docs` - Documentation

3. **Check Console**
   - Open browser DevTools
   - Should have no errors ✅

---

## 🎨 Project Structure Best Practice

For monorepos, Vercel recommends:

### Option 1: Root Directory (What we're using)
```
RealTerrainStudio/
├── vercel.json          ← Points to website/
└── website/             ← Vercel builds this
    ├── package.json
    ├── next.config.js
    └── src/
```

### Option 2: Separate Repos (Alternative)
Create separate GitHub repos:
- `RealTerrainStudio-Website` (Vercel)
- `RealTerrainStudio-Backend`
- `RealTerrainStudio-QGIS`
- `RealTerrainStudio-UE5`

---

## 🚨 Common Issues

### Issue 1: Still Getting 404
**Solution:** Make sure Root Directory is set to `website` in Vercel dashboard.

### Issue 2: "No package.json found"
**Solution:** Vercel is looking at root. Set Root Directory to `website`.

### Issue 3: Build succeeds but site is blank
**Solution:** Check environment variables are set in Vercel.

### Issue 4: API routes not working
**Solution:** Ensure Vercel region matches Supabase region (or add fallback).

---

## 📚 Resources

- **Vercel Monorepo Docs:** https://vercel.com/docs/concepts/monorepos
- **Next.js Deployment:** https://nextjs.org/docs/deployment
- **Vercel CLI:** https://vercel.com/docs/cli

---

## 🎯 Quick Fix Checklist

- [ ] `vercel.json` exists at root
- [ ] Root Directory set to `website` in Vercel dashboard
- [ ] Environment variables added in Vercel
- [ ] Redeployed after configuration
- [ ] Build logs show "Using root directory: website"
- [ ] Deployment succeeds
- [ ] Website loads at Vercel URL

---

## 💡 Summary

**The fix is simple:**

1. ✅ Added `vercel.json` at root (done!)
2. ⚠️ **YOU NEED TO:** Set Root Directory to `website` in Vercel dashboard
3. ⚠️ **YOU NEED TO:** Add environment variables
4. ⚠️ **YOU NEED TO:** Redeploy

**Once you set the Root Directory to `website`, it will work!** 🎉

---

**Created:** December 13, 2024
**Status:** ✅ Configuration pushed to GitHub
**Next Step:** Configure Root Directory in Vercel dashboard

🌍 **From Earth to Engine** 🎮
