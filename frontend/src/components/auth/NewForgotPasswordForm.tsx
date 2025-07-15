'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Mail, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react'
import { toast } from 'react-hot-toast'
import { passwordResetService } from '@/lib/passwordReset'

interface ForgotPasswordProps {
  onBack?: () => void
}

export function NewForgotPasswordForm({ onBack }: ForgotPasswordProps) {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState('')

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email) {
      setError('Email is required')
      return
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const result = await passwordResetService.sendResetEmail(email)
      
      if (result.success) {
        setIsSuccess(true)
        toast.success('Password reset email sent!')
      } else {
        setError(result.error || 'Failed to send reset email')
        toast.error(result.error || 'Failed to send reset email')
      }
    } catch (error) {
      setError('An unexpected error occurred')
      toast.error('An unexpected error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  if (isSuccess) {
    return (
      <div className="w-full max-w-md mx-auto space-y-6">
        <div className="text-center space-y-4">
          <div className="flex justify-center">
            <CheckCircle className="h-16 w-16 text-green-500" />
          </div>
          
          <div className="space-y-2">
            <h1 className="text-2xl font-bold">Check your email</h1>
            <p className="text-muted-foreground">
              We've sent a password reset link to <strong>{email}</strong>
            </p>
            <p className="text-sm text-muted-foreground">
              Click the link in the email to reset your password. The link will expire in 1 hour.
            </p>
          </div>
        </div>
        
        <div className="flex flex-col space-y-3">
          <Button 
            onClick={() => {
              setIsSuccess(false)
              setEmail('')
            }}
            variant="outline"
            className="w-full"
          >
            Send another email
          </Button>
          
          {onBack && (
            <Button 
              onClick={onBack}
              variant="ghost"
              className="w-full"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to login
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-md mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Reset your password</h1>
        <p className="text-muted-foreground">
          Enter your email address and we'll send you a link to reset your password.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="email">Email address</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setError('')
              }}
              className={`pl-10 ${error ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="email"
            />
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
        </div>

        <Button 
          type="submit" 
          className="w-full" 
          disabled={isLoading || !email}
        >
          {isLoading ? 'Sending...' : 'Send reset link'}
        </Button>
      </form>

      {onBack && (
        <div className="text-center">
          <Button 
            onClick={onBack}
            variant="ghost"
            className="text-sm"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to login
          </Button>
        </div>
      )}
    </div>
  )
}
