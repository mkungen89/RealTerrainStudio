import Link from 'next/link'
import { Mountain, Zap, Globe, Layers, Download, Sparkles, ArrowRight, CheckCircle, MapPin } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export default function HomePage() {
  const features = [
    {
      icon: Globe,
      title: 'Real-World Data',
      description: 'Import elevation data from SRTM, ASTER, and LiDAR. Download high-resolution satellite imagery from Sentinel-2 and Mapbox.',
    },
    {
      icon: Layers,
      title: 'Complete Package',
      description: 'Everything in one .rterrain file: heightmaps, textures, materials, roads, buildings, and vegetation data.',
    },
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Select an area, click export, and get production-ready terrain in minutes. No complex GIS workflows required.',
    },
    {
      icon: Mountain,
      title: 'Game-Optimized',
      description: '13 preset profiles for different game types: FPS, RPG, Flight Sim, Racing, and more. Automatically optimized for performance.',
    },
    {
      icon: Download,
      title: 'One-Click Import',
      description: 'Import .rterrain files into Unreal Engine 5 with a single click. Automatic landscape generation and material setup.',
    },
    {
      icon: Sparkles,
      title: 'OSM Integration',
      description: 'Automatic road splines, building placement, and vegetation spawning from OpenStreetMap data.',
    },
  ]

  const workflow = [
    {
      step: 1,
      title: 'Select Area',
      description: 'Use QGIS to select any area on Earth. From city blocks to entire mountain ranges.',
    },
    {
      step: 2,
      title: 'Choose Profile',
      description: 'Pick from 13 game-optimized presets or customize your export settings.',
    },
    {
      step: 3,
      title: 'Export Terrain',
      description: 'Click export and get a single .rterrain file with everything you need.',
    },
    {
      step: 4,
      title: 'Import to UE5',
      description: 'One-click import into Unreal Engine 5. Production-ready in seconds.',
    },
  ]

  const stats = [
    { value: '1000+', label: 'Happy Users' },
    { value: '50,000+', label: 'Terrains Created' },
    { value: '100km²', label: 'Max Area (Pro)' },
    { value: '< 5 min', label: 'Average Export Time' },
  ]

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50 py-20 md:py-32">
        <div className="absolute inset-0 grid-pattern opacity-50" />
        <div className="container relative mx-auto px-4">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mb-6 inline-flex items-center rounded-full bg-primary-100 px-4 py-2 text-sm font-medium text-primary-700">
              <Sparkles className="mr-2 h-4 w-4" />
              Transform Earth into Engine
            </div>
            <h1 className="mb-6 text-5xl font-bold tracking-tight text-slate-900 md:text-7xl">
              From Earth to Engine
            </h1>
            <p className="mb-8 text-xl text-slate-600 md:text-2xl">
              Transform real-world terrain into production-ready Unreal Engine 5 landscapes in minutes.
              No GIS expertise required.
            </p>
            <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
              <Link href="/signup">
                <Button variant="primary" size="lg" className="gap-2">
                  Get Started Free
                  <ArrowRight className="h-5 w-5" />
                </Button>
              </Link>
              <Link href="/docs">
                <Button variant="outline" size="lg">
                  View Documentation
                </Button>
              </Link>
            </div>
            <div className="mt-12 flex flex-wrap items-center justify-center gap-8 text-sm text-slate-600">
              {stats.map((stat) => (
                <div key={stat.label} className="text-center">
                  <div className="text-2xl font-bold text-primary-600">{stat.value}</div>
                  <div className="text-slate-600">{stat.label}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="mx-auto mb-16 max-w-3xl text-center">
            <h2 className="mb-4 text-4xl font-bold text-slate-900 md:text-5xl">
              Everything You Need
            </h2>
            <p className="text-xl text-slate-600">
              Professional terrain creation pipeline with real-world data integration
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <Card key={feature.title} className="transition-shadow hover:shadow-lg">
                  <CardHeader>
                    <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-primary-100">
                      <Icon className="h-6 w-6 text-primary-600" />
                    </div>
                    <CardTitle>{feature.title}</CardTitle>
                    <CardDescription className="mt-2">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Workflow Section */}
      <section className="bg-slate-50 py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="mx-auto mb-16 max-w-3xl text-center">
            <h2 className="mb-4 text-4xl font-bold text-slate-900 md:text-5xl">
              Simple Workflow
            </h2>
            <p className="text-xl text-slate-600">
              From satellite data to UE5 in four easy steps
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {workflow.map((item) => (
              <div key={item.step} className="relative">
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-primary-500 text-lg font-bold text-white">
                  {item.step}
                </div>
                <h3 className="mb-2 text-xl font-semibold text-slate-900">
                  {item.title}
                </h3>
                <p className="text-slate-600">{item.description}</p>
                {item.step < 4 && (
                  <div className="absolute left-6 top-12 hidden h-full w-0.5 bg-primary-200 lg:block" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases Section */}
      <section className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="mx-auto mb-16 max-w-3xl text-center">
            <h2 className="mb-4 text-4xl font-bold text-slate-900 md:text-5xl">
              Built For Creators
            </h2>
            <p className="text-xl text-slate-600">
              Trusted by game developers, architects, and filmmakers
            </p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Game Development</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Realistic open-world environments</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>FPS and RPG map creation</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Flight and racing simulations</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Architecture & Visualization</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Site context modeling</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Urban planning visualization</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Real-world asset integration</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Film & Virtual Production</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Location scouting</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Virtual set extensions</span>
                  </li>
                  <li className="flex items-start">
                    <CheckCircle className="mr-2 h-5 w-5 text-primary-500" />
                    <span>Previz and planning</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-primary-600 to-secondary-600 py-20 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="mb-4 text-4xl font-bold md:text-5xl">
            Ready to Build Your World?
          </h2>
          <p className="mb-8 text-xl opacity-90">
            Start transforming real-world terrain into stunning UE5 landscapes today
          </p>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/signup">
              <Button
                variant="default"
                size="lg"
                className="bg-white text-primary-600 hover:bg-slate-100"
              >
                Get Started Free
              </Button>
            </Link>
            <Link href="/pricing">
              <Button
                variant="outline"
                size="lg"
                className="border-white text-white hover:bg-white/10"
              >
                View Pricing
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
