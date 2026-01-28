export default function NewsLoading() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse mb-2"></div>
        <div className="h-4 w-64 bg-gray-200 rounded animate-pulse"></div>
      </div>

      <div className="space-y-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-4 flex gap-4">
            <div className="w-24 h-24 bg-gray-200 rounded animate-pulse flex-shrink-0"></div>
            <div className="flex-1">
              <div className="h-5 w-3/4 bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="h-4 w-full bg-gray-200 rounded animate-pulse mb-2"></div>
              <div className="h-4 w-1/2 bg-gray-200 rounded animate-pulse mb-3"></div>
              <div className="flex gap-2">
                <div className="h-5 w-20 bg-gray-200 rounded animate-pulse"></div>
                <div className="h-5 w-24 bg-gray-200 rounded animate-pulse"></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
