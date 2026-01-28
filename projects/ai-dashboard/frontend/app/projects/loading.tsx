export default function ProjectsLoading() {
  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="h-8 w-48 bg-gray-200 rounded animate-pulse mb-2"></div>
        <div className="h-4 w-64 bg-gray-200 rounded animate-pulse"></div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-5">
            <div className="flex items-start justify-between mb-3">
              <div className="h-6 w-40 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-6 w-16 bg-gray-200 rounded animate-pulse"></div>
            </div>
            <div className="h-4 w-full bg-gray-200 rounded animate-pulse mb-2"></div>
            <div className="h-4 w-3/4 bg-gray-200 rounded animate-pulse mb-4"></div>
            <div className="flex gap-2 mb-3">
              <div className="h-5 w-16 bg-gray-200 rounded-full animate-pulse"></div>
              <div className="h-5 w-20 bg-gray-200 rounded-full animate-pulse"></div>
              <div className="h-5 w-14 bg-gray-200 rounded-full animate-pulse"></div>
            </div>
            <div className="flex gap-4">
              <div className="h-4 w-20 bg-gray-200 rounded animate-pulse"></div>
              <div className="h-4 w-16 bg-gray-200 rounded animate-pulse"></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
