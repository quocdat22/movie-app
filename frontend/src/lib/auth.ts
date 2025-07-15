import { createClient } from '@/lib/supabase/client'
import type { AuthUser, AuthSession, AuthError } from '@/types/auth'

/**
 * Auth utility functions for client-side operations
 */

export class AuthService {
  private supabase = createClient()

  /**
   * Get current user session
   */
  async getSession(): Promise<{ user: AuthUser | null; session: AuthSession | null; error: AuthError | null }> {
    try {
      const { data, error } = await this.supabase.auth.getSession()
      
      if (error) {
        return { user: null, session: null, error: { message: error.message } }
      }

      return {
        user: data.session?.user || null,
        session: data.session,
        error: null
      }
    } catch (error) {
      return {
        user: null,
        session: null,
        error: { message: 'Failed to get session' }
      }
    }
  }

  /**
   * Get current user
   */
  async getUser(): Promise<{ user: AuthUser | null; error: AuthError | null }> {
    try {
      const { data, error } = await this.supabase.auth.getUser()
      
      if (error) {
        return { user: null, error: { message: error.message } }
      }

      return { user: data.user, error: null }
    } catch (error) {
      return {
        user: null,
        error: { message: 'Failed to get user' }
      }
    }
  }

  /**
   * Sign in with email and password
   */
  async signInWithPassword(email: string, password: string) {
    try {
      const { data, error } = await this.supabase.auth.signInWithPassword({
        email,
        password
      })

      if (error) {
        return { user: null, session: null, error: { message: error.message } }
      }

      return { user: data.user, session: data.session, error: null }
    } catch (error) {
      return {
        user: null,
        session: null,
        error: { message: 'Failed to sign in' }
      }
    }
  }

  /**
   * Sign up with email and password
   */
  async signUp(email: string, password: string, userData?: { full_name?: string }) {
    try {
      const { data, error } = await this.supabase.auth.signUp({
        email,
        password,
        options: {
          data: userData
        }
      })

      if (error) {
        return { user: null, session: null, error: { message: error.message } }
      }

      return { user: data.user, session: data.session, error: null }
    } catch (error) {
      return {
        user: null,
        session: null,
        error: { message: 'Failed to sign up' }
      }
    }
  }

  /**
   * Sign out
   */
  async signOut() {
    try {
      const { error } = await this.supabase.auth.signOut()
      
      if (error) {
        return { error: { message: error.message } }
      }

      return { error: null }
    } catch (error) {
      return { error: { message: 'Failed to sign out' } }
    }
  }

  /**
   * Send password reset email
   */
  async sendPasswordResetEmail(email: string) {
    try {
      const { error } = await this.supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/auth/reset-password`
      })
      
      if (error) {
        return { error: { message: error.message } }
      }

      return { error: null }
    } catch (error) {
      return { error: { message: 'Failed to send password reset email' } }
    }
  }

  /**
   * Update user password (used after email verification or with reauthentication nonce)
   */
  async updatePassword(newPassword: string, nonce?: string) {
    try {
      console.log('Auth service: updatePassword called with nonce:', !!nonce)
      
      const updateData: { password: string; nonce?: string } = {
        password: newPassword
      }
      
      if (nonce) {
        updateData.nonce = nonce
        console.log('Auth service: Including nonce in update')
      }

      console.log('Auth service: Calling supabase.auth.updateUser')
      
      // Simple approach: just call the API
      const { data, error } = await this.supabase.auth.updateUser(updateData)

      console.log('Auth service: updateUser response:', { 
        hasData: !!data, 
        hasUser: !!data?.user,
        error: error?.message,
        success: !error
      })

      if (error) {
        console.log('Auth service: Update error:', error.message)
        return { user: null, error: { message: error.message } }
      }

      // Success - password updates often don't return user data, but that's okay
      console.log('Auth service: Update successful - returning success indicator')
      return { user: data?.user || { updated: true }, error: null }
      
    } catch (error) {
      console.error('Auth service: Unexpected error in updatePassword:', error)
      const errorMessage = error instanceof Error ? error.message : 'Failed to update password'
      return { user: null, error: { message: errorMessage } }
    }
  }

  /**
   * Verify password reset token
   */
  async verifyPasswordResetToken() {
    try {
      const { data, error } = await this.supabase.auth.getSession()
      
      if (error) {
        return { valid: false, error: { message: error.message } }
      }

      // Check if user has a valid session after clicking the reset link
      if (data.session && data.session.user) {
        return { valid: true, error: null }
      }

      return { valid: false, error: { message: 'Invalid or expired reset token' } }
    } catch (error) {
      return { valid: false, error: { message: 'Failed to verify reset token' } }
    }
  }

  /**
   * Sign in with Google OAuth
   */
  async signInWithGoogle() {
    try {
      const { data, error } = await this.supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })

      if (error) {
        return { error: { message: error.message } }
      }

      return { error: null }
    } catch (error) {
      return { error: { message: 'Failed to sign in with Google' } }
    }
  }

  /**
   * Sign in with OAuth provider (generic method)
   */
  async signInWithOAuth(provider: 'google' | 'github' | 'facebook') {
    try {
      const { data, error } = await this.supabase.auth.signInWithOAuth({
        provider,
        options: {
          redirectTo: `${window.location.origin}/auth/callback`
        }
      })

      if (error) {
        return { error: { message: error.message } }
      }

      return { error: null }
    } catch (error) {
      return { error: { message: `Failed to sign in with ${provider}` } }
    }
  }

  /**
   * Send reauthentication nonce
   */
  async reauthenticate() {
    try {
      console.log('Auth service: reauthenticate called')
      const { error } = await this.supabase.auth.reauthenticate()
      
      if (error) {
        console.log('Auth service: reauthenticate error:', error.message)
        return { error: { message: error.message } }
      }

      console.log('Auth service: reauthenticate successful')
      return { error: null }
    } catch (error) {
      console.error('Auth service: Unexpected error in reauthenticate:', error)
      return { error: { message: 'Failed to send reauthentication nonce' } }
    }
  }

  /**
   * Listen to auth state changes
   */
  onAuthStateChange(callback: (user: AuthUser | null, session: AuthSession | null) => void) {
    return this.supabase.auth.onAuthStateChange((event, session) => {
      callback(session?.user || null, session)
    })
  }
}

// Export singleton instance
export const authService = new AuthService()
