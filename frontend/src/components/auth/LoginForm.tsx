"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authService } from '@/lib/auth'
import { Eye, EyeOff, Mail, Lock } from 'lucide-react'
import { createClient } from '@/lib/supabase/client'
import { FcGoogle } from 'react-icons/fc'

interface LoginFormProps {
  onSuccess?: () => void
  onSwitchToRegister?: () => void
}

export function LoginForm({ onSuccess, onSwitchToRegister }: LoginFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email) return 'Email is required'
    if (!emailRegex.test(email)) return 'Please enter a valid email address'
    if (email.length > 254) return 'Email is too long'
    return ''
  }

  const validatePassword = (password: string) => {
    if (!password) return 'Password is required'
    if (password.length < 6) return 'Password must be at least 6 characters'
    if (password.length > 128) return 'Password is too long'
    return ''
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    const emailError = validateEmail(formData.email)
    if (emailError) newErrors.email = emailError

    const passwordError = validatePassword(formData.password)
    if (passwordError) newErrors.password = passwordError

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const validateField = (field: keyof typeof formData, value: string) => {
    let error = ''
    switch (field) {
      case 'email':
        error = validateEmail(value)
        break
      case 'password':
        error = validatePassword(value)
        break
    }
    
    setErrors(prev => ({ ...prev, [field]: error }))
    return error === ''
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)
    setErrors({})

    try {
      const { user, session, error } = await authService.signInWithPassword(
        formData.email,
        formData.password
      )

      if (error) {
        setErrors({ submit: error.message })
        return
      }

      if (user && session) {
        onSuccess?.()
      }
    } catch (error) {
      setErrors({ submit: 'An unexpected error occurred' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: keyof typeof formData) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Real-time validation on blur or after user stops typing
    const timeoutId = setTimeout(() => {
      validateField(field, value)
    }, 300)

    return () => clearTimeout(timeoutId)
  }

  const handleInputBlur = (field: keyof typeof formData) => (e: React.FocusEvent<HTMLInputElement>) => {
    validateField(field, e.target.value)
  }

  // Google Sign In Button
  const handleGoogleSignIn = async () => {
    const supabase = createClient();
    await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: typeof window !== 'undefined' ? `${window.location.origin}/auth/callback` : undefined,
      },
    });
  };

  return (
    <div className="w-full max-w-md mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Welcome back</h1>
        <p className="text-muted-foreground">Sign in to your account to continue</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Email Field */}
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="email"
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleInputChange('email')}
              onBlur={handleInputBlur('email')}
              className={`pl-10 ${errors.email ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="email"
            />
          </div>
          {errors.email && <p className="text-sm text-red-500">{errors.email}</p>}
        </div>

        {/* Password Field */}
        <div className="space-y-2">
          <Label htmlFor="password">Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleInputChange('password')}
              onBlur={handleInputBlur('password')}
              className={`pl-10 pr-10 ${errors.password ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
              disabled={isLoading}
            >
              {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.password && <p className="text-sm text-red-500">{errors.password}</p>}
        </div>

        {/* Submit Error */}
        {errors.submit && (
          <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
            {errors.submit}
          </div>
        )}

        {/* Submit Button */}
        <Button 
          type="submit" 
          className="w-full" 
          disabled={isLoading}
        >
          {isLoading ? 'Signing in...' : 'Sign in'}
        </Button>
        {/* Google Sign In Divider */}
        <div className="flex items-center my-2">
          <div className="flex-grow h-px bg-gray-200" />
          <span className="mx-2 text-gray-400 text-xs">or</span>
          <div className="flex-grow h-px bg-gray-200" />
        </div>
        {/* Google Sign In Button */}
        <Button
          type="button"
          variant="outline"
          className="w-full flex items-center justify-center gap-2 border-gray-300"
          onClick={handleGoogleSignIn}
          disabled={isLoading}
        >
          <FcGoogle className="w-5 h-5" />
          Sign in with Google
        </Button>
      </form>

      {/* Switch to Register */}
      <div className="text-center text-sm">
        <span className="text-muted-foreground">Don't have an account? </span>
        <button
          type="button"
          onClick={onSwitchToRegister}
          className="text-primary hover:underline font-medium"
          disabled={isLoading}
        >
          Sign up
        </button>
      </div>
    </div>
  )
}
