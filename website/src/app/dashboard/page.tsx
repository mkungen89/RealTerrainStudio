'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Key, Download, Calendar, TrendingUp, ExternalLink, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { createSupabaseClient } from '@/lib/supabase'
import { formatDate, formatFileSize } from '@/lib/utils'

export default function DashboardPage() {
  const [user, setUser] = useState<any>(null)
  const [licenses, setLicenses] = useState<any[]>([])
  const [recentExports, setRecentExports] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [copiedKey, setCopiedKey] = useState<string | null>(null)
  const router = useRouter()
  const supabase = createSupabaseClient()

  useEffect(() => {
    checkUser()
    fetchUserData()
  }, [])

  const checkUser = async () => {
    const { data: { user } } = await supabase.auth.getUser()

    if (!user) {
      router.push('/login')
      return
    }

    setUser(user)
  }

  const fetchUserData = async () => {
    try {
      const { data: { user } } = await supabase.auth.getUser()
      if (!user) return

      // Fetch licenses
      const { data: licensesData, error: licensesError } = await supabase
        .from('licenses')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })

      if (licensesError) throw licensesError
      setLicenses(licensesData || [])

      // Fetch recent exports
      const { data: exportsData, error: exportsError } = await supabase
        .from('exports')
        .select('*')
        .eq('user_id', user.id)
        .order('created_at', { ascending: false })
        .limit(5)

      if (exportsError) throw exportsError
      setRecentExports(exportsData || [])
    } catch (error) {
      console.error('Error fetching user data:', error)
    } finally {
      setLoading(false)
    }
  }

  const copyLicenseKey = async (key: string) => {
    await navigator.clipboard.writeText(key)
    setCopiedKey(key)
    setTimeout(() => setCopiedKey(null), 2000)
  }

  const getStats = () => {
    const activeLicense = licenses.find(l => l.status === 'active')
    const totalExports = recentExports.length
    const thisMonthExports = recentExports.filter(e => {
      const exportDate = new Date(e.created_at)
      const now = new Date()
      return exportDate.getMonth() === now.getMonth() && exportDate.getFullYear() === now.getFullYear()
    }).length

    return {
      planType: activeLicense?.plan_type || 'None',
      activations: activeLicense?.current_activations || 0,
      maxActivations: activeLicense?.max_activations || 3,
      exportsThisMonth: thisMonthExports,
      totalExports,
    }
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg text-slate-600">Loading...</div>
      </div>
    )
  }

  const stats = getStats()

  return (
    <div className="container mx-auto px-4 py-12">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-slate-900">Dashboard</h1>
        <p className="mt-2 text-slate-600">
          Welcome back, {user?.user_metadata?.full_name || user?.email}
        </p>
      </div>

      {/* Stats Grid */}
      <div className="mb-8 grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Current Plan</CardDescription>
            <CardTitle className="text-3xl capitalize">{stats.planType}</CardTitle>
          </CardHeader>
          <CardContent>
            <Link href="/pricing">
              <Button variant="outline" size="sm" className="w-full">
                Upgrade Plan
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Activations</CardDescription>
            <CardTitle className="text-3xl">
              {stats.activations} / {stats.maxActivations}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-600">
              {stats.maxActivations - stats.activations} slots available
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Exports This Month</CardDescription>
            <CardTitle className="text-3xl">{stats.exportsThisMonth}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center text-sm text-green-600">
              <TrendingUp className="mr-1 h-4 w-4" />
              Total: {stats.totalExports}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Account Status</CardDescription>
            <CardTitle className="text-3xl text-green-600">Active</CardTitle>
          </CardHeader>
          <CardContent>
            <Link href="/dashboard/billing">
              <Button variant="outline" size="sm" className="w-full">
                Manage Billing
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        {/* License Keys */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>License Keys</CardTitle>
                <CardDescription>Your active license keys</CardDescription>
              </div>
              <Key className="h-6 w-6 text-slate-400" />
            </div>
          </CardHeader>
          <CardContent>
            {licenses.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-slate-600 mb-4">No active licenses</p>
                <Link href="/pricing">
                  <Button variant="primary">Get a License</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {licenses.map((license) => (
                  <div
                    key={license.id}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-sm font-medium capitalize text-slate-900">
                        {license.plan_type}
                      </span>
                      <span
                        className={`rounded-full px-2 py-1 text-xs font-medium ${
                          license.status === 'active'
                            ? 'bg-green-100 text-green-700'
                            : 'bg-slate-100 text-slate-700'
                        }`}
                      >
                        {license.status}
                      </span>
                    </div>
                    <div className="flex items-center justify-between rounded-md bg-slate-50 p-3">
                      <code className="text-sm font-mono text-slate-700">
                        {license.license_key}
                      </code>
                      <button
                        onClick={() => copyLicenseKey(license.license_key)}
                        className="ml-2 text-slate-400 hover:text-slate-600"
                      >
                        {copiedKey === license.license_key ? (
                          <Check className="h-4 w-4 text-green-600" />
                        ) : (
                          <Copy className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                    <div className="mt-2 text-xs text-slate-500">
                      Created: {formatDate(license.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Exports */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Exports</CardTitle>
                <CardDescription>Your latest terrain exports</CardDescription>
              </div>
              <Download className="h-6 w-6 text-slate-400" />
            </div>
          </CardHeader>
          <CardContent>
            {recentExports.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-slate-600 mb-4">No exports yet</p>
                <Link href="/docs">
                  <Button variant="outline">Get Started</Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {recentExports.map((exp) => (
                  <div
                    key={exp.id}
                    className="rounded-lg border border-slate-200 p-4"
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-sm font-medium text-slate-900">
                        {exp.profile}
                      </span>
                      <span className="text-xs text-slate-500">
                        {formatFileSize(exp.file_size)}
                      </span>
                    </div>
                    <div className="text-xs text-slate-500">
                      <Calendar className="mr-1 inline h-3 w-3" />
                      {formatDate(exp.created_at)}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <div className="mt-8">
        <h2 className="mb-4 text-2xl font-bold text-slate-900">Quick Links</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Link href="/docs">
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <h3 className="font-semibold text-slate-900">Documentation</h3>
                  <p className="text-sm text-slate-600">Learn how to use RealTerrain</p>
                </div>
                <ExternalLink className="h-5 w-5 text-slate-400" />
              </CardContent>
            </Card>
          </Link>

          <Link href="/docs/download">
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <h3 className="font-semibold text-slate-900">Download Plugin</h3>
                  <p className="text-sm text-slate-600">Get the QGIS and UE5 plugins</p>
                </div>
                <ExternalLink className="h-5 w-5 text-slate-400" />
              </CardContent>
            </Card>
          </Link>

          <Link href="/help">
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center justify-between p-6">
                <div>
                  <h3 className="font-semibold text-slate-900">Get Help</h3>
                  <p className="text-sm text-slate-600">Contact support</p>
                </div>
                <ExternalLink className="h-5 w-5 text-slate-400" />
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  )
}
