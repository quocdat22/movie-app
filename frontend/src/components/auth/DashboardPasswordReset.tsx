'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { authService } from '@/lib/auth'
import { Eye, EyeOff, Lock, CheckCircle, Key, AlertCircle } from 'lucide-react'
import { useAuth } from '@/components/providers/AuthProvider'
import { toast } from 'react-hot-toast'

interface DashboardPasswordResetProps {
  onSuccess?: () => void
}

export function DashboardPasswordReset({ onSuccess }: DashboardPasswordResetProps) {
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
    nonce: ''
  })
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isLoading, setIsLoading] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const [needsReauth, setNeedsReauth] = useState(false)
  const [reauthSent, setReauthSent] = useState(false)
  const { user } = useAuth()

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

  const validateConfirmPassword = (password: string, confirmPassword: string) => {
    if (!confirmPassword) return 'Please confirm your password'
    if (password !== confirmPassword) return 'Passwords do not match'
    return ''
  }

  const validateForm = () => {
    const newErrors: Record<string, string> = {}

    const passwordError = validatePassword(formData.password)
    if (passwordError) newErrors.password = passwordError

    const confirmPasswordError = validateConfirmPassword(formData.password, formData.confirmPassword)
    if (confirmPasswordError) newErrors.confirmPassword = confirmPasswordError

    if (needsReauth && !formData.nonce) {
      newErrors.nonce = 'Verification code is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSendReauth = async () => {
    setIsLoading(true)
    setErrors({})

    try {
      const { error } = await authService.reauthenticate()
      
      if (error) {
        toast.error(`Failed to send verification code: ${error.message}`)
        return false
      } else {
        setReauthSent(true)
        setNeedsReauth(true)
        toast.success('A verification code has been sent to your email')
        return true
      }
    } catch (error) {
      toast.error('Failed to send verification code')
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const handlePasswordUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsLoading(true)
    setErrors({})

    try {
      console.log('Updating password...')
      
      // Try to update password with nonce if available
      const result = await authService.updatePassword(
        formData.password, 
        needsReauth ? formData.nonce : undefined
      )
      
      console.log('Update result:', result)

      if (result.error) {
        const errorMessage = result.error.message.toLowerCase()
        
        // Check if password is the same as current password
        if (errorMessage.includes('new password should be different') || 
            errorMessage.includes('same as') ||
            errorMessage.includes('already')) {
          console.log('Error: Password is the same as current password')
          toast.error('New password must be different from your current password. Please choose a different password.')
          setIsLoading(false)
          return
        }
        
        // Check if reauthentication is required
        if (errorMessage.includes('reauthentication') || 
            errorMessage.includes('nonce') || 
            errorMessage.includes('verification') ||
            errorMessage.includes('recent sign')) {
          
          if (!needsReauth) {
            // First time we encounter this error - send reauthentication
            console.log('Reauthentication required, sending nonce...')
            const sent = await handleSendReauth()
            if (!sent) {
              setIsLoading(false)
            }
            return
          } else {
            // Nonce was wrong or expired
            setErrors({ nonce: 'Invalid or expired verification code. Please try again.' })
            setIsLoading(false)
            return
          }
        } else if (errorMessage.includes('timeout')) {
          toast.error('Password update timed out. Please try again.')
          setIsLoading(false)
          return
        } else {
          toast.error(result.error.message)
          setIsLoading(false)
          return
        }
      }

      // Success case: No error means the update was successful
      console.log('Password updated successfully')
      toast.success('Your password has been updated successfully!')
      setIsSuccess(true)
      onSuccess?.()
    } catch (error) {
      console.error('Unexpected error during password update:', error)
      toast.error('An unexpected error occurred while updating password')
    } finally {
      setIsLoading(false)
    }
  }

  const handleInputChange = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({ ...prev, [field]: e.target.value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const getPasswordStrength = (password: string) => {
    let strength = 0
    if (password.length >= 8) strength++
    if (/[a-z]/.test(password)) strength++
    if (/[A-Z]/.test(password)) strength++
    if (/[0-9]/.test(password)) strength++
    if (/[^A-Za-z0-9]/.test(password)) strength++
    return strength
  }

  const getPasswordStrengthLabel = (strength: number) => {
    switch (strength) {
      case 0:
      case 1: return { label: 'Very Weak', color: 'text-red-500' }
      case 2: return { label: 'Weak', color: 'text-orange-500' }
      case 3: return { label: 'Fair', color: 'text-yellow-500' }
      case 4: return { label: 'Good', color: 'text-blue-500' }
      case 5: return { label: 'Strong', color: 'text-green-500' }
      default: return { label: '', color: '' }
    }
  }

  const resetForm = () => {
    setFormData({ password: '', confirmPassword: '', nonce: '' })
    setErrors({})
    setIsSuccess(false)
    setShowPassword(false)
    setShowConfirmPassword(false)
    setNeedsReauth(false)
    setReauthSent(false)
  }

  if (isSuccess) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 text-green-600">
          <CheckCircle className="h-5 w-5" />
          <h3 className="text-lg font-semibold">Password Updated Successfully!</h3>
        </div>
        <p className="text-muted-foreground">
          Your password has been updated successfully. You can continue using your account with the new password.
        </p>
        <Button 
          onClick={resetForm}
          variant="outline"
        >
          Update Another Password
        </Button>
      </div>
    )
  }

  const passwordStrength = getPasswordStrength(formData.password)
  const strengthInfo = getPasswordStrengthLabel(passwordStrength)

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <h3 className="text-lg font-semibold flex items-center gap-2">
          <Key className="h-5 w-5" />
          Update Your Password
        </h3>
        <p className="text-sm text-muted-foreground">
          Enter a new password for your account: <strong>{user?.email}</strong>
        </p>
      </div>

      {needsReauth && reauthSent && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
          <div className="flex items-start gap-2">
            <AlertCircle className="h-4 w-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium text-blue-800">Verification Required</p>
              <p className="text-blue-700">
                We've sent a verification code to your email. Please enter it below to confirm your password change.
              </p>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handlePasswordUpdate} className="space-y-4">
        {/* New Password Field */}
        <div className="space-y-2">
          <Label htmlFor="new-password">New Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="new-password"
              type={showPassword ? 'text' : 'password'}
              placeholder="Enter your new password"
              value={formData.password}
              onChange={handleInputChange('password')}
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
          {formData.password && (
            <div className="flex items-center gap-2 text-xs">
              <span>Strength:</span>
              <span className={strengthInfo.color}>{strengthInfo.label}</span>
              <div className="flex gap-1 ml-2">
                {[1, 2, 3, 4, 5].map((level) => (
                  <div
                    key={level}
                    className={`h-1 w-4 rounded ${
                      passwordStrength >= level ? 'bg-current' : 'bg-gray-200'
                    } ${
                      passwordStrength >= level ? strengthInfo.color.replace('text-', 'text-') : ''
                    }`}
                  />
                ))}
              </div>
            </div>
          )}
          {errors.password && <p className="text-sm text-red-500">{errors.password}</p>}
        </div>

        {/* Confirm Password Field */}
        <div className="space-y-2">
          <Label htmlFor="confirm-password">Confirm New Password</Label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="confirm-password"
              type={showConfirmPassword ? 'text' : 'password'}
              placeholder="Confirm your new password"
              value={formData.confirmPassword}
              onChange={handleInputChange('confirmPassword')}
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

        {/* Verification Code Field (shown only if reauthentication is needed) */}
        {needsReauth && (
          <div className="space-y-2">
            <Label htmlFor="verification-code">Verification Code</Label>
            <Input
              id="verification-code"
              type="text"
              placeholder="Enter the code from your email"
              value={formData.nonce}
              onChange={handleInputChange('nonce')}
              className={`${errors.nonce ? 'border-red-500' : ''}`}
              disabled={isLoading}
              autoComplete="off"
            />
            {errors.nonce && <p className="text-sm text-red-500">{errors.nonce}</p>}
            <p className="text-xs text-muted-foreground">
              Didn't receive the code? 
              <button
                type="button"
                onClick={handleSendReauth}
                className="text-blue-600 hover:text-blue-800 ml-1"
                disabled={isLoading}
              >
                Send again
              </button>
            </p>
          </div>
        )}

        {errors.submit && (
          <div className="text-sm text-red-500 bg-red-50 p-3 rounded-md border border-red-200">
            <strong>Error:</strong> {errors.submit}
          </div>
        )}

        <div className="flex gap-2">
          {!needsReauth ? (
            <Button 
              type="submit" 
              disabled={isLoading || !formData.password || !formData.confirmPassword}
              className="flex-1"
            >
              {isLoading ? 'Updating Password...' : 'Update Password'}
            </Button>
          ) : (
            <>
              <Button 
                type="submit" 
                disabled={isLoading || !formData.password || !formData.confirmPassword || !formData.nonce}
                className="flex-1"
              >
                {isLoading ? 'Updating Password...' : 'Update Password'}
              </Button>
              {!reauthSent && (
                <Button 
                  type="button"
                  variant="outline"
                  onClick={handleSendReauth}
                  disabled={isLoading}
                >
                  {isLoading ? 'Sending...' : 'Send Code'}
                </Button>
              )}
            </>
          )}
        </div>
      </form>
    </div>
  )
}
