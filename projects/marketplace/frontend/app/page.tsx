export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            You Build.
            <span className="text-blue-400"> You Share.</span>
            <span className="text-green-400"> You Sell.</span>
          </h1>

          <p className="text-xl text-gray-300 mb-10">
            The AI-powered development marketplace where developers monetize
            their production-ready projects.
          </p>

          <div className="flex gap-4 justify-center">
            <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition">
              Start Building Free
            </button>
            <button className="px-8 py-4 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-semibold transition">
              Browse Marketplace
            </button>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="grid md:grid-cols-3 gap-8">
          {/* Build */}
          <div className="bg-gray-800 rounded-xl p-8 border border-gray-700">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Build with AI</h3>
            <p className="text-gray-400">
              Use our AI-powered framework to build production-ready projects faster than ever.
            </p>
          </div>

          {/* Share */}
          <div className="bg-gray-800 rounded-xl p-8 border border-gray-700">
            <div className="w-12 h-12 bg-purple-600 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Share Knowledge</h3>
            <p className="text-gray-400">
              Contribute to the collective Brain. Learn from others. Grow together.
            </p>
          </div>

          {/* Sell */}
          <div className="bg-gray-800 rounded-xl p-8 border border-gray-700">
            <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Sell & Earn</h3>
            <p className="text-gray-400">
              List your projects on the marketplace. Keep 90% of every sale. Fair and simple.
            </p>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="container mx-auto px-4 py-20">
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-12">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold text-white">90%</div>
              <div className="text-blue-100">To Creators</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white">1,300+</div>
              <div className="text-blue-100">Modules in Brain</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white">$49</div>
              <div className="text-blue-100">Pro Subscription</div>
            </div>
            <div>
              <div className="text-4xl font-bold text-white">Free</div>
              <div className="text-blue-100">Framework Access</div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="container mx-auto px-4 py-20 text-center">
        <h2 className="text-3xl font-bold text-white mb-4">
          Ready to start building?
        </h2>
        <p className="text-gray-400 mb-8">
          Join thousands of developers building and selling on MyWork.
        </p>
        <button className="px-8 py-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-semibold transition">
          Get Started Free
        </button>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-8">
        <div className="container mx-auto px-4 text-center text-gray-500">
          <p>Built with MyWork AI Framework</p>
        </div>
      </footer>
    </main>
  )
}
