import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ResetPasswordForm } from '@/components/auth/ResetPasswordForm'
import { authService } from '@/lib/auth'
import { useRouter } from 'next/navigation'

// Mock the auth service
jest.mock('@/lib/auth', () => ({
  authService: {
    verifyPasswordResetToken: jest.fn(),
    updatePassword: jest.fn()
  }
}))

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn()
}))

const mockAuthService = authService as jest.Mocked<typeof authService>
const mockUseRouter = useRouter as jest.MockedFunction<typeof useRouter>
const mockPush = jest.fn()

describe('ResetPasswordForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: jest.fn(),
      forward: jest.fn(),
      refresh: jest.fn(),
      replace: jest.fn(),
      prefetch: jest.fn()
    })
  })

  it('shows loading state while verifying token', () => {
    // Mock token verification to never resolve
    mockAuthService.verifyPasswordResetToken.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    )
    
    render(<ResetPasswordForm />)
    
    expect(screen.getByText('Verifying reset link...')).toBeInTheDocument()
  })

  it('shows error for invalid token', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: false, 
      error: { message: 'Invalid token' } 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByText('Invalid or expired link')).toBeInTheDocument()
      expect(screen.getByRole('button', { name: /request new reset link/i })).toBeInTheDocument()
    })
  })

  it('renders form for valid token', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: true, 
      error: null 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /set new password/i })).toBeInTheDocument()
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument()
    })
  })

  it('validates password requirements', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: true, 
      error: null 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    })
    
    const passwordInput = screen.getByLabelText(/new password/i)
    const submitButton = screen.getByRole('button', { name: /update password/i })
    
    // Test weak password
    fireEvent.change(passwordInput, { target: { value: 'weak' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(/password must be at least 8 characters/i)).toBeInTheDocument()
    })
  })

  it('validates password confirmation', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: true, 
      error: null 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    })
    
    const passwordInput = screen.getByLabelText(/new password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /update password/i })
    
    fireEvent.change(passwordInput, { target: { value: 'ValidPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'DifferentPassword123!' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument()
    })
  })

  it('shows password strength indicator', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: true, 
      error: null 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    })
    
    const passwordInput = screen.getByLabelText(/new password/i)
    
    fireEvent.change(passwordInput, { target: { value: 'ValidPassword123!' } })
    
    await waitFor(() => {
      expect(screen.getByText(/password strength/i)).toBeInTheDocument()
    })
  })

  it('updates password successfully', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: true, 
      error: null 
    })
    mockAuthService.updatePassword.mockResolvedValue({ 
      user: { 
        id: '1', 
        email: 'test@example.com',
        app_metadata: {},
        user_metadata: {},
        aud: 'authenticated',
        created_at: '2023-01-01T00:00:00Z'
      } as any, 
      error: null 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    })
    
    const passwordInput = screen.getByLabelText(/new password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /update password/i })
    
    fireEvent.change(passwordInput, { target: { value: 'ValidPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'ValidPassword123!' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockAuthService.updatePassword).toHaveBeenCalledWith('ValidPassword123!')
    })
    
    await waitFor(() => {
      expect(screen.getByText('Password updated!')).toBeInTheDocument()
    })
  })

  it('handles password update error', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: true, 
      error: null 
    })
    mockAuthService.updatePassword.mockResolvedValue({ 
      user: null, 
      error: { message: 'Failed to update password' } 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByLabelText(/new password/i)).toBeInTheDocument()
    })
    
    const passwordInput = screen.getByLabelText(/new password/i)
    const confirmPasswordInput = screen.getByLabelText(/confirm password/i)
    const submitButton = screen.getByRole('button', { name: /update password/i })
    
    fireEvent.change(passwordInput, { target: { value: 'ValidPassword123!' } })
    fireEvent.change(confirmPasswordInput, { target: { value: 'ValidPassword123!' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Failed to update password')).toBeInTheDocument()
    })
  })

  it('navigates to forgot password page when request new link is clicked', async () => {
    mockAuthService.verifyPasswordResetToken.mockResolvedValue({ 
      valid: false, 
      error: { message: 'Invalid token' } 
    })
    
    render(<ResetPasswordForm />)
    
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /request new reset link/i })).toBeInTheDocument()
    })
    
    const requestNewLinkButton = screen.getByRole('button', { name: /request new reset link/i })
    fireEvent.click(requestNewLinkButton)
    
    expect(mockPush).toHaveBeenCalledWith('/auth/forgot-password')
  })
})
