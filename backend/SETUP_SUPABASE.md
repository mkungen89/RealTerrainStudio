# 🗄️ Supabase Database Setup Guide

**Complete step-by-step guide to set up your database for RealTerrain Studio**

---

## ✅ What We've Done So Far

- ✅ Connected to your Supabase project successfully
- ✅ Created `.env` file with your credentials
- ✅ Tested the connection (it works!)
- ✅ Prepared the SQL migration script

---

## 📋 What You Need to Do Now

Run the SQL migration to create the database tables. This is a simple copy-paste operation!

---

## 🎯 Step-by-Step Instructions

### Step 1: Open Supabase Dashboard

1. Go to: **https://supabase.com/dashboard**
2. Log in if prompted
3. You should see your project: **RTS_APP**
4. Click on the **RTS_APP** project to open it

### Step 2: Open SQL Editor

1. Look at the left sidebar
2. Find and click on **"SQL Editor"**
   - It has an icon that looks like: `</>`
3. The SQL Editor page will open

### Step 3: Create New Query

1. Click the **"New Query"** button
   - It's usually in the top right
   - Or you might see a **"+"** button
2. A blank editor window will appear

### Step 4: Copy the SQL Migration

The SQL migration is located at:
```
C:\RealTerrainStudio\backend\supabase\migrations\001_initial_schema.sql
```

**Option A: Open the file and copy all contents**
1. Open the file in VS Code or Notepad
2. Select all (Ctrl+A)
3. Copy (Ctrl+C)

**Option B: The SQL is also shown in the terminal above!**
- Scroll up in your terminal
- Copy everything between the `====` lines

### Step 5: Paste and Run

1. Paste the SQL into the Supabase SQL Editor
   - Click in the editor window
   - Paste (Ctrl+V)

2. Click the **"Run"** button
   - Or press **Ctrl+Enter**

3. Wait for it to finish (should take 2-3 seconds)

### Step 6: Check for Success

After running, you should see:
- ✅ A success message at the bottom
- ✅ Something like: "Success. No rows returned"
- ✅ Or: "Migration 001_initial_schema.sql completed successfully"

**If you see an error:**
- Red text will appear
- Copy the error message
- Let me know and I'll help fix it!

---

## 🔍 Step 7: Verify the Setup

After running the SQL, let's verify everything worked:

**Open your terminal and run:**
```bash
cd C:\RealTerrainStudio\backend
python verify_database.py
```

This will check that all 5 tables were created:
1. ✅ profiles
2. ✅ licenses
3. ✅ hardware_activations
4. ✅ exports
5. ✅ payments

---

## 📊 What The Migration Creates

### Tables:

**1. profiles**
- Stores user information (name, email, company)
- Automatically created when someone signs up

**2. licenses**
- Stores license keys for users
- Tracks if license is active, expired, or cancelled
- Links to stripe payments

**3. hardware_activations**
- Tracks which computers have activated a license
- Prevents sharing one license across too many computers
- Limited by plan (Free: 1 computer, Pro: 3 computers)

**4. exports**
- Records every terrain export a user makes
- Tracks area size for quota management
- Used for analytics

**5. payments**
- Records all payments made through Stripe
- Links payments to licenses
- Track refunds and failed payments

### Security Features:

**Row Level Security (RLS)**
- Users can only see their own data
- No user can access another user's licenses or payments
- Service role key (for admin) can see everything

**Automatic Triggers**
- When a user signs up, automatically create their profile
- When a user signs up, give them a free license key
- Automatically update timestamps when records change

---

## 🎓 Understanding What Happened

**Before:**
- Empty database
- No tables
- No data structure

**After:**
- 5 tables created
- Row Level Security enabled
- Automatic triggers set up
- Foreign key relationships defined
- Indexes for fast queries

**Real-world analogy:**
Think of it like building a filing cabinet system:
- Before: Empty room
- After: 5 filing cabinets (tables), each with labeled drawers (columns)
- Security: Only you can open your own drawers (RLS)
- Automation: New folder created automatically when you start (triggers)

---

## 🐛 Troubleshooting

### Error: "relation already exists"
**Meaning:** Tables are already created!
**Solution:** Great! Run the verification script to confirm

### Error: "permission denied"
**Meaning:** Not logged in or wrong project
**Solution:**
1. Check you're in the RTS_APP project
2. Try refreshing the page
3. Log out and log back in

### Error: "syntax error at or near..."
**Meaning:** SQL wasn't copied correctly
**Solution:**
1. Make sure you copied ALL the SQL
2. Don't add or remove any characters
3. Copy from the beginning (-- RealTerrain...) to the end (END $$;)

### No error but verification fails
**Meaning:** SQL might not have run
**Solution:**
1. Check the "Results" panel in SQL Editor
2. Look for success message
3. Try running the SQL again

---

## ✨ After Verification Passes

Once `verify_database.py` shows all tables exist:

**You're done with TASK-003!** 🎉

**What's ready:**
- ✅ Database structure complete
- ✅ Security policies active
- ✅ Automatic user provisioning set up
- ✅ Ready to build the QGIS plugin!

**Next steps:**
- TASK-004: Setup VS Code Workspace (optional)
- TASK-005: Create QGIS Plugin Base (exciting!)

---

## 📬 Need Help?

If you get stuck:
1. Copy any error messages
2. Take a screenshot of the SQL Editor
3. Let me know and I'll help immediately!

---

**Created:** 2024-12-08
**Database:** Supabase PostgreSQL
**Project:** RTS_APP
**Tables:** 5
**Status:** Ready to run!
