'use client'

import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/button'
import { DashboardPasswordReset } from '@/components/auth/DashboardPasswordReset'
import { useRouter } from 'next/navigation'
import { useState } from 'react'

export default function DashboardPage() {
  const { user, profile, loading } = useAuth()
  const router = useRouter()
  const [showPasswordReset, setShowPasswordReset] = useState(false)

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  // This page should be protected by middleware, but just in case
  if (!user) {
    router.push('/auth/login')
    return null
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
        
        <div className="grid gap-6 md:grid-cols-2">
          {/* User Profile Card */}
          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Profile</h2>
            <div className="space-y-2">
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Name:</strong> {profile?.full_name || 'Not set'}</p>
              <p><strong>Member since:</strong> {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}</p>
            </div>
            <div className="flex gap-2 mt-4">
              <Button 
                variant="outline" 
                onClick={() => router.push('/profile')}
              >
                Edit Profile
              </Button>
              <Button 
                variant="outline" 
                onClick={() => setShowPasswordReset(!showPasswordReset)}
              >
                {showPasswordReset ? 'Hide' : 'Reset Password'}
              </Button>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <Button 
                variant="outline" 
                className="w-full justify-start"
                onClick={() => router.push('/movies')}
              >
                Browse Movies
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-start"
                onClick={() => router.push('/favorites')}
              >
                My Favorites
              </Button>
              <Button 
                variant="outline" 
                className="w-full justify-start"
                onClick={() => router.push('/watchlist')}
              >
                My Watchlist
              </Button>
            </div>
          </div>
        </div>

        {/* Password Reset Section */}
        {showPasswordReset && (
          <div className="mt-8 bg-card rounded-lg border p-6">
            <DashboardPasswordReset 
              onSuccess={() => {
                // Optional: show a success message or perform additional actions
                setTimeout(() => setShowPasswordReset(false), 3000)
              }}
            />
          </div>
        )}

        {/* Recent Activity */}
        <div className="mt-8 bg-card rounded-lg border p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="text-muted-foreground">
            <p>No recent activity yet. Start by browsing some movies!</p>
          </div>
        </div>
      </div>
    </div>
  )
}
