import { useState } from 'react'

function RequestCard({ request, onApprove, onReject }) {
  const [isProcessing, setIsProcessing] = useState(false)

  const handleApprove = async () => {
    setIsProcessing(true)
    try {
      await onApprove(request.id)
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReject = async () => {
    setIsProcessing(true)
    try {
      await onReject(request.id)
    } finally {
      setIsProcessing(false)
    }
  }

  // Format amount if present
  const amount = request.args?.amount
  const amountDisplay = amount ? `$${amount.toLocaleString()}` : 'N/A'

  // Format timestamp
  const createdDate = request.created_at ? new Date(request.created_at).toLocaleString() : 'Unknown'

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-lg p-6 hover:border-gray-700 transition-all shadow-lg">
      {/* Header with Resource and Risk Badge */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="text-xl font-bold text-white mb-1">
            {request.resource}
          </h3>
          <p className="text-sm text-gray-400">Action: <span className="text-gray-300 font-mono">{request.action}</span></p>
        </div>
        <span className="px-3 py-1 bg-red-900/30 text-red-400 border border-red-800 rounded-full text-xs font-semibold uppercase">
          High Risk
        </span>
      </div>

      {/* Request Details */}
      <div className="space-y-3 mb-4">
        {amount && (
          <div className="flex items-center gap-2">
            <span className="text-gray-500 text-sm">Amount:</span>
            <span className="text-emerald-400 font-bold text-lg">{amountDisplay}</span>
          </div>
        )}
        
        <div>
          <span className="text-gray-500 text-sm">Reason:</span>
          <p className="text-gray-300 mt-1">{request.reason}</p>
        </div>

        <div className="bg-black/50 rounded p-3 border border-gray-800">
          <span className="text-gray-500 text-xs uppercase mb-1 block">Arguments</span>
          <pre className="text-xs text-gray-400 font-mono overflow-x-auto">
            {JSON.stringify(request.args, null, 2)}
          </pre>
        </div>

        <div className="flex items-center gap-4 text-xs text-gray-500">
          <span>ID: <span className="text-gray-400 font-mono">{request.id.slice(0, 8)}...</span></span>
          <span>Created: <span className="text-gray-400">{createdDate}</span></span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mt-6">
        <button
          onClick={handleApprove}
          disabled={isProcessing || request.status !== 'PENDING'}
          className="flex-1 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-4 rounded transition-colors border border-emerald-500/50"
        >
          {isProcessing ? 'Processing...' : 'AUTHORIZE'}
        </button>
        <button
          onClick={handleReject}
          disabled={isProcessing || request.status !== 'PENDING'}
          className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white font-semibold py-2.5 px-4 rounded transition-colors border border-red-500/50"
        >
          {isProcessing ? 'Processing...' : 'BLOCK'}
        </button>
      </div>

      {/* Status Badge */}
      {request.status !== 'PENDING' && (
        <div className="mt-3 pt-3 border-t border-gray-800">
          <span className={`text-xs font-semibold ${
            request.status === 'APPROVED' ? 'text-emerald-400' : 'text-red-400'
          }`}>
            Status: {request.status}
          </span>
        </div>
      )}
    </div>
  )
}

export default RequestCard


