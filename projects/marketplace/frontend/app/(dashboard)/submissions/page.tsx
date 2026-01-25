"use client"

export const dynamic = "force-dynamic"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useAuth } from "@clerk/nextjs"
import { PackageCheck, RefreshCcw, UploadCloud } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { submissionsApi, setAuthToken } from "@/lib/api"
import { formatDate } from "@/lib/utils"

interface Submission {
  id: string
  title: string
  status: string
  audit_score?: number | null
  failure_reason?: string | null
  created_at: string
  product_id?: string | null
}

const STATUS_COLORS: Record<string, { text: string; variant: "success" | "warning" | "destructive" | "secondary" | "default" }> = {
  submitted: { text: "Submitted", variant: "secondary" },
  auditing: { text: "Auditing", variant: "warning" },
  approved: { text: "Approved", variant: "success" },
  rejected: { text: "Rejected", variant: "destructive" },
  published: { text: "Published", variant: "success" },
}

export default function SubmissionsPage() {
  const { getToken } = useAuth()
  const [submissions, setSubmissions] = useState<Submission[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadSubmissions()
  }, [])

  async function loadSubmissions() {
    try {
      setLoading(true)
      setError(null)
      const token = await getToken()
      if (!token) {
        setError("Authentication required")
        return
      }
      setAuthToken(token)
      const response = await submissionsApi.listMine()
      setSubmissions(response.data.submissions || [])
    } catch (err: any) {
      console.error("Failed to load submissions:", err)
      setError(err.response?.data?.detail || "Failed to load submissions")
    } finally {
      setLoading(false)
    }
  }

  async function handleRetry(submissionId: string) {
    try {
      const token = await getToken()
      if (!token) return
      setAuthToken(token)
      await submissionsApi.retry(submissionId)
      await loadSubmissions()
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to retry audit")
    }
  }

  async function handlePublish(submissionId: string) {
    try {
      const token = await getToken()
      if (!token) return
      setAuthToken(token)
      await submissionsApi.publish(submissionId)
      await loadSubmissions()
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to publish submission")
    }
  }

  if (loading) {
    return (
      <div className="p-6 lg:p-8">
        <div className="flex items-center justify-center h-64 text-gray-400">Loading submissions...</div>
      </div>
    )
  }

  return (
    <div className="p-6 lg:p-8 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Submissions</h1>
          <p className="text-gray-400">Track your audit status before publishing.</p>
        </div>
        <Link href="/dashboard/my-products/new">
          <Button className="gap-2">
            <UploadCloud className="h-4 w-4" />
            New Submission
          </Button>
        </Link>
      </div>

      {error && (
        <Card className="border-red-900 bg-red-950/20">
          <CardContent className="p-6">
            <p className="text-red-400">{error}</p>
          </CardContent>
        </Card>
      )}

      {submissions.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <p className="text-gray-400">No submissions yet.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {submissions.map((submission) => {
            const badge = STATUS_COLORS[submission.status] || STATUS_COLORS.submitted
            return (
              <Card key={submission.id} className="bg-gray-900 border-gray-800">
                <CardHeader className="flex flex-row items-center justify-between">
                  <div>
                    <CardTitle className="text-white">{submission.title}</CardTitle>
                    <p className="text-sm text-gray-500">Submitted {formatDate(submission.created_at)}</p>
                  </div>
                  <Badge variant={badge.variant}>{badge.text}</Badge>
                </CardHeader>
                <CardContent className="flex flex-col gap-3">
                  {submission.audit_score !== null && submission.audit_score !== undefined && (
                    <p className="text-sm text-gray-400">Audit score: {submission.audit_score}</p>
                  )}
                  {submission.failure_reason && (
                    <p className="text-sm text-red-400">Reason: {submission.failure_reason}</p>
                  )}
                  <div className="flex flex-wrap gap-2">
                    {submission.status === "rejected" && (
                      <Button variant="outline" size="sm" onClick={() => handleRetry(submission.id)} className="gap-2">
                        <RefreshCcw className="h-4 w-4" />
                        Retry Audit
                      </Button>
                    )}
                    {submission.status === "approved" && (
                      <Button size="sm" onClick={() => handlePublish(submission.id)} className="gap-2">
                        <PackageCheck className="h-4 w-4" />
                        Publish
                      </Button>
                    )}
                    {submission.status === "published" && submission.product_id && (
                      <Link href={`/products/${submission.product_id}`}>
                        <Button variant="secondary" size="sm">View Listing</Button>
                      </Link>
                    )}
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
