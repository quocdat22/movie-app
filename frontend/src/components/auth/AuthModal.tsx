"use client"

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { LoginForm } from './LoginForm'
import { RegisterForm } from './RegisterForm'

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
  initialMode?: 'login' | 'register'
  onAuthSuccess?: () => void
}

export function AuthModal({ 
  isOpen, 
  onClose, 
  initialMode = 'login',
  onAuthSuccess 
}: AuthModalProps) {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode)

  const handleAuthSuccess = () => {
    onAuthSuccess?.()
    onClose()
  }

  const handleSwitchMode = () => {
    setMode(mode === 'login' ? 'register' : 'login')
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="sr-only">
            {mode === 'login' ? 'Sign In' : 'Sign Up'}
          </DialogTitle>
        </DialogHeader>
        
        <div className="px-1 py-4">
          {mode === 'login' ? (
            <LoginForm
              onSuccess={handleAuthSuccess}
              onSwitchToRegister={handleSwitchMode}
            />
          ) : (
            <RegisterForm
              onSuccess={handleAuthSuccess}
              onSwitchToLogin={handleSwitchMode}
            />
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
