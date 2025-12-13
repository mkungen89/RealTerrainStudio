-- RealTerrain Studio - Initial Database Schema
-- Migration: 001_initial_schema.sql
-- Description: Creates the initial database tables and relationships
-- Author: RealTerrain Studio
-- Date: 2024-12-08

-- ============================================
-- ENABLE EXTENSIONS
-- ============================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable pgcrypto for encryption
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- PROFILES TABLE
-- ============================================

-- User profiles (extends Supabase Auth users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT,
    company TEXT,
    avatar_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comment
COMMENT ON TABLE public.profiles IS 'User profile information extending Supabase Auth';

-- Add RLS policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Users can view their own profile
CREATE POLICY "Users can view own profile"
ON public.profiles FOR SELECT
USING (auth.uid() = id);

-- Users can update their own profile
CREATE POLICY "Users can update own profile"
ON public.profiles FOR UPDATE
USING (auth.uid() = id);

-- ============================================
-- LICENSES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.licenses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    license_key TEXT NOT NULL UNIQUE,
    plan_type TEXT NOT NULL CHECK (plan_type IN ('free', 'pro', 'enterprise')),
    status TEXT NOT NULL CHECK (status IN ('active', 'expired', 'cancelled', 'suspended')) DEFAULT 'active',
    max_activations INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Add comment
COMMENT ON TABLE public.licenses IS 'User licenses and subscriptions';

-- Add index on user_id for faster lookups
CREATE INDEX licenses_user_id_idx ON public.licenses(user_id);
CREATE INDEX licenses_license_key_idx ON public.licenses(license_key);
CREATE INDEX licenses_status_idx ON public.licenses(status);

-- Add RLS policies
ALTER TABLE public.licenses ENABLE ROW LEVEL SECURITY;

-- Users can view their own licenses
CREATE POLICY "Users can view own licenses"
ON public.licenses FOR SELECT
USING (auth.uid() = user_id);

-- ============================================
-- HARDWARE ACTIVATIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.hardware_activations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_id UUID NOT NULL REFERENCES public.licenses(id) ON DELETE CASCADE,
    hardware_id TEXT NOT NULL,
    machine_name TEXT,
    os_info TEXT,
    activated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}'::jsonb,
    UNIQUE(license_id, hardware_id)
);

-- Add comment
COMMENT ON TABLE public.hardware_activations IS 'Track which machines have activated licenses';

-- Add indexes
CREATE INDEX hardware_activations_license_id_idx ON public.hardware_activations(license_id);
CREATE INDEX hardware_activations_hardware_id_idx ON public.hardware_activations(hardware_id);
CREATE INDEX hardware_activations_is_active_idx ON public.hardware_activations(is_active);

-- Add RLS policies
ALTER TABLE public.hardware_activations ENABLE ROW LEVEL SECURITY;

-- Users can view activations for their licenses
CREATE POLICY "Users can view own activations"
ON public.hardware_activations FOR SELECT
USING (
    license_id IN (
        SELECT id FROM public.licenses WHERE user_id = auth.uid()
    )
);

-- ============================================
-- EXPORTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.exports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    area_km2 FLOAT NOT NULL,
    bounds JSONB NOT NULL, -- {minLon, minLat, maxLon, maxLat}
    file_size_mb FLOAT,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Add comment
COMMENT ON TABLE public.exports IS 'Track user exports for quota management';

-- Add indexes
CREATE INDEX exports_user_id_idx ON public.exports(user_id);
CREATE INDEX exports_created_at_idx ON public.exports(created_at);
CREATE INDEX exports_status_idx ON public.exports(status);

-- Add RLS policies
ALTER TABLE public.exports ENABLE ROW LEVEL SECURITY;

-- Users can view their own exports
CREATE POLICY "Users can view own exports"
ON public.exports FOR SELECT
USING (auth.uid() = user_id);

-- Users can create exports
CREATE POLICY "Users can create exports"
ON public.exports FOR INSERT
WITH CHECK (auth.uid() = user_id);

-- ============================================
-- PAYMENTS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS public.payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    stripe_payment_id TEXT UNIQUE,
    stripe_subscription_id TEXT,
    amount INTEGER NOT NULL, -- in cents
    currency TEXT NOT NULL DEFAULT 'usd',
    status TEXT NOT NULL CHECK (status IN ('pending', 'succeeded', 'failed', 'refunded')),
    plan_type TEXT CHECK (plan_type IN ('free', 'pro', 'enterprise')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Add comment
COMMENT ON TABLE public.payments IS 'Payment history and transactions';

-- Add indexes
CREATE INDEX payments_user_id_idx ON public.payments(user_id);
CREATE INDEX payments_stripe_payment_id_idx ON public.payments(stripe_payment_id);
CREATE INDEX payments_status_idx ON public.payments(status);

-- Add RLS policies
ALTER TABLE public.payments ENABLE ROW LEVEL SECURITY;

-- Users can view their own payments
CREATE POLICY "Users can view own payments"
ON public.payments FOR SELECT
USING (auth.uid() = user_id);

-- ============================================
-- FUNCTIONS
-- ============================================

-- Function to automatically create profile when user signs up
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        NEW.raw_user_meta_data->>'full_name'
    );

    -- Create free license for new user
    INSERT INTO public.licenses (user_id, license_key, plan_type, max_activations)
    VALUES (
        NEW.id,
        'RT-FREE-' || UPPER(SUBSTRING(MD5(NEW.id::TEXT) FROM 1 FOR 8)),
        'free',
        1
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to call handle_new_user on signup
CREATE OR REPLACE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION public.handle_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at on profiles
CREATE OR REPLACE TRIGGER on_profiles_updated
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_updated_at();

-- ============================================
-- SEED DATA (for development/testing)
-- ============================================

-- This section is commented out for production
-- Uncomment for development to create test data

/*
-- Insert test user profile (requires user to exist in auth.users first)
INSERT INTO public.profiles (id, email, full_name, company)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'test@realterrainstudio.com',
    'Test User',
    'Test Company'
) ON CONFLICT (id) DO NOTHING;

-- Insert test license
INSERT INTO public.licenses (user_id, license_key, plan_type, max_activations)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'RT-TEST-1234-5678',
    'pro',
    3
) ON CONFLICT (license_key) DO NOTHING;
*/

-- ============================================
-- DONE
-- ============================================

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_initial_schema.sql completed successfully';
END $$;
