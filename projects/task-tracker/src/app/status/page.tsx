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
    name: 'Task Tracker Frontend',
    url: 'https://mywork-task-tracker.vercel.app',
  },
  {
    name: 'Task Tracker API',
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
        if (typeof data?.status === 'string') {
          detail = data.status
          const normalized = data.status.toLowerCase()
          ok = ok && (normalized === 'healthy' || normalized === 'ok' || normalized === 'pass')
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
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto">
          <div className="flex flex-col gap-2 mb-10">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">
              Task Tracker Status
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Live health checks for the Task Tracker experience.
            </p>
            <span className="text-sm text-gray-500 dark:text-gray-500">
              Last checked: {checkedAt}
            </span>
          </div>

          <div className="bg-white/80 dark:bg-gray-900/60 border border-gray-200 dark:border-gray-700 rounded-2xl p-6 shadow-sm">
            <div className="grid gap-4">
              {results.map((result) => (
                <div
                  key={result.name}
                  className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 p-4 rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900"
                >
                  <div>
                    <div className="flex items-center gap-3">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold ${
                          result.ok
                            ? 'bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-300'
                            : 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-300'
                        }`}
                      >
                        {result.ok ? 'UP' : 'DOWN'}
                      </span>
                      <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {result.name}
                      </h2>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
                      {result.detail}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{result.url}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Latency</div>
                    <div className="text-xl font-semibold text-gray-900 dark:text-white">
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
