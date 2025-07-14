'use client'

import { useState } from 'react'
import { useAuth } from '@/components/providers/AuthProvider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useRouter } from 'next/navigation'
import { createClient } from '@/lib/supabase/client'

export default function ProfilePage() {
  const { user, profile, loading, refreshProfile } = useAuth()
  const [isEditing, setIsEditing] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const [formData, setFormData] = useState({
    full_name: profile?.full_name || '',
    avatar_url: profile?.avatar_url || ''
  })
  const router = useRouter()
  const supabase = createClient()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!user) {
    router.push('/auth/login')
    return null
  }

  const handleSave = async () => {
    if (!user) return

    setIsSaving(true)
    try {
      const { error } = await supabase
        .from('profiles')
        .update({
          full_name: formData.full_name,
          avatar_url: formData.avatar_url,
          updated_at: new Date().toISOString()
        })
        .eq('id', user.id)

      if (error) {
        console.error('Error updating profile:', error)
        alert('Failed to update profile. Please try again.')
      } else {
        await refreshProfile()
        setIsEditing(false)
        alert('Profile updated successfully!')
      }
    } catch (error) {
      console.error('Error updating profile:', error)
      alert('Failed to update profile. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      full_name: profile?.full_name || '',
      avatar_url: profile?.avatar_url || ''
    })
    setIsEditing(false)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <Button
            variant="outline"
            onClick={() => router.back()}
            className="mb-4"
          >
            ← Back
          </Button>
          <h1 className="text-3xl font-bold">Profile</h1>
          <p className="text-muted-foreground mt-2">
            Manage your account information
          </p>
        </div>

        <div className="bg-card rounded-lg border p-6">
          <div className="space-y-6">
            {/* Email (Read-only) */}
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                value={user.email || ''}
                disabled
                className="mt-1"
              />
              <p className="text-sm text-muted-foreground mt-1">
                Email cannot be changed
              </p>
            </div>

            {/* Full Name */}
            <div>
              <Label htmlFor="full_name">Full Name</Label>
              {isEditing ? (
                <Input
                  id="full_name"
                  value={formData.full_name}
                  onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                  className="mt-1"
                  placeholder="Enter your full name"
                />
              ) : (
                <Input
                  id="full_name"
                  value={profile?.full_name || 'Not set'}
                  disabled
                  className="mt-1"
                />
              )}
            </div>

            {/* Avatar URL */}
            <div>
              <Label htmlFor="avatar_url">Avatar URL</Label>
              {isEditing ? (
                <Input
                  id="avatar_url"
                  value={formData.avatar_url}
                  onChange={(e) => setFormData({ ...formData, avatar_url: e.target.value })}
                  className="mt-1"
                  placeholder="Enter avatar image URL"
                />
              ) : (
                <Input
                  id="avatar_url"
                  value={profile?.avatar_url || 'Not set'}
                  disabled
                  className="mt-1"
                />
              )}
            </div>

            {/* Account Info */}
            <div className="border-t pt-4">
              <h3 className="font-semibold mb-2">Account Information</h3>
              <div className="space-y-2 text-sm text-muted-foreground">
                <p>
                  <strong>Account created:</strong>{' '}
                  {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'Unknown'}
                </p>
                <p>
                  <strong>Last updated:</strong>{' '}
                  {profile?.updated_at ? new Date(profile.updated_at).toLocaleDateString() : 'Never'}
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-4">
              {isEditing ? (
                <>
                  <Button onClick={handleSave} disabled={isSaving}>
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </Button>
                  <Button variant="outline" onClick={handleCancel} disabled={isSaving}>
                    Cancel
                  </Button>
                </>
              ) : (
                <Button onClick={() => setIsEditing(true)}>
                  Edit Profile
                </Button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
