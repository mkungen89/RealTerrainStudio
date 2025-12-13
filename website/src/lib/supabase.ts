import { createClient } from '@supabase/supabase-js'
import { createBrowserClient } from '@supabase/ssr'

// Supabase client for server-side usage
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
)

// Supabase client for client-side usage in components
export const createSupabaseClient = () => {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

// Types for database tables
export type Database = {
  public: {
    Tables: {
      users: {
        Row: {
          id: string
          email: string
          full_name: string | null
          created_at: string
          updated_at: string
        }
        Insert: {
          id: string
          email: string
          full_name?: string | null
          created_at?: string
          updated_at?: string
        }
        Update: {
          id?: string
          email?: string
          full_name?: string | null
          updated_at?: string
        }
      }
      licenses: {
        Row: {
          id: string
          user_id: string
          license_key: string
          plan_type: 'hobby' | 'professional' | 'enterprise'
          status: 'active' | 'expired' | 'cancelled'
          created_at: string
          expires_at: string | null
          max_activations: number
          current_activations: number
        }
        Insert: {
          id?: string
          user_id: string
          license_key: string
          plan_type: 'hobby' | 'professional' | 'enterprise'
          status?: 'active' | 'expired' | 'cancelled'
          created_at?: string
          expires_at?: string | null
          max_activations?: number
          current_activations?: number
        }
        Update: {
          user_id?: string
          license_key?: string
          plan_type?: 'hobby' | 'professional' | 'enterprise'
          status?: 'active' | 'expired' | 'cancelled'
          expires_at?: string | null
          max_activations?: number
          current_activations?: number
        }
      }
      activations: {
        Row: {
          id: string
          license_id: string
          hardware_id: string
          machine_name: string | null
          activated_at: string
          last_seen: string
        }
        Insert: {
          id?: string
          license_id: string
          hardware_id: string
          machine_name?: string | null
          activated_at?: string
          last_seen?: string
        }
        Update: {
          machine_name?: string | null
          last_seen?: string
        }
      }
      exports: {
        Row: {
          id: string
          user_id: string
          license_id: string
          bounds: any // JSON object
          profile: string
          file_size: number
          created_at: string
        }
        Insert: {
          id?: string
          user_id: string
          license_id: string
          bounds: any
          profile: string
          file_size: number
          created_at?: string
        }
        Update: {
          bounds?: any
          profile?: string
          file_size?: number
        }
      }
    }
  }
}
