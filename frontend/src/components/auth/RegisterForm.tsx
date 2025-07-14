"use client"

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authService } from '@/lib/auth'
import { Eye, EyeOff, Mail, Lock, User } from 'lucide-react'

interface RegisterFormProps {
  onSuccess?: () => void
  onSwitchToLogin?: () => void
}

export function RegisterForm({ onSuccess, onSwitchToLogin }: RegisterFormProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    fullName: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!email) return 'Email is required'
    if (!emailRegex.test(email)) return 'Please enter a valid email address'
    if (email.length > 254) return 'Email is too long'
    return ''
  }

  const validateFullName = (fullName: string) => {
    if (!fullName.trim()) return 'Full name is required'
    if (fullName.trim().length < 2) return 'Full name must be at least 2 characters'
    if (fullName.length > 100) return 'Full name is too long'
    if (!/^[a-zA-Z\s'-]+$/.test(fullName)) return 'Full name can only contain letters, spaces, hyphens, and apostrophes'
    return ''
  }

  const validatePassword = (password: string) => {
    if (!password) return 'Password is required'
    if (password.length < 8) return 'Password must be at least 8 characters'
    if (password.length > 128) return 'Password is too long'
    if (!/(?=.*[a-z])/.test(password)) return 'Password must contain at least one lowercase letter'
    if (!/(?=.*[A-Z])/.test(password)) return 'Password must contain at least one uppercase letter'
    if (!/(?=.*\d)/.test(password)) return 'Password must contain at least one number'
    if (!/(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/.test(password)) return 'Password must contain at least one special character'
    return ''
  }

  const validateConfirmPassword = (confirmPassword: string, password: string) => {
    if (!confirmPassword) return 'Please confirm your password'
    if (confirmPassword !== password) return 'Passwords do not match'
    return ''
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    const emailError = validateEmail(formData.email)
    if (emailError) newErrors.email = emailError

    const fullNameError = validateFullName(formData.fullName)
    if (fullNameError) newErrors.fullName = fullNameError

    const passwordError = validatePassword(formData.password)
    if (passwordError) newErrors.password = passwordError

    const confirmPasswordError = validateConfirmPassword(formData.confirmPassword, formData.password)
    if (confirmPasswordError) newErrors.confirmPassword = confirmPasswordError

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const validateField = (field: keyof typeof formData, value: string) => {
    let error = ''
    switch (field) {
      case 'email':
        error = validateEmail(value)
        break
      case 'fullName':
        error = validateFullName(value)
        break
      case 'password':
        error = validatePassword(value)
        break
      case 'confirmPassword':
        error = validateConfirmPassword(value, formData.password)
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
      const { user, session, error } = await authService.signUp(
        formData.email,
        formData.password,
        { full_name: formData.fullName }
      )

      if (error) {
        setErrors({ submit: error.message })
        return
      }

      if (user) {
        // Show success message for email confirmation
        setErrors({ 
          submit: 'Success! Please check your email to confirm your account before signing in.' 
        })
        
        // Optionally switch to login after a delay
        setTimeout(() => {
          onSwitchToLogin?.()
        }, 3000)
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
    
    // Real-time validation on blur or after user stops typing (except for confirmPassword which needs immediate feedback)
    if (field === 'confirmPassword') {
      validateField(field, value)
    } else {
      const timeoutId = setTimeout(() => {
        validateField(field, value)
      }, 300)
      return () => clearTimeout(timeoutId)
    }
  }

  const handleInputBlur = (field: keyof typeof formData) => (e: React.FocusEvent<HTMLInputElement>) => {
    validateField(field, e.target.value)
  }

  const getPasswordStrength = (password: string) => {
    let strength = 0
    if (password.length >= 6) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/\d/.test(password)) strength++
    if (/[^a-zA-Z\d]/.test(password)) strength++
    return strength
  }

  const passwordStrength = getPasswordStrength(formData.password)
  const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-blue-500', 'bg-green-500']
  const strengthLabels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']

  return (
    <div className="w-full max-w-md mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h1 className="text-2xl font-bold">Create account</h1>
        <p className="text-muted-foreground">Sign up to start discovering movies</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Full Name Field */}
        <div className="space-y-2">
          <Label htmlFor="fullName">Full Name</Label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="fullName"
              type="text"
              placeholder="Enter your full name"
              value={formData.fullName}
              onChange={handleInputChange('fullName')}
              onBlur={handleInputBlur('fullName')}
              className={`pl-10 ${errors.fullName ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="name"
            />
          </div>
          {errors.fullName && <p className="text-sm text-red-500">{errors.fullName}</p>}
        </div>

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
              placeholder="Create a password"
              value={formData.password}
              onChange={handleInputChange('password')}
              onBlur={handleInputBlur('password')}
              className={`pl-10 pr-10 ${errors.password ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="new-password"
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
          
          {/* Password Strength Indicator */}
          {formData.password && (
            <div className="space-y-1">
              <div className="flex space-x-1">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div
                    key={level}
                    className={`h-2 w-full rounded-full ${
                      passwordStrength >= level ? strengthColors[passwordStrength - 1] : 'bg-gray-200'
                    }`}
                  />
                ))}
              </div>
              <p className="text-xs text-muted-foreground">
                Password strength: {strengthLabels[passwordStrength - 1] || 'Very Weak'}
              </p>
            </div>
          )}
          
          {errors.password && <p className="text-sm text-red-500">{errors.password}</p>}
        </div>

        {/* Confirm Password Field */}
        <div className="space-y-2">
          <Label htmlFor="confirmPassword">Confirm Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="confirmPassword"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm your password"
              value={formData.confirmPassword}
              onChange={handleInputChange('confirmPassword')}
              onBlur={handleInputBlur('confirmPassword')}
              className={`pl-10 pr-10 ${errors.confirmPassword ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="new-password"
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
              disabled={isLoading}
            >
              {showConfirmPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
          {errors.confirmPassword && <p className="text-sm text-red-500">{errors.confirmPassword}</p>}
        </div>

        {/* Submit Error/Success */}
        {errors.submit && (
          <div className={`p-3 text-sm border rounded-md ${
            errors.submit.includes('Success') 
              ? 'text-green-600 bg-green-50 border-green-200' 
              : 'text-red-600 bg-red-50 border-red-200'
          }`}>
            {errors.submit}
          </div>
        )}

        {/* Submit Button */}
        <Button 
          type="submit" 
          className="w-full" 
          disabled={isLoading}
        >
          {isLoading ? 'Creating account...' : 'Create account'}
        </Button>
      </form>

      {/* Switch to Login */}
      <div className="text-center text-sm">
        <span className="text-muted-foreground">Already have an account? </span>
        <button
          type="button"
          onClick={onSwitchToLogin}
          className="text-primary hover:underline font-medium"
          disabled={isLoading}
        >
          Sign in
        </button>
      </div>
    </div>
  )
}
