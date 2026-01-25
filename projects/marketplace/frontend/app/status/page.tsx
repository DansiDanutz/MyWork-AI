export const dynamic = 'force-dynamic'

type ServiceCheck = {
  name: string
  url: string
  expectJson?: boolean
}

type ServiceResult = {
  name: string
  url: string
  ok: boolean
  statusCode: number | null
  detail: string
  latencyMs: number | null
}

const SERVICES: ServiceCheck[] = [
  {
    name: 'Marketplace Frontend',
    url: 'https://mywork-marketplace.vercel.app',
  },
  {
    name: 'Marketplace API',
    url: 'https://mywork-ai-production.up.railway.app/health',
    expectJson: true,
  },
  {
    name: 'Task Tracker',
    url: 'https://mywork-task-tracker.vercel.app/api/health',
    expectJson: true,
  },
]

async function checkService(service: ServiceCheck): Promise<ServiceResult> {
  const started = Date.now()

  try {
    const response = await fetch(service.url, { cache: 'no-store' })
    const latencyMs = Date.now() - started
    let detail = `HTTP ${response.status}`
    let ok = response.ok

    if (service.expectJson) {
      try {
        const data = (await response.json()) as { status?: string } | null
        if (data?.status) {
          detail = data.status
          ok = ok && data.status.toLowerCase() === 'healthy'
        }
      } catch (error) {
        detail = 'Invalid JSON response'
        ok = false
      }
    }

    return {
      name: service.name,
      url: service.url,
      ok,
      statusCode: response.status,
      detail,
      latencyMs,
    }
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Request failed'
    return {
      name: service.name,
      url: service.url,
      ok: false,
      statusCode: null,
      detail: message,
      latencyMs: null,
    }
  }
}

export default async function StatusPage() {
  const results = await Promise.all(SERVICES.map(checkService))
  const checkedAt = new Date().toISOString()

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h1 className="text-4xl font-bold text-white">System Status</h1>
              <p className="text-gray-400 mt-2">
                Public health checks for the MyWork Marketplace ecosystem.
              </p>
            </div>
            <span className="text-sm text-gray-500">
              Last checked: {checkedAt}
            </span>
          </div>

          <div className="bg-gray-900/60 border border-gray-700 rounded-2xl p-6">
            <div className="grid gap-4">
              {results.map((result) => (
                <div
                  key={result.name}
                  className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-4 rounded-xl border border-gray-800 bg-gray-900/70"
                >
                  <div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                          result.ok
                            ? 'bg-green-500/20 text-green-300'
                            : 'bg-red-500/20 text-red-300'
                        }`}
                      >
                        {result.ok ? 'UP' : 'DOWN'}
                      </span>
                      <h2 className="text-lg font-semibold text-white">
                        {result.name}
                      </h2>
                    </div>
                    <p className="text-sm text-gray-400 mt-2">
                      {result.detail}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{result.url}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">Latency</div>
                    <div className="text-xl font-semibold text-white">
                      {result.latencyMs !== null ? `${result.latencyMs}ms` : '—'}
                    </div>
                    <div className="text-xs text-gray-500 mt-1">
                      Status: {result.statusCode ?? 'N/A'}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-8 text-sm text-gray-500">
            Status checks run server-side on every request. If you see a failure,
            refresh in a few seconds to confirm.
          </div>
        </div>
      </div>
    </main>
  )
}
