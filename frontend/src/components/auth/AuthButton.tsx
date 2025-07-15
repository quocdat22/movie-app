"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { AuthModal } from './AuthModal'
import { useAuth } from '@/components/providers/AuthProvider'
import { User, LogOut } from 'lucide-react'
import { useRouter } from 'next/navigation'

export function AuthButton() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const { user, profile, loading, signOut } = useAuth()
  const router = useRouter()

  const handleSignOut = async () => {
    await signOut()
  }

  const handleAuthSuccess = () => {
    // Auth state will be updated via AuthProvider
    setIsAuthModalOpen(false)
  }

  const handleUserNameClick = () => {
    router.push('/dashboard')
  }

  if (loading) {
    return (
      <div className="h-9 w-20 bg-muted animate-pulse rounded-md" />
    )
  }

  if (user) {
    return (
      <div className="flex items-center gap-2">
        <button
          onClick={handleUserNameClick}
          className="flex items-center gap-2 text-sm hover:text-foreground/80 transition-colors cursor-pointer"
        >
          <User className="h-4 w-4" />
          <span className="hidden sm:inline">
            {profile?.full_name || user.email?.split('@')[0] || 'User'}
          </span>
        </button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleSignOut}
          className="text-muted-foreground hover:text-foreground"
        >
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline ml-1">Sign out</span>
        </Button>
      </div>
    )
  }

  return (
    <>
      <Button 
        variant="default" 
        size="sm"
        onClick={() => setIsAuthModalOpen(true)}
      >
        Sign In
      </Button>
      
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />
    </>
  )
}
