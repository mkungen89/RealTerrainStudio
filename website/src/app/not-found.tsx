import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Mountain } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center px-4">
      <div className="text-center">
        <Mountain className="mx-auto mb-6 h-16 w-16 text-primary-500" />
        <h1 className="mb-4 text-6xl font-bold text-slate-900">404</h1>
        <h2 className="mb-4 text-2xl font-semibold text-slate-700">
          Page Not Found
        </h2>
        <p className="mb-8 text-slate-600">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link href="/">
          <Button variant="primary" size="lg">
            Go Home
          </Button>
        </Link>
      </div>
    </div>
  )
}
