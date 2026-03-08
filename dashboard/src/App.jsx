import { useState, useEffect } from 'react'
import RequestCard from './components/RequestCard'
import SimulationView from './components/SimulationView'
import PoliciesView from './components/PoliciesView'

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : ''

function App() {
  const [activeTab, setActiveTab] = useState('simulation')
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchRequests = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/requests`)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      const data = await response.json()
      setRequests(data.requests || [])
      setError(null)
    } catch (err) {
      console.error('Error fetching requests:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchRequests()
    const interval = setInterval(() => {
      fetchRequests()
    }, 2000)
    return () => clearInterval(interval)
  }, [])

  const handleApprove = async (requestId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/requests/${requestId}/approve`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      await fetchRequests()
    } catch (err) {
      console.error('Error approving request:', err)
      alert(`Failed to approve: ${err.message}`)
    }
  }

  const handleReject = async (requestId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/v1/requests/${requestId}/reject`, {
        method: 'POST',
      })
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      await fetchRequests()
    } catch (err) {
      console.error('Error rejecting request:', err)
      alert(`Failed to reject: ${err.message}`)
    }
  }

  const pendingRequests = requests.filter((req) => req.status === 'PENDING')

  return (
    <div className="min-h-screen bg-black">
      {/* Header */}
      <header className="border-b border-gray-800 bg-gray-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-[1600px] mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                SudoMode <span className="text-gray-500">//</span>{' '}
                <span className="text-emerald-400">Sentinel</span>
              </h1>
              <p className="text-sm text-gray-500 mt-1">AI Governance & Authorization Platform</p>
            </div>

            {/* Tab Navigation */}
            <div className="flex items-center gap-1 bg-gray-800/50 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('simulation')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'simulation'
                  ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                  }`}
              >
                ⚡ Live Simulation
              </button>
              <button
                onClick={() => setActiveTab('approvals')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all flex items-center gap-2 ${activeTab === 'approvals'
                  ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                  }`}
              >
                🔒 Approvals
                {pendingRequests.length > 0 && (
                  <span className="bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full min-w-[20px] text-center animate-pulse">
                    {pendingRequests.length}
                  </span>
                )}
              </button>
              <button
                onClick={() => setActiveTab('policies')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${activeTab === 'policies'
                  ? 'bg-emerald-600 text-white shadow-lg shadow-emerald-900/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-700/50'
                  }`}
              >
                📋 Active Policies
              </button>
            </div>

            <div className="text-right">
              <div className="text-xs text-gray-500">Pending Requests</div>
              <div className="text-2xl font-bold text-emerald-400">{pendingRequests.length}</div>
            </div>
          </div>
        </div>
      </header>

      {/* Tab Content — all always mounted, toggle with hidden */}
      <div className={activeTab !== 'simulation' ? 'hidden' : ''}>
        <SimulationView />
      </div>

      <div className={activeTab !== 'approvals' ? 'hidden' : ''}>
        <main className="max-w-7xl mx-auto px-6 py-8">
          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="text-gray-500">Loading requests...</div>
            </div>
          )}

          {error && (
            <div className="bg-red-900/20 border border-red-800 rounded-lg p-4 mb-6">
              <p className="text-red-400">Error: {error}</p>
              <p className="text-sm text-gray-500 mt-2">
                Make sure the backend server is running on {API_BASE_URL}
              </p>
            </div>
          )}

          {!loading && !error && pendingRequests.length === 0 && (
            <div className="text-center py-20">
              <div className="inline-block p-8 bg-gray-900 border border-gray-800 rounded-lg">
                <div className="text-6xl mb-4">🔒</div>
                <h2 className="text-2xl font-bold text-white mb-2">No Pending Requests</h2>
                <p className="text-gray-500">
                  All clear. No actions require approval at this time.
                </p>
                <p className="text-gray-600 text-sm mt-3">
                  Try requesting a refund between $20-$100 in the Live Simulation tab to trigger a HITL request.
                </p>
              </div>
            </div>
          )}

          {!loading && !error && pendingRequests.length > 0 && (
            <>
              <div className="mb-6">
                <h2 className="text-xl font-semibold text-white mb-2">Pending Approvals</h2>
                <p className="text-gray-500 text-sm">
                  Review and authorize or block AI agent actions
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pendingRequests.map((request) => (
                  <RequestCard
                    key={request.id}
                    request={request}
                    onApprove={handleApprove}
                    onReject={handleReject}
                  />
                ))}
              </div>
            </>
          )}

          {!loading && !error && requests.length > pendingRequests.length && (
            <div className="mt-12 pt-8 border-t border-gray-800">
              <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {requests
                  .filter((req) => req.status !== 'PENDING')
                  .map((request) => (
                    <RequestCard
                      key={request.id}
                      request={request}
                      onApprove={handleApprove}
                      onReject={handleReject}
                    />
                  ))}
              </div>
            </div>
          )}
        </main>
      </div>

      <div className={activeTab !== 'policies' ? 'hidden' : ''}>
        <PoliciesView />
      </div>
    </div>
  )
}

export default App
