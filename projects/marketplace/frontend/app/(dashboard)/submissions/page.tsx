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
  audit_report?: {
    errors?: string[]
    warnings?: string[]
  } | null
  repo_commit_sha?: string | null
  brain_ingest_status?: string | null
  brain_ingested_at?: string | null
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

const BRAIN_STATUS: Record<string, { text: string; variant: "success" | "warning" | "destructive" | "secondary" | "default" }> = {
  queued: { text: "Queued", variant: "secondary" },
  processing: { text: "Processing", variant: "warning" },
  ingested: { text: "Ingested", variant: "success" },
  error: { text: "Error", variant: "destructive" },
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
                  {(submission.audit_report?.errors?.length || submission.audit_report?.warnings?.length) && (
                    <div className="flex flex-wrap gap-2 text-xs">
                      {submission.audit_report?.errors && submission.audit_report.errors.length > 0 && (
                        <span className="px-2 py-1 rounded-full bg-red-900/30 text-red-400 border border-red-700/50">
                          {submission.audit_report.errors.length} errors
                        </span>
                      )}
                      {submission.audit_report?.warnings && submission.audit_report.warnings.length > 0 && (
                        <span className="px-2 py-1 rounded-full bg-yellow-900/30 text-yellow-400 border border-yellow-700/50">
                          {submission.audit_report.warnings.length} warnings
                        </span>
                      )}
                    </div>
                  )}
                  {submission.failure_reason && (
                    <p className="text-sm text-red-400">Reason: {submission.failure_reason}</p>
                  )}
                  {submission.repo_commit_sha && (
                    <p className="text-xs text-gray-500">
                      Snapshot commit: <span className="text-gray-300">{submission.repo_commit_sha.slice(0, 8)}</span>
                    </p>
                  )}
                  {submission.brain_ingest_status && (
                    <div className="flex items-center gap-2 text-xs">
                      <span className="text-gray-400">Brain:</span>
                      <Badge variant={BRAIN_STATUS[submission.brain_ingest_status]?.variant || "secondary"}>
                        {BRAIN_STATUS[submission.brain_ingest_status]?.text || submission.brain_ingest_status}
                      </Badge>
                      {submission.brain_ingested_at && (
                        <span className="text-gray-500">
                          {formatDate(submission.brain_ingested_at)}
                        </span>
                      )}
                    </div>
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
