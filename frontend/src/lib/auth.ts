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
   * Reset password
   */
  async resetPassword(email: string) {
    try {
      const { error } = await this.supabase.auth.resetPasswordForEmail(email)
      
      if (error) {
        return { error: { message: error.message } }
      }

      return { error: null }
    } catch (error) {
      return { error: { message: 'Failed to reset password' } }
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
