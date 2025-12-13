import Link from 'next/link'
import { Book, Download, Play, Settings, FileText, HelpCircle } from 'lucide-react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

export default function DocsPage() {
  const sections = [
    {
      icon: Play,
      title: 'Getting Started',
      description: 'Install plugins and create your first terrain',
      links: [
        { name: 'Installation Guide', href: '#installation' },
        { name: 'Quick Start Tutorial', href: '#quick-start' },
        { name: 'System Requirements', href: '#requirements' },
      ],
    },
    {
      icon: Download,
      title: 'QGIS Plugin',
      description: 'Export real-world terrain data',
      links: [
        { name: 'Download Plugin', href: '#qgis-download' },
        { name: 'Configuration', href: '#qgis-config' },
        { name: 'Export Tutorial', href: '#qgis-export' },
      ],
    },
    {
      icon: FileText,
      title: 'UE5 Plugin',
      description: 'Import terrain into Unreal Engine',
      links: [
        { name: 'Download Plugin', href: '#ue5-download' },
        { name: 'Installation', href: '#ue5-install' },
        { name: 'Import Guide', href: '#ue5-import' },
      ],
    },
    {
      icon: Settings,
      title: 'Configuration',
      description: 'License management and settings',
      links: [
        { name: 'Activate License', href: '#activate' },
        { name: 'Game Profiles', href: '#profiles' },
        { name: 'Advanced Settings', href: '#advanced' },
      ],
    },
  ]

  return (
    <div className="py-12">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="mx-auto mb-12 max-w-3xl text-center">
          <Book className="mx-auto mb-4 h-12 w-12 text-primary-500" />
          <h1 className="mb-4 text-5xl font-bold text-slate-900">
            Documentation
          </h1>
          <p className="text-xl text-slate-600">
            Everything you need to transform real-world terrain into UE5
          </p>
        </div>

        {/* Quick Links Grid */}
        <div className="mb-16 grid gap-6 md:grid-cols-2">
          {sections.map((section) => {
            const Icon = section.icon
            return (
              <Card key={section.title}>
                <CardHeader>
                  <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100">
                    <Icon className="h-5 w-5 text-primary-600" />
                  </div>
                  <CardTitle>{section.title}</CardTitle>
                  <CardDescription>{section.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {section.links.map((link) => (
                      <li key={link.name}>
                        <a
                          href={link.href}
                          className="text-sm text-primary-600 hover:text-primary-700 hover:underline"
                        >
                          {link.name} →
                        </a>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Main Documentation Content */}
        <div className="mx-auto max-w-4xl space-y-12">
          {/* Installation */}
          <section id="installation">
            <h2 className="mb-4 text-3xl font-bold text-slate-900">Installation</h2>

            <h3 className="mb-3 text-xl font-semibold text-slate-800">System Requirements</h3>
            <Card className="mb-6">
              <CardContent className="pt-6">
                <div className="grid gap-6 md:grid-cols-2">
                  <div>
                    <h4 className="mb-2 font-semibold text-slate-900">QGIS Plugin</h4>
                    <ul className="space-y-1 text-sm text-slate-600">
                      <li>• QGIS 3.22 or higher</li>
                      <li>• Python 3.9+</li>
                      <li>• 4GB RAM minimum</li>
                      <li>• Internet connection</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="mb-2 font-semibold text-slate-900">UE5 Plugin</h4>
                    <ul className="space-y-1 text-sm text-slate-600">
                      <li>• Unreal Engine 5.3+</li>
                      <li>• Visual Studio 2022</li>
                      <li>• 8GB RAM minimum</li>
                      <li>• DirectX 12 compatible GPU</li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <h3 className="mb-3 text-xl font-semibold text-slate-800" id="qgis-download">QGIS Plugin Installation</h3>
            <ol className="space-y-3 text-slate-700">
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  1
                </span>
                <span>Download the latest RealTerrain QGIS plugin from your <Link href="/dashboard" className="text-primary-600 hover:underline">dashboard</Link></span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  2
                </span>
                <span>Open QGIS and go to Plugins → Manage and Install Plugins</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  3
                </span>
                <span>Click "Install from ZIP" and select the downloaded file</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  4
                </span>
                <span>Restart QGIS and activate your license key</span>
              </li>
            </ol>
          </section>

          {/* Quick Start */}
          <section id="quick-start">
            <h2 className="mb-4 text-3xl font-bold text-slate-900">Quick Start Guide</h2>
            <p className="mb-4 text-slate-600">
              Follow these steps to create your first terrain in under 5 minutes:
            </p>

            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Step 1: Select Area</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-700">
                    Open QGIS and use the RealTerrain panel to select any area on Earth.
                    You can search by location name or manually draw a bounding box.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Step 2: Choose Profile</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-700">
                    Select from 13 game-optimized presets (FPS, RPG, Flight Sim, etc.) or
                    customize export settings for your specific needs.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Step 3: Export Terrain</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-700">
                    Click "Export" and wait while RealTerrain downloads elevation data,
                    satellite imagery, and OpenStreetMap data. You'll get a single .rterrain file.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Step 4: Import to UE5</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-slate-700">
                    In Unreal Engine 5, use the RealTerrain import tool to load your .rterrain file.
                    The terrain will be automatically generated with materials, roads, and objects.
                  </p>
                </CardContent>
              </Card>
            </div>
          </section>

          {/* License Activation */}
          <section id="activate">
            <h2 className="mb-4 text-3xl font-bold text-slate-900">License Activation</h2>
            <p className="mb-4 text-slate-600">
              After purchasing a license, you'll receive a license key. Follow these steps to activate:
            </p>

            <ol className="space-y-3 text-slate-700">
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  1
                </span>
                <span>Copy your license key from the <Link href="/dashboard" className="text-primary-600 hover:underline">dashboard</Link></span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  2
                </span>
                <span>Open QGIS and go to RealTerrain → Settings → License</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  3
                </span>
                <span>Paste your license key and click "Activate"</span>
              </li>
              <li className="flex items-start">
                <span className="mr-3 flex h-6 w-6 items-center justify-center rounded-full bg-primary-500 text-sm font-bold text-white">
                  4
                </span>
                <span>You can activate on up to 3 machines</span>
              </li>
            </ol>
          </section>

          {/* Help Section */}
          <section>
            <Card className="border-primary-200 bg-primary-50">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <HelpCircle className="h-6 w-6 text-primary-600" />
                  <CardTitle>Need More Help?</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="mb-4 text-slate-700">
                  Can't find what you're looking for? We're here to help!
                </p>
                <div className="flex flex-wrap gap-3">
                  <Link href="/help">
                    <Button variant="primary">Contact Support</Button>
                  </Link>
                  <Link href="/community">
                    <Button variant="outline">Join Community</Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </section>
        </div>
      </div>
    </div>
  )
}
