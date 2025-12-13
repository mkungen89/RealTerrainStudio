import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { Header } from '@/components/Header'
import { Footer } from '@/components/Footer'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'RealTerrain Studio - From Earth to Engine',
  description: 'Transform real-world terrain into production-ready Unreal Engine 5 landscapes. Export satellite data, elevation maps, and OpenStreetMap data in minutes.',
  keywords: ['terrain', 'unreal engine', 'qgis', 'elevation', 'srtm', 'game development', 'landscape', 'satellite imagery'],
  authors: [{ name: 'RealTerrain Studio' }],
  openGraph: {
    title: 'RealTerrain Studio - From Earth to Engine',
    description: 'Transform real-world terrain into production-ready Unreal Engine 5 landscapes.',
    type: 'website',
    url: 'https://realterrainstudio.com',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'RealTerrain Studio - From Earth to Engine',
    description: 'Transform real-world terrain into production-ready Unreal Engine 5 landscapes.',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen flex flex-col">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
