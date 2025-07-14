export interface UserProfile {
  id: string
  email: string
  full_name?: string
  avatar_url?: string
  created_at: string
  updated_at: string
}

export interface AuthUser {
  id: string
  email?: string
  user_metadata?: {
    full_name?: string
    avatar_url?: string
  }
}

export interface AuthSession {
  access_token: string
  refresh_token: string
  expires_in: number
  token_type: string
  user: AuthUser
}

export interface AuthError {
  message: string
  status?: number
}

export interface AuthState {
  user: AuthUser | null
  session: AuthSession | null
  loading: boolean
  error: AuthError | null
}
