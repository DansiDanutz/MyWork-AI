"use client"

export const dynamic = "force-dynamic"

import { useEffect, useState } from "react"
import { ArrowDownLeft, ArrowUpRight, Coins, Loader2, PlusCircle } from "lucide-react"
import Link from "next/link"

import { creditsApi } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

type LedgerEntry = {
  id: string
  amount: number
  currency: string
  entry_type: string
  status: string
  related_order_id?: string | null
  posted_at?: string | null
  created_at?: string | null
}

export default function CreditsPage() {
  const [balance, setBalance] = useState(0)
  const [currency, setCurrency] = useState("USD")
  const [entries, setEntries] = useState<LedgerEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [topupAmount, setTopupAmount] = useState("50")
  const [topupLoading, setTopupLoading] = useState(false)

  useEffect(() => {
    const loadCredits = async () => {
      setLoading(true)
      setError(null)
      try {
        const [balanceRes, ledgerRes] = await Promise.all([
          creditsApi.getBalance(),
          creditsApi.listLedger(25),
        ])
        setBalance(Number(balanceRes.data.balance || 0))
        setCurrency(balanceRes.data.currency || "USD")
        setEntries(ledgerRes.data.entries || [])
      } catch (err: any) {
        console.error("Failed to load credits:", err)
        setError(err.response?.data?.detail || "Failed to load credits data")
      } finally {
        setLoading(false)
      }
    }

    loadCredits()
  }, [])

  const formatAmount = (amount: number) =>
    new Intl.NumberFormat("en-US", { style: "currency", currency }).format(amount)

  const handleTopup = async () => {
    if (!topupAmount || topupLoading) return
    const amountValue = Number(topupAmount)
    if (!amountValue || amountValue <= 0) {
      setError("Enter a valid amount to top up")
      return
    }

    setTopupLoading(true)
    setError(null)
    try {
      const res = await creditsApi.createTopupSession(amountValue)
      const { checkout_url } = res.data
      window.location.href = checkout_url
    } catch (err: any) {
      console.error("Top up failed:", err)
      setError(err.response?.data?.detail || "Failed to start top-up checkout")
      setTopupLoading(false)
    }
  }

  const entryLabel = (entry: LedgerEntry) => {
    switch (entry.entry_type) {
      case "topup":
        return "Top up"
      case "purchase":
        return "Purchase"
      case "sale":
        return "Sale"
      case "fee":
        return "Platform fee"
      case "refund":
        return "Refund"
      case "escrow_hold":
        return "Escrow hold"
      case "escrow_release":
        return "Escrow release"
      default:
        return entry.entry_type.replace(/_/g, " ")
    }
  }

  const statusBadge = (status: string) => {
    if (status === "posted") {
      return "bg-green-900/30 text-green-400 border-green-700/50"
    }
    if (status === "pending") {
      return "bg-yellow-900/30 text-yellow-400 border-yellow-700/50"
    }
    return "bg-gray-800 text-gray-300 border-gray-700"
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-3 mb-2">
        <Coins className="w-8 h-8 text-blue-400" />
        <h1 className="text-3xl font-bold text-white">Credits</h1>
      </div>
      <p className="text-gray-400 mb-8">
        Use credits to buy projects instantly. Top up 1:1 in USD.
      </p>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-10 h-10 animate-spin text-blue-500" />
        </div>
      ) : (
        <>
          {error && (
            <div className="bg-red-900/20 border border-red-700/50 rounded-lg p-4 text-red-400 mb-6">
              {error}
            </div>
          )}

          <div className="grid gap-6 lg:grid-cols-3 mb-10">
            <Card className="bg-gray-900 border-gray-800 lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-white">Balance</CardTitle>
              </CardHeader>
              <CardContent className="flex items-center justify-between gap-6">
                <div>
                  <p className="text-4xl font-bold text-white">{formatAmount(balance)}</p>
                  <p className="text-gray-400 mt-2">Available credits</p>
                </div>
                <div className="text-sm text-gray-400">
                  <p>Credits can be used at checkout.</p>
                  <Link href="/products" className="text-blue-400 hover:text-blue-300">
                    Browse projects
                  </Link>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle className="text-white">Top up</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm text-gray-400">Amount (USD)</label>
                  <input
                    type="number"
                    min="1"
                    step="1"
                    value={topupAmount}
                    onChange={(event) => setTopupAmount(event.target.value)}
                    className="mt-2 w-full rounded-lg border border-gray-700 bg-gray-950 px-3 py-2 text-white focus:border-blue-500 focus:outline-none"
                  />
                </div>
                <Button
                  onClick={handleTopup}
                  className="w-full"
                  disabled={topupLoading}
                >
                  {topupLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  ) : (
                    <PlusCircle className="w-4 h-4 mr-2" />
                  )}
                  Top up credits
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white">Recent activity</CardTitle>
            </CardHeader>
            <CardContent>
              {entries.length === 0 ? (
                <div className="text-gray-400 text-sm">No credit activity yet.</div>
              ) : (
                <div className="space-y-4">
                  {entries.map((entry) => {
                    const isPositive = entry.amount >= 0
                    const icon = isPositive ? (
                      <ArrowDownLeft className="w-4 h-4 text-green-400" />
                    ) : (
                      <ArrowUpRight className="w-4 h-4 text-red-400" />
                    )
                    const date = entry.posted_at || entry.created_at
                    return (
                      <div
                        key={entry.id}
                        className="flex items-center justify-between border border-gray-800 rounded-lg px-4 py-3"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-full bg-gray-800 flex items-center justify-center">
                            {icon}
                          </div>
                          <div>
                            <p className="text-white font-medium">{entryLabel(entry)}</p>
                            <p className="text-xs text-gray-400">
                              {date ? new Date(date).toLocaleString() : "Pending"}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className={`font-semibold ${isPositive ? "text-green-400" : "text-red-400"}`}>
                            {isPositive ? "+" : "-"}
                            {formatAmount(Math.abs(entry.amount))}
                          </p>
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded-full border text-xs ${statusBadge(entry.status)}`}
                          >
                            {entry.status}
                          </span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
