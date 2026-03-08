import { useState, useEffect } from 'react'

const API_BASE_URL = import.meta.env.DEV ? 'http://localhost:8000' : ''

const BADGE_STYLES = {
    ALLOW: 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30',
    REQUIRE_APPROVAL: 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30',
    DENY: 'bg-red-500/20 text-red-400 border border-red-500/30',
}

const BADGE_LABELS = {
    ALLOW: 'AUTO-APPROVE',
    REQUIRE_APPROVAL: 'HUMAN-IN-THE-LOOP',
    DENY: 'HARD DENY',
}

const RISK_COLORS = {
    LOW: 'text-emerald-400',
    MEDIUM: 'text-yellow-400',
    HIGH: 'text-red-400',
    CRITICAL: 'text-red-500',
}

const CARD_BORDERS = {
    green: 'border-emerald-800/40 hover:border-emerald-700/60',
    yellow: 'border-yellow-800/40 hover:border-yellow-700/60',
    red: 'border-red-800/40 hover:border-red-700/60',
}

const CARD_GLOWS = {
    green: 'hover:shadow-emerald-900/20',
    yellow: 'hover:shadow-yellow-900/20',
    red: 'hover:shadow-red-900/20',
}

const ICON_BG = {
    green: 'bg-emerald-500/10',
    yellow: 'bg-yellow-500/10',
    red: 'bg-red-500/10',
}

const ICONS = {
    ALLOW: '✅',
    REQUIRE_APPROVAL: '⏳',
    DENY: '⛔',
}

export default function PoliciesView() {
    const [policies, setPolicies] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        const fetchPolicies = async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/v1/policies`)
                if (!res.ok) throw new Error(`Server error: ${res.status}`)
                const data = await res.json()
                setPolicies(data)
                setError(null)
            } catch (err) {
                setError(err.message)
            } finally {
                setLoading(false)
            }
        }
        fetchPolicies()
    }, [])

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="text-gray-500">Loading policies...</div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="max-w-5xl mx-auto px-6 py-8">
                <div className="bg-red-900/20 border border-red-800 rounded-lg p-4">
                    <p className="text-red-400">Error loading policies: {error}</p>
                    <p className="text-sm text-gray-500 mt-2">Make sure the server is running on {API_BASE_URL}</p>
                </div>
            </div>
        )
    }

    return (
        <div className="max-w-5xl mx-auto px-6 py-8">
            {/* Header */}
            <div className="flex items-start justify-between mb-8">
                <div>
                    <h2 className="text-2xl font-bold text-white mb-1">{policies.policy_name}</h2>
                    <p className="text-gray-500 text-sm">{policies.description}</p>
                    <div className="flex items-center gap-3 mt-3">
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/20">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                            {policies.enforcement}
                        </span>
                        <span className="text-xs text-gray-600">
                            Last updated: {new Date(policies.last_updated).toLocaleDateString()}
                        </span>
                    </div>
                </div>
                <div className="relative group">
                    <button
                        disabled
                        className="px-4 py-2 rounded-lg text-sm font-medium bg-gray-800 text-gray-500 border border-gray-700 cursor-not-allowed"
                    >
                        ✏️ Edit Policy
                    </button>
                    <div className="absolute right-0 top-full mt-2 px-3 py-2 bg-gray-800 border border-gray-700 rounded-lg text-xs text-gray-400 whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none shadow-xl">
                        Editing locked for demo purposes
                    </div>
                </div>
            </div>

            {/* Escalation Flow Diagram */}
            <div className="mb-8 p-4 bg-gray-900/50 border border-gray-800 rounded-xl">
                <div className="text-xs font-mono text-gray-500 mb-3">ESCALATION MATRIX</div>
                <div className="flex items-center justify-between gap-2">
                    <div className="flex-1 text-center">
                        <div className="text-emerald-400 text-lg font-bold">≤ $20</div>
                        <div className="text-emerald-400/60 text-xs mt-1">AUTO-APPROVE</div>
                    </div>
                    <div className="text-gray-600 text-xl">→</div>
                    <div className="flex-1 text-center">
                        <div className="text-yellow-400 text-lg font-bold">$20 – $100</div>
                        <div className="text-yellow-400/60 text-xs mt-1">HUMAN REVIEW</div>
                    </div>
                    <div className="text-gray-600 text-xl">→</div>
                    <div className="flex-1 text-center">
                        <div className="text-red-400 text-lg font-bold">&gt; $100</div>
                        <div className="text-red-400/60 text-xs mt-1">HARD DENY + SOC</div>
                    </div>
                </div>
            </div>

            {/* Policy Cards */}
            <div className="space-y-4">
                {policies.rules.map((rule) => (
                    <div
                        key={rule.id}
                        className={`bg-gray-900/60 border rounded-xl p-5 transition-all duration-200 shadow-lg ${CARD_BORDERS[rule.color]} ${CARD_GLOWS[rule.color]}`}
                    >
                        <div className="flex items-start gap-4">
                            {/* Icon */}
                            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-lg shrink-0 ${ICON_BG[rule.color]}`}>
                                {ICONS[rule.decision]}
                            </div>

                            {/* Content */}
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-3 mb-1.5">
                                    <h3 className="text-white font-semibold text-sm">{rule.name}</h3>
                                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold tracking-wider ${BADGE_STYLES[rule.decision]}`}>
                                        {BADGE_LABELS[rule.decision]}
                                    </span>
                                </div>
                                <p className="text-gray-400 text-sm leading-relaxed mb-3">{rule.description}</p>

                                {/* Metadata Row */}
                                <div className="flex flex-wrap gap-4 text-xs">
                                    <div>
                                        <span className="text-gray-600">Resource: </span>
                                        <span className="text-gray-300 font-mono">{rule.resource}</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">Action: </span>
                                        <span className="text-gray-300 font-mono">{rule.action}</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">Condition: </span>
                                        <span className="text-gray-300 font-mono">{rule.condition}</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-600">Risk: </span>
                                        <span className={`font-semibold ${RISK_COLORS[rule.risk_level]}`}>{rule.risk_level}</span>
                                    </div>
                                </div>
                            </div>

                            {/* Policy ID */}
                            <div className="text-xs text-gray-600 font-mono shrink-0">{rule.id}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}
