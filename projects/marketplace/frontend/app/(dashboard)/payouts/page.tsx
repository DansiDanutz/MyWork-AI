'use client'

import { useState, useEffect } from 'react'
import { useUser } from '@clerk/nextjs'
import { payoutsApi } from '@/lib/api'
import {
  DollarSign,
  Calendar,
  CheckCircle,
  Clock,
  XCircle,
  ArrowUpRight,
  Download,
} from 'lucide-react'

type Payout = {
  id: string
  amount: number
  currency: string
  order_count: number
  status: string
  status_label: string
  period_start: string
  period_end: string
  initiated_at: string | null
  completed_at: string | null
  failure_reason: string | null
  created_at: string
}

type Balance = {
  pending_balance: number
  currency: string
  order_count: number
  next_payout_date: string
  payouts_enabled: boolean
  stripe_account_id: string | null
}

type SellerProfile = {
  is_seller: boolean
  payouts_enabled: boolean
  stripe_onboarding_complete: boolean
  stripe_account_id: string | null
  charges_enabled: boolean | null
}

export default function PayoutsPage() {
  const { user, isLoaded: userLoaded } = useUser()
  const [balance, setBalance] = useState<Balance | null>(null)
  const [payouts, setPayouts] = useState<Payout[]>([])
  const [sellerProfile, setSellerProfile] = useState<SellerProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [requestingPayout, setRequestingPayout] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [selectedStatus, setSelectedStatus] = useState<string | null>(null)

  useEffect(() => {
    if (userLoaded && user) {
      loadData()
    }
  }, [userLoaded, user, selectedStatus])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)

      const [balanceRes, payoutsRes, profileRes] = await Promise.all([
        payoutsApi.getBalance(),
        payoutsApi.getPayouts(selectedStatus ? { status: selectedStatus } : {}),
        payoutsApi.getSellerProfile(),
      ])

      setBalance(balanceRes.data)
      setPayouts(payoutsRes.data.payouts)
      setSellerProfile(profileRes.data)
    } catch (err: any) {
      console.error('Failed to load payouts:', err)
      setError(err.response?.data?.detail || 'Failed to load payouts')
    } finally {
      setLoading(false)
    }
  }

  const handleRequestPayout = async () => {
    if (!balance || balance.pending_balance < 10) {
      setError('Minimum payout amount is $10.00')
      return
    }

    try {
      setRequestingPayout(true)
      setError(null)
      setSuccessMessage(null)

      const response = await payoutsApi.requestPayout()

      setSuccessMessage(response.data.message || 'Payout requested successfully!')

      // Reload data after successful request
      await loadData()
    } catch (err: any) {
      console.error('Failed to request payout:', err)
      setError(err.response?.data?.detail || 'Failed to request payout')
    } finally {
      setRequestingPayout(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'processing':
        return <Clock className="w-5 h-5 text-yellow-500" />
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'processing':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      case 'failed':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    }
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Show message if not a seller
  if (sellerProfile && !sellerProfile.is_seller) {
    return (
      <div className="text-center py-12">
        <DollarSign className="w-16 h-16 text-gray-600 mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-white mb-2">Become a Seller</h2>
        <p className="text-gray-400 mb-6">
          You need to become a seller to access payouts and earn from your products.
        </p>
        <a
          href="/my-products"
          className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Get Started
          <ArrowUpRight className="w-4 h-4 ml-2" />
        </a>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">Payouts</h1>
        <p className="text-gray-400">Manage your earnings and request payouts</p>
      </div>

      {/* Error and Success Messages */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-500 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {successMessage && (
        <div className="bg-green-500/10 border border-green-500/20 text-green-500 px-4 py-3 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* Pending Balance Card */}
      {balance && (
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="text-gray-400 text-sm mb-1">Pending Balance</p>
              <p className="text-4xl font-bold text-white">
                ${balance.pending_balance.toFixed(2)}
              </p>
              <p className="text-gray-500 text-sm mt-1">
                {balance.order_count} order{balance.order_count !== 1 ? 's' : ''} awaiting payout
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center text-gray-400 text-sm mb-2">
                <Calendar className="w-4 h-4 mr-2" />
                Next Payout Date
              </div>
              <p className="text-white font-semibold">
                {formatDate(balance.next_payout_date)}
              </p>
            </div>
          </div>

          {/* Stripe Onboarding Alert */}
          {!balance.payouts_enabled && (
            <div className="bg-yellow-500/10 border border-yellow-500/20 text-yellow-500 px-4 py-3 rounded-lg mb-4">
              <p className="font-semibold mb-1">Setup Payouts</p>
              <p className="text-sm">
                You need to complete Stripe onboarding to receive payouts. This takes about 5 minutes.
              </p>
            </div>
          )}

          {/* Request Payout Button */}
          {balance.payouts_enabled ? (
            <button
              onClick={handleRequestPayout}
              disabled={
                requestingPayout ||
                balance.pending_balance < 10 ||
                balance.order_count === 0
              }
              className={`w-full py-3 rounded-lg font-semibold transition-colors ${
                requestingPayout ||
                balance.pending_balance < 10 ||
                balance.order_count === 0
                  ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {requestingPayout ? (
                'Processing...'
              ) : balance.pending_balance < 10 ? (
                `Minimum payout is $10.00 (you have $${balance.pending_balance.toFixed(2)})`
              ) : balance.order_count === 0 ? (
                'No pending orders to payout'
              ) : (
                'Request Payout'
              )}
            </button>
          ) : (
            <button
              disabled
              className="w-full py-3 rounded-lg font-semibold bg-gray-700 text-gray-500 cursor-not-allowed"
            >
              Complete Stripe Onboarding First
            </button>
          )}
        </div>
      )}

      {/* Payouts History */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-white">Payout History</h2>

          {/* Status Filter */}
          <select
            value={selectedStatus || ''}
            onChange={(e) => setSelectedStatus(e.target.value || null)}
            className="bg-gray-800 border border-gray-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        {payouts.length === 0 ? (
          <div className="bg-gray-800 border border-gray-700 rounded-lg p-12 text-center">
            <DollarSign className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">No Payouts Yet</h3>
            <p className="text-gray-400">
              {selectedStatus
                ? `No ${selectedStatus} payouts found`
                : 'Your payout history will appear here once you start earning'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {payouts.map((payout) => (
              <div
                key={payout.id}
                className="bg-gray-800 border border-gray-700 rounded-lg p-6 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <p className="text-2xl font-bold text-white">
                        ${payout.amount.toFixed(2)}
                      </p>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold border ${getStatusColor(
                          payout.status
                        )}`}
                      >
                        {payout.status_label}
                      </span>
                    </div>

                    <div className="space-y-1 text-sm text-gray-400">
                      <p>
                        <span className="text-gray-500">Period:</span>{' '}
                        {formatDate(payout.period_start)} - {formatDate(payout.period_end)}
                      </p>
                      <p>
                        <span className="text-gray-500">Orders:</span> {payout.order_count}
                      </p>
                      <p>
                        <span className="text-gray-500">ID:</span> {payout.id.slice(0, 8)}...
                      </p>
                      {payout.initiated_at && (
                        <p>
                          <span className="text-gray-500">Initiated:</span>{' '}
                          {formatDate(payout.initiated_at)}
                        </p>
                      )}
                      {payout.completed_at && (
                        <p>
                          <span className="text-gray-500">Completed:</span>{' '}
                          {formatDate(payout.completed_at)}
                        </p>
                      )}
                      {payout.failure_reason && (
                        <p className="text-red-500">
                          <span className="text-red-400">Failure Reason:</span>{' '}
                          {payout.failure_reason}
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    {getStatusIcon(payout.status)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
