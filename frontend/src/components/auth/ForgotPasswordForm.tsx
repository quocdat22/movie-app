'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authService } from '@/lib/auth'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'
import Link from 'next/link'

interface ForgotPasswordFormProps {
  onSuccess?: () => void
  onBackToLogin?: () => void
}

export function ForgotPasswordForm({ onSuccess, onBackToLogin }: ForgotPasswordFormProps) {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email) return 'Email is required'
    if (!emailRegex.test(email)) return 'Please enter a valid email address'
    if (email.length > 254) return 'Email is too long'
    return ''
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    const emailError = validateEmail(email)
    if (emailError) {
      setError(emailError)
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const { error: resetError } = await authService.sendPasswordResetEmail(email)

      if (resetError) {
        setError(resetError.message)
        return
      }

      setIsSuccess(true)
      onSuccess?.()
    } catch (error) {
      setError('An unexpected error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
    if (error) setError('') // Clear error when user starts typing
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
              We've sent a password reset link to:
            </p>
            <p className="font-medium text-foreground">{email}</p>
          </div>
          
          <div className="text-sm text-muted-foreground space-y-2">
            <p>
              Click the link in the email to reset your password. The link will expire in 24 hours.
            </p>
            <p>
              Don't see the email? Check your spam folder or try again.
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
          
          <Button 
            onClick={onBackToLogin}
            variant="ghost"
            className="w-full flex items-center gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to login
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="w-full max-w-md mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Forgot your password?</h1>
        <p className="text-muted-foreground">
          Enter your email address and we'll send you a link to reset your password.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Field */}
        <div className="space-y-2">
          <Label htmlFor="email">Email address</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="Enter your email address"
              value={email}
              onChange={handleEmailChange}
              className={`pl-10 ${error ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="email"
              autoFocus
            />
          </div>
          {error && <p className="text-sm text-red-500">{error}</p>}
        </div>

        {/* Submit Button */}
        <Button 
          type="submit" 
          className="w-full" 
          disabled={isLoading || !email}
        >
          {isLoading ? 'Sending...' : 'Send reset link'}
        </Button>
      </form>

      {/* Back to Login */}
      <div className="text-center">
        <Button 
          onClick={onBackToLogin}
          variant="ghost"
          className="text-sm flex items-center gap-2"
          disabled={isLoading}
        >
          <ArrowLeft className="h-4 w-4" />
          Back to login
        </Button>
      </div>
    </div>
  )
}
