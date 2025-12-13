import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with proper precedence
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/**
 * Format a date to a readable string
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

/**
 * Format a number as currency
 */
export function formatCurrency(amount: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount)
}

/**
 * Format bytes to human-readable file size
 */
export function formatFileSize(bytes: number): string {
  const units = ['B', 'KB', 'MB', 'GB', 'TB']
  let size = bytes
  let unitIndex = 0

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }

  return `${size.toFixed(2)} ${units[unitIndex]}`
}

/**
 * Calculate area in km² from bounds
 */
export function calculateArea(bounds: {
  north: number
  south: number
  east: number
  west: number
}): number {
  const EARTH_RADIUS_KM = 6371
  const { north, south, east, west } = bounds

  // Convert to radians
  const lat1 = (south * Math.PI) / 180
  const lat2 = (north * Math.PI) / 180
  const lon1 = (west * Math.PI) / 180
  const lon2 = (east * Math.PI) / 180

  // Calculate area using spherical geometry
  const latDiff = lat2 - lat1
  const lonDiff = lon2 - lon1

  const area =
    EARTH_RADIUS_KM *
    EARTH_RADIUS_KM *
    Math.abs(Math.sin(lat1) - Math.sin(lat2)) *
    lonDiff

  return Math.abs(area)
}

/**
 * Generate a random hardware ID (for testing)
 */
export function generateHardwareId(): string {
  return Array.from({ length: 32 }, () =>
    Math.floor(Math.random() * 16).toString(16)
  ).join('')
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Truncate text to a maximum length
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

/**
 * Sleep for a given number of milliseconds
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/**
 * Debounce a function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

/**
 * Check if user can export based on plan limits
 */
export function canExport(
  planType: 'hobby' | 'professional' | 'enterprise',
  exportsThisMonth: number,
  areaKm2: number
): { allowed: boolean; reason?: string } {
  const limits = {
    hobby: { exportsPerMonth: 10, maxAreaKm2: 25 },
    professional: { exportsPerMonth: -1, maxAreaKm2: 100 },
    enterprise: { exportsPerMonth: -1, maxAreaKm2: -1 },
  }

  const limit = limits[planType]

  // Check export limit
  if (limit.exportsPerMonth !== -1 && exportsThisMonth >= limit.exportsPerMonth) {
    return {
      allowed: false,
      reason: `You've reached your monthly export limit (${limit.exportsPerMonth}). Upgrade to continue.`,
    }
  }

  // Check area limit
  if (limit.maxAreaKm2 !== -1 && areaKm2 > limit.maxAreaKm2) {
    return {
      allowed: false,
      reason: `Selected area (${areaKm2.toFixed(1)}km²) exceeds your plan limit (${limit.maxAreaKm2}km²). Upgrade to export larger areas.`,
    }
  }

  return { allowed: true }
}
