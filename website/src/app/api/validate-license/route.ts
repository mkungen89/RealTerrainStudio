import { NextRequest, NextResponse } from 'next/server'
import { supabase } from '@/lib/supabase'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { licenseKey, hardwareId, machineName } = body

    // Validate request
    if (!licenseKey || !hardwareId) {
      return NextResponse.json(
        {
          valid: false,
          error: 'Missing license key or hardware ID'
        },
        { status: 400 }
      )
    }

    // Fetch license from database
    const { data: license, error: licenseError } = await supabase
      .from('licenses')
      .select('*')
      .eq('license_key', licenseKey)
      .single()

    if (licenseError || !license) {
      return NextResponse.json({
        valid: false,
        error: 'Invalid license key'
      })
    }

    // Check if license is active
    if (license.status !== 'active') {
      return NextResponse.json({
        valid: false,
        error: `License is ${license.status}`
      })
    }

    // Check if license is expired
    if (license.expires_at) {
      const expiresAt = new Date(license.expires_at)
      if (expiresAt < new Date()) {
        // Update license status to expired
        await supabase
          .from('licenses')
          .update({ status: 'expired' })
          .eq('id', license.id)

        return NextResponse.json({
          valid: false,
          error: 'License has expired'
        })
      }
    }

    // Check if hardware ID is already activated
    const { data: existingActivation } = await supabase
      .from('activations')
      .select('*')
      .eq('license_id', license.id)
      .eq('hardware_id', hardwareId)
      .single()

    if (existingActivation) {
      // Update last seen
      await supabase
        .from('activations')
        .update({
          last_seen: new Date().toISOString(),
          machine_name: machineName || existingActivation.machine_name
        })
        .eq('id', existingActivation.id)

      return NextResponse.json({
        valid: true,
        license: {
          planType: license.plan_type,
          expiresAt: license.expires_at,
          activationsUsed: license.current_activations,
          maxActivations: license.max_activations,
        }
      })
    }

    // Check if max activations reached
    if (license.current_activations >= license.max_activations) {
      return NextResponse.json({
        valid: false,
        error: `Maximum activations reached (${license.max_activations})`
      })
    }

    // Create new activation
    const { error: activationError } = await supabase
      .from('activations')
      .insert({
        license_id: license.id,
        hardware_id: hardwareId,
        machine_name: machineName,
        activated_at: new Date().toISOString(),
        last_seen: new Date().toISOString(),
      })

    if (activationError) {
      console.error('Error creating activation:', activationError)
      return NextResponse.json({
        valid: false,
        error: 'Failed to activate license'
      })
    }

    // Update license activation count
    await supabase
      .from('licenses')
      .update({
        current_activations: license.current_activations + 1
      })
      .eq('id', license.id)

    return NextResponse.json({
      valid: true,
      license: {
        planType: license.plan_type,
        expiresAt: license.expires_at,
        activationsUsed: license.current_activations + 1,
        maxActivations: license.max_activations,
      }
    })
  } catch (error: any) {
    console.error('Error validating license:', error)
    return NextResponse.json(
      {
        valid: false,
        error: error.message || 'Failed to validate license'
      },
      { status: 500 }
    )
  }
}
