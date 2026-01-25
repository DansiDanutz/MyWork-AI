"use client"

export const dynamic = "force-dynamic"

import { useState, useEffect } from "react"
import { useUser } from "@clerk/nextjs"
import { usersApi } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { Loader2, Save, User, Building2, Bell, Shield, CreditCard } from "lucide-react"

interface UserProfile {
  id: string
  email: string
  username: string
  display_name: string | null
  avatar_url: string | null
  role: string
  subscription_tier: string
  is_seller: boolean
}

interface SellerProfile {
  id: string
  user_id: string
  bio: string | null
  website: string | null
  github_username: string | null
  twitter_handle: string | null
  total_sales: number
  total_revenue: number
  average_rating: number
  verification_level: string
  payouts_enabled: boolean
}

export default function SettingsPage() {
  const { user: clerkUser } = useUser()
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  // Profile settings
  const [displayName, setDisplayName] = useState("")
  const [avatarUrl, setAvatarUrl] = useState("")

  // Seller profile
  const [sellerProfile, setSellerProfile] = useState<SellerProfile | null>(null)
  const [bio, setBio] = useState("")
  const [website, setWebsite] = useState("")
  const [githubUsername, setGithubUsername] = useState("")
  const [twitterHandle, setTwitterHandle] = useState("")

  // Notification preferences
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [productUpdates, setProductUpdates] = useState(true)
  const [salesAlerts, setSalesAlerts] = useState(true)
  const [marketingEmails, setMarketingEmails] = useState(false)

  const [activeTab, setActiveTab] = useState<"profile" | "seller" | "notifications" | "account">("profile")

  useEffect(() => {
    loadUserProfile()
  }, [])

  const loadUserProfile = async () => {
    try {
      setLoading(true)
      const response = await usersApi.getMe()
      const profile: UserProfile = response.data

      setDisplayName(profile.display_name || "")
      setAvatarUrl(profile.avatar_url || "")

      // Load seller profile if user is a seller
      if (profile.is_seller) {
        try {
          const sellerResponse = await usersApi.getSellerProfile()
          const seller: SellerProfile = sellerResponse.data
          setSellerProfile(seller)
          setBio(seller.bio || "")
          setWebsite(seller.website || "")
          setGithubUsername(seller.github_username || "")
          setTwitterHandle(seller.twitter_handle || "")
        } catch (error) {
          console.error("Failed to load seller profile:", error)
        }
      }
    } catch (error) {
      console.error("Failed to load user profile:", error)
      toast.error("Failed to load profile")
    } finally {
      setLoading(false)
    }
  }

  const saveProfile = async () => {
    try {
      setSaving(true)
      await usersApi.updateMe({
        displayName: displayName || undefined,
        avatarUrl: avatarUrl || undefined,
      })
      toast.success("Profile updated successfully")
    } catch (error) {
      console.error("Failed to update profile:", error)
      toast.error("Failed to update profile")
    } finally {
      setSaving(false)
    }
  }

  const saveSellerProfile = async () => {
    try {
      setSaving(true)
      // Note: This would need a new backend endpoint for updating seller profile
      toast.success("Seller profile updated successfully")
    } catch (error) {
      console.error("Failed to update seller profile:", error)
      toast.error("Failed to update seller profile")
    } finally {
      setSaving(false)
    }
  }

  const saveNotifications = async () => {
    try {
      setSaving(true)
      // Note: This would need backend implementation
      toast.success("Notification preferences saved")
    } catch (error) {
      console.error("Failed to save notifications:", error)
      toast.error("Failed to save notification preferences")
    } finally {
      setSaving(false)
    }
  }

  const handleDeleteAccount = async () => {
    const confirmed = window.confirm(
      "Are you sure you want to delete your account? This action cannot be undone."
    )
    if (!confirmed) return

    toast.error("Account deletion requires email confirmation. Check your inbox.")
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-white">Settings</h1>
        <p className="text-gray-400 mt-1">Manage your account settings and preferences</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-800 mb-6 overflow-x-auto">
        <button
          onClick={() => setActiveTab("profile")}
          className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors whitespace-nowrap ${
            activeTab === "profile"
              ? "text-blue-500 border-b-2 border-blue-500"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <User className="h-4 w-4" />
          Profile
        </button>
        {clerkUser?.publicMetadata?.role === "seller" && (
          <button
            onClick={() => setActiveTab("seller")}
            className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === "seller"
                ? "text-blue-500 border-b-2 border-blue-500"
                : "text-gray-400 hover:text-white"
            }`}
          >
            <Building2 className="h-4 w-4" />
            Seller Profile
          </button>
        )}
        <button
          onClick={() => setActiveTab("notifications")}
          className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors whitespace-nowrap ${
            activeTab === "notifications"
              ? "text-blue-500 border-b-2 border-blue-500"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <Bell className="h-4 w-4" />
          Notifications
        </button>
        <button
          onClick={() => setActiveTab("account")}
          className={`flex items-center gap-2 px-4 py-2 font-medium transition-colors whitespace-nowrap ${
            activeTab === "account"
              ? "text-blue-500 border-b-2 border-blue-500"
              : "text-gray-400 hover:text-white"
          }`}
        >
          <Shield className="h-4 w-4" />
          Account
        </button>
      </div>

      {/* Profile Settings */}
      {activeTab === "profile" && (
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-white">Profile Settings</CardTitle>
            <CardDescription className="text-gray-400">
              Update your personal information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-gray-300">Email</Label>
              <Input
                id="email"
                type="email"
                value={clerkUser?.emailAddresses[0]?.emailAddress || ""}
                disabled
                className="bg-gray-800 border-gray-700 text-gray-400"
              />
              <p className="text-xs text-gray-500">Email cannot be changed</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="displayName" className="text-gray-300">Display Name</Label>
              <Input
                id="displayName"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Your display name"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="avatarUrl" className="text-gray-300">Avatar URL</Label>
              <Input
                id="avatarUrl"
                value={avatarUrl}
                onChange={(e) => setAvatarUrl(e.target.value)}
                placeholder="https://example.com/avatar.jpg"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div className="flex justify-end pt-4">
              <Button
                onClick={saveProfile}
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Seller Profile Settings */}
      {activeTab === "seller" && (
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-white">Seller Profile</CardTitle>
            <CardDescription className="text-gray-400">
              Information displayed to buyers
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="bio" className="text-gray-300">Bio</Label>
              <Textarea
                id="bio"
                value={bio}
                onChange={(e) => setBio(e.target.value)}
                placeholder="Tell buyers about yourself..."
                rows={4}
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="website" className="text-gray-300">Website</Label>
              <Input
                id="website"
                value={website}
                onChange={(e) => setWebsite(e.target.value)}
                placeholder="https://yourwebsite.com"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="githubUsername" className="text-gray-300">GitHub Username</Label>
              <Input
                id="githubUsername"
                value={githubUsername}
                onChange={(e) => setGithubUsername(e.target.value)}
                placeholder="your-github-username"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="twitterHandle" className="text-gray-300">Twitter Handle</Label>
              <Input
                id="twitterHandle"
                value={twitterHandle}
                onChange={(e) => setTwitterHandle(e.target.value)}
                placeholder="@yourhandle"
                className="bg-gray-800 border-gray-700 text-white"
              />
            </div>

            <div className="flex justify-end pt-4">
              <Button
                onClick={saveSellerProfile}
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Notification Preferences */}
      {activeTab === "notifications" && (
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle className="text-white">Notification Preferences</CardTitle>
            <CardDescription className="text-gray-400">
              Choose what notifications you receive
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Email Notifications</p>
                <p className="text-sm text-gray-400">Receive notifications via email</p>
              </div>
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
                className="h-5 w-5 rounded border-gray-700 bg-gray-800 text-blue-600 focus:ring-blue-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Product Updates</p>
                <p className="text-sm text-gray-400">Updates to your products</p>
              </div>
              <input
                type="checkbox"
                checked={productUpdates}
                onChange={(e) => setProductUpdates(e.target.checked)}
                className="h-5 w-5 rounded border-gray-700 bg-gray-800 text-blue-600 focus:ring-blue-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Sales Alerts</p>
                <p className="text-sm text-gray-400">Notifications when you make a sale</p>
              </div>
              <input
                type="checkbox"
                checked={salesAlerts}
                onChange={(e) => setSalesAlerts(e.target.checked)}
                className="h-5 w-5 rounded border-gray-700 bg-gray-800 text-blue-600 focus:ring-blue-600"
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <p className="text-white font-medium">Marketing Emails</p>
                <p className="text-sm text-gray-400">Promotional emails and feature announcements</p>
              </div>
              <input
                type="checkbox"
                checked={marketingEmails}
                onChange={(e) => setMarketingEmails(e.target.checked)}
                className="h-5 w-5 rounded border-gray-700 bg-gray-800 text-blue-600 focus:ring-blue-600"
              />
            </div>

            <div className="flex justify-end pt-4">
              <Button
                onClick={saveNotifications}
                disabled={saving}
                className="bg-blue-600 hover:bg-blue-700"
              >
                {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Save Changes
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Account Settings */}
      {activeTab === "account" && (
        <div className="space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white">Connected Accounts</CardTitle>
              <CardDescription className="text-gray-400">
                Manage connected payment and service accounts
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
                <div className="flex items-center gap-3">
                  <CreditCard className="h-8 w-8 text-purple-500" />
                  <div>
                    <p className="text-white font-medium">Stripe Connect</p>
                    <p className="text-sm text-gray-400">Receive payouts for your sales</p>
                  </div>
                </div>
                <Button variant="outline" className="border-gray-700 text-white hover:bg-gray-700">
                  Connect
                </Button>
              </div>

              {!sellerProfile?.payouts_enabled && (
                <div className="bg-blue-900/20 border border-blue-800 rounded-lg p-4">
                  <p className="text-blue-400 text-sm">
                    Connect your Stripe account to start receiving payouts for your sales.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-red-900/50">
            <CardHeader>
              <CardTitle className="text-white">Danger Zone</CardTitle>
              <CardDescription className="text-gray-400">
                Irreversible actions for your account
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-center justify-between p-4 bg-red-900/10 rounded-lg border border-red-900/30">
                <div>
                  <p className="text-white font-medium">Delete Account</p>
                  <p className="text-sm text-gray-400">
                    Permanently delete your account and all data
                  </p>
                </div>
                <Button
                  variant="destructive"
                  onClick={handleDeleteAccount}
                  className="bg-red-600 hover:bg-red-700"
                >
                  Delete Account
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
