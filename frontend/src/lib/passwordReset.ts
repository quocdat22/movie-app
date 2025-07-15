/**
 * Dedicated Password Reset Service
 * Handles all password reset related operations with proper error handling
 */

import { createClient } from '@/lib/supabase/client'

export interface PasswordResetResult {
  success: boolean
  error?: string
  data?: any
}

export class PasswordResetService {
  private supabase = createClient()

  /**
   * Step 1: Send password reset email
   */
  async sendResetEmail(email: string): Promise<PasswordResetResult> {
    try {
      console.log('PasswordResetService: Sending reset email to:', email)
      
      const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      })

      if (error) {
        console.error('PasswordResetService: Send email error:', error.message)
        return {
          success: false,
          error: error.message
        }
      }

      console.log('PasswordResetService: Reset email sent successfully')
      return {
        success: true,
        data: { message: 'Password reset email sent successfully' }
      }

    } catch (error) {
      console.error('PasswordResetService: Unexpected error sending email:', error)
      return {
        success: false,
        error: 'Failed to send password reset email'
      }
    }
  }

  /**
   * Step 2: Extract tokens from URL (after user clicks email link)
   */
  extractTokensFromUrl(): { accessToken?: string; refreshToken?: string } {
    try {
      const hashParams = new URLSearchParams(window.location.hash.substring(1))
      const searchParams = new URLSearchParams(window.location.search)
      
      return {
        accessToken: hashParams.get('access_token') || searchParams.get('access_token') || undefined,
        refreshToken: hashParams.get('refresh_token') || searchParams.get('refresh_token') || undefined
      }
    } catch (error) {
      console.error('PasswordResetService: Error extracting tokens:', error)
      return {}
    }
  }

  /**
   * Step 3: Verify the reset session is valid
   */
  async verifyResetSession(): Promise<PasswordResetResult> {
    try {
      console.log('PasswordResetService: Verifying reset session')
      
      // First check if we have tokens in URL
      const { accessToken, refreshToken } = this.extractTokensFromUrl()
      console.log('PasswordResetService: Extracted tokens:', { hasAccess: !!accessToken, hasRefresh: !!refreshToken })
      
      if (accessToken && refreshToken) {
        // Set session with extracted tokens
        console.log('PasswordResetService: Setting session with extracted tokens')
        const { data, error } = await this.supabase.auth.setSession({
          access_token: accessToken,
          refresh_token: refreshToken
        })

        if (error) {
          console.error('PasswordResetService: Failed to set session:', error.message)
          return {
            success: false,
            error: 'Invalid or expired reset link'
          }
        }

        console.log('PasswordResetService: Session set successfully')
        return {
          success: true,
          data: { user: data.user }
        }
      }

      // If no tokens in URL, check current session
      console.log('PasswordResetService: No tokens in URL, checking current session')
      const { data: sessionData, error: sessionError } = await this.supabase.auth.getSession()
      
      if (sessionError || !sessionData.session) {
        console.log('PasswordResetService: No valid session found')
        return {
          success: false,
          error: 'Invalid or expired reset link'
        }
      }
      
      console.log('PasswordResetService: Found existing valid session')
      return {
        success: true,
        data: { user: sessionData.session.user }
      }

    } catch (error) {
      console.error('PasswordResetService: Unexpected error verifying session:', error)
      return {
        success: false,
        error: 'Failed to verify reset link'
      }
    }
  }

  /**
   * Step 4: Update password with new password
   */
  async updatePassword(newPassword: string): Promise<PasswordResetResult> {
    try {
      console.log('PasswordResetService: Starting password update')

      // First ensure we have a valid session
      const sessionResult = await this.verifyResetSession()
      if (!sessionResult.success) {
        console.error('PasswordResetService: Session verification failed before password update')
        return sessionResult
      }

      console.log('PasswordResetService: Session verified, proceeding with password update')

      // Update the password
      const { data, error } = await this.supabase.auth.updateUser({
        password: newPassword
      })

      console.log('PasswordResetService: updateUser response:', {
        hasData: !!data,
        hasUser: !!data?.user,
        error: error?.message
      })

      if (error) {
        console.error('PasswordResetService: Password update error:', error.message)
        return {
          success: false,
          error: error.message
        }
      }

      console.log('PasswordResetService: Password updated successfully!')
      
      // Clean up URL parameters
      this.cleanupUrl()

      // Return success even if user data is null (common with password updates)
      return {
        success: true,
        data: { user: data?.user || { updated: true } }
      }

    } catch (error) {
      console.error('PasswordResetService: Unexpected error updating password:', error)
      return {
        success: false,
        error: 'Failed to update password'
      }
    }
  }

  /**
   * Clean up URL parameters after successful reset
   */
  private cleanupUrl() {
    try {
      // Remove hash and search params
      window.history.replaceState({}, document.title, window.location.pathname)
    } catch (error) {
      console.warn('PasswordResetService: Could not clean up URL:', error)
    }
  }

  /**
   * Complete password reset flow (convenience method)
   */
  async completePasswordReset(newPassword: string): Promise<PasswordResetResult> {
    return this.updatePassword(newPassword)
  }
}

// Export singleton instance
export const passwordResetService = new PasswordResetService()
