import { useState, useRef, useEffect, useCallback } from 'react'

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : ''

export default function SimulationView() {
  const [messages, setMessages] = useState([
    {
      role: 'system',
      text: '🛡️ You are chatting with the AI Support Agent. Try requesting refunds at different amounts to see the 3-tier escalation policy.',
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [gatewayEvents, setGatewayEvents] = useState([])
  const [pendingApproval, setPendingApproval] = useState(null)
  const chatEndRef = useRef(null)
  const monitorEndRef = useRef(null)
  const pollIntervalRef = useRef(null)

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  useEffect(() => {
    monitorEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [gatewayEvents])
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
    }
  }, [])

  const startPolling = useCallback((requestId) => {
    if (pollIntervalRef.current) clearInterval(pollIntervalRef.current)
    pollIntervalRef.current = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/simulation/poll/${requestId}`)
        if (!res.ok) return
        const data = await res.json()
        const now = new Date().toLocaleTimeString()

        if (data.status === 'APPROVED') {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
          setPendingApproval(null)
          setMessages((prev) => [...prev, { role: 'agent', text: data.agent_reply }])
          setGatewayEvents((prev) => [
            ...prev,
            { type: 'approved', time: now, text: 'APPROVED BY MANAGER', detail: `Request ${requestId.slice(0, 8)}... approved. Refund processing.` },
          ])
        } else if (data.status === 'REJECTED') {
          clearInterval(pollIntervalRef.current)
          pollIntervalRef.current = null
          setPendingApproval(null)
          setMessages((prev) => [...prev, { role: 'agent', text: data.agent_reply }])
          setGatewayEvents((prev) => [
            ...prev,
            { type: 'rejected', time: now, text: 'REJECTED BY MANAGER', detail: `Request ${requestId.slice(0, 8)}... rejected.` },
          ])
        }
      } catch (err) {
        console.error('Poll error:', err)
      }
    }, 2000)
  }, [])

  const sendMessage = async () => {
    if (!input.trim() || loading || pendingApproval) return
    const userMsg = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: userMsg }])
    setLoading(true)

    const timestamp = new Date().toLocaleTimeString()
    setGatewayEvents((prev) => [
      ...prev,
      { type: 'info', time: timestamp, text: `Intercepting: "${userMsg}"` },
    ])

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/chat-simulation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      const now = new Date().toLocaleTimeString()

      if (data.gateway_triggered) {
        if (data.gateway_action === 'PENDING') {
          setMessages((prev) => [...prev, { role: 'agent', text: data.agent_reply }])
          setPendingApproval({ requestId: data.request_id, amount: data.attempted_amount })
          setGatewayEvents((prev) => [
            ...prev,
            {
              type: 'pending',
              time: now,
              text: 'ACTION PAUSED: ROUTED TO HUMAN APPROVALS',
              detail: `Tool: issue_refund | Amount: $${data.attempted_amount} | Tier: $20-$100 HITL\n\n👉 Switch to "Approvals" tab to approve or reject.`,
            },
          ])
          startPolling(data.request_id)
        } else if (data.gateway_action === 'DENY') {
          setMessages((prev) => [...prev, { role: 'agent', text: data.agent_reply }])
          setGatewayEvents((prev) => [
            ...prev,
            {
              type: 'deny',
              time: now,
              text: 'ACCESS DENIED: POLICY VIOLATION',
              detail: `Tool: issue_refund | Amount: $${data.attempted_amount} | Hard Limit: $100`,
            },
            ...(data.threat_analysis
              ? [{ type: 'threat', time: now, text: 'SOC THREAT REPORT', detail: data.threat_analysis }]
              : []),
          ])
        } else if (data.gateway_action === 'ALLOW') {
          setMessages((prev) => [...prev, { role: 'agent', text: data.agent_reply }])
          setGatewayEvents((prev) => [
            ...prev,
            {
              type: 'allow',
              time: now,
              text: 'ACCESS GIVEN: AUTO-APPROVED',
              detail: `Tool: issue_refund | Amount: $${data.attempted_amount} | Tier: ≤$20 Auto`,
            },
          ])
        }
      } else {
        setMessages((prev) => [...prev, { role: 'agent', text: data.agent_reply }])
        setGatewayEvents((prev) => [...prev, { type: 'info', time: now, text: 'No policy check required' }])
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'error', text: `Connection error: ${err.message}. Is the server running?` }])
      setGatewayEvents((prev) => [...prev, { type: 'error', time: new Date().toLocaleTimeString(), text: `ERROR: ${err.message}` }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="flex h-[calc(100vh-73px)]">
      {/* LEFT PANE: Customer Chat */}
      <div className="w-1/2 flex flex-col border-r border-gray-800">
        <div className="px-5 py-3 border-b border-gray-800 bg-gray-900/50">
          <h2 className="text-sm font-semibold text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            AI Customer Support Agent
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">Powered by Amazon Bedrock</p>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          {messages.map((msg, i) => (
            <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${msg.role === 'user'
                  ? 'bg-emerald-600 text-white rounded-br-md'
                  : msg.role === 'system'
                    ? 'bg-gray-800/80 text-gray-300 border border-gray-700 rounded-bl-md'
                    : msg.role === 'error'
                      ? 'bg-red-900/30 text-red-400 border border-red-800 rounded-bl-md'
                      : 'bg-gray-800 text-gray-100 rounded-bl-md'
                  }`}
              >
                {msg.role === 'system' && <span className="text-emerald-400 font-semibold text-xs block mb-1">SYSTEM</span>}
                {msg.role === 'agent' && <span className="text-blue-400 font-semibold text-xs block mb-1">AI AGENT</span>}
                {msg.text}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-800 rounded-2xl rounded-bl-md px-4 py-3">
                <div className="flex gap-1.5">
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        <div className="px-5 py-3 border-t border-gray-800 bg-gray-900/30">
          {pendingApproval && (
            <div className="mb-2 px-3 py-2 bg-yellow-900/20 border border-yellow-800/50 rounded-lg text-xs text-yellow-400 flex items-center gap-2">
              <span className="animate-pulse">⏳</span>
              Waiting for manager approval... Switch to the Approvals tab.
            </div>
          )}
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder={pendingApproval ? 'Waiting for approval...' : 'Ask for a refund...'}
              disabled={loading || !!pendingApproval}
              className="flex-1 bg-gray-800 border border-gray-700 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500/50 disabled:opacity-50 transition-colors"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim() || !!pendingApproval}
              className="bg-emerald-600 hover:bg-emerald-500 disabled:bg-gray-700 disabled:text-gray-500 text-white px-5 py-2.5 rounded-xl text-sm font-medium transition-colors"
            >
              Send
            </button>
          </div>
          <p className="text-xs text-gray-600 mt-2">
            Try: "$15 refund" (auto-approved) · "$50 refund" (needs manager) · "$500 refund" (hard denied)
          </p>
        </div>
      </div>

      {/* RIGHT PANE: SudoMode Live Monitor */}
      <div className="w-1/2 flex flex-col bg-gray-950">
        <div className="px-5 py-3 border-b border-gray-800 bg-gray-900/80">
          <h2 className="text-sm font-semibold text-emerald-400 flex items-center gap-2 font-mono">
            <span className="text-red-400">●</span>
            SUDOMODE // SENTINEL MONITOR
          </h2>
          <p className="text-xs text-gray-500 mt-0.5 font-mono">Zero-Trust AI Governance Gateway — Live Feed</p>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3 font-mono text-xs">
          {gatewayEvents.length === 0 && (
            <div className="text-gray-600 py-8 text-center">
              <div className="text-4xl mb-3">🔒</div>
              <p>Waiting for agent activity...</p>
              <p className="mt-1 text-gray-700">Send a message to see SudoMode in action</p>
            </div>
          )}

          {gatewayEvents.map((evt, i) => (
            <div key={i} className="animate-fadeIn">
              {/* GREEN: Auto-approved */}
              {evt.type === 'allow' && (
                <div className="border border-emerald-800/60 bg-emerald-950/30 rounded-lg p-3">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span className="text-emerald-400 font-bold tracking-wider">✅ {evt.text}</span>
                    <span className="text-gray-600 ml-auto">{evt.time}</span>
                  </div>
                  {evt.detail && <div className="text-emerald-300/60 text-xs pl-4 mt-1 border-l-2 border-emerald-800/60">{evt.detail}</div>}
                </div>
              )}

              {/* YELLOW: Routed to human */}
              {evt.type === 'pending' && (
                <div className="border border-yellow-700/60 bg-yellow-950/30 rounded-lg p-3 shadow-lg shadow-yellow-900/10">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-full bg-yellow-500 animate-pulse"></span>
                    <span className="text-yellow-400 font-bold tracking-wider">⏳ {evt.text}</span>
                    <span className="text-gray-600 ml-auto">{evt.time}</span>
                  </div>
                  <div className="text-yellow-200/70 text-xs pl-4 border-l-2 border-yellow-700/60 leading-relaxed whitespace-pre-line">{evt.detail}</div>
                </div>
              )}

              {/* RED: Hard deny */}
              {evt.type === 'deny' && (
                <div className="border border-red-800 bg-red-950/50 rounded-lg p-3 shadow-lg shadow-red-900/20">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
                    <span className="text-red-400 font-bold tracking-wider">⛔ {evt.text}</span>
                    <span className="text-gray-600 ml-auto">{evt.time}</span>
                  </div>
                  <div className="text-red-300/80 text-xs pl-4 border-l-2 border-red-800">{evt.detail}</div>
                </div>
              )}

              {/* AMBER: Threat analysis SOC report */}
              {evt.type === 'threat' && (
                <div className="border border-amber-800/60 bg-amber-950/30 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                    <span className="text-amber-400 font-bold tracking-wider">🔍 {evt.text}</span>
                    <span className="text-gray-600 ml-auto">{evt.time}</span>
                  </div>
                  <div className="text-amber-200/70 text-xs pl-4 border-l-2 border-amber-800/60 leading-relaxed">{evt.detail}</div>
                </div>
              )}

              {/* GREEN: Manager approved */}
              {evt.type === 'approved' && (
                <div className="border border-emerald-700/60 bg-emerald-950/40 rounded-lg p-3 shadow-lg shadow-emerald-900/20">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span className="text-emerald-400 font-bold tracking-wider">✅ {evt.text}</span>
                    <span className="text-gray-600 ml-auto">{evt.time}</span>
                  </div>
                  <div className="text-emerald-300/60 text-xs pl-4 border-l-2 border-emerald-700/60">{evt.detail}</div>
                </div>
              )}

              {/* RED: Manager rejected */}
              {evt.type === 'rejected' && (
                <div className="border border-red-800 bg-red-950/30 rounded-lg p-3">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="w-2 h-2 rounded-full bg-red-500"></span>
                    <span className="text-red-400 font-bold tracking-wider">❌ {evt.text}</span>
                    <span className="text-gray-600 ml-auto">{evt.time}</span>
                  </div>
                  <div className="text-red-300/60 text-xs pl-4 border-l-2 border-red-800">{evt.detail}</div>
                </div>
              )}

              {evt.type === 'info' && (
                <div className="text-gray-500 pl-4 border-l-2 border-gray-800 py-1">
                  <span className="text-gray-600">[{evt.time}]</span> {evt.text}
                </div>
              )}
              {evt.type === 'error' && (
                <div className="text-red-500 pl-4 border-l-2 border-red-900 py-1">
                  <span className="text-gray-600">[{evt.time}]</span> {evt.text}
                </div>
              )}
            </div>
          ))}
          <div ref={monitorEndRef} />
        </div>

        <div className="px-5 py-2 border-t border-gray-800 bg-gray-900/50 font-mono text-xs text-gray-600 flex justify-between">
          <span>≤$20 AUTO · $20-$100 HITL · &gt;$100 DENY</span>
          <span className="flex gap-3">
            <span className="text-emerald-500">{gatewayEvents.filter((e) => e.type === 'allow').length} auto</span>
            <span className="text-yellow-500">{gatewayEvents.filter((e) => e.type === 'pending').length} pending</span>
            <span className="text-red-500">{gatewayEvents.filter((e) => e.type === 'deny').length} denied</span>
          </span>
        </div>
      </div>
    </div>
  )
}
