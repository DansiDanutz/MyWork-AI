export default function YouTubeBotLoading() {
  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <div className="h-8 w-48 bg-gray-200 rounded animate-pulse mb-2"></div>
          <div className="h-4 w-64 bg-gray-200 rounded animate-pulse"></div>
        </div>
        <div className="h-10 w-32 bg-gray-200 rounded animate-pulse"></div>
      </div>

      <div className="space-y-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="h-5 w-64 bg-gray-200 rounded animate-pulse mb-2"></div>
                <div className="h-4 w-full bg-gray-200 rounded animate-pulse mb-2"></div>
                <div className="flex gap-2">
                  <div className="h-6 w-20 bg-gray-200 rounded-full animate-pulse"></div>
                  <div className="h-6 w-24 bg-gray-200 rounded-full animate-pulse"></div>
                </div>
              </div>
              <div className="h-8 w-24 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
