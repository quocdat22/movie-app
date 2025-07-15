import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ForgotPasswordForm } from '@/components/auth/ForgotPasswordForm'
import { authService } from '@/lib/auth'

// Mock the auth service
jest.mock('@/lib/auth', () => ({
  authService: {
    sendPasswordResetEmail: jest.fn()
  }
}))

const mockAuthService = authService as jest.Mocked<typeof authService>

describe('ForgotPasswordForm', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders correctly', () => {
    render(<ForgotPasswordForm />)
    
    expect(screen.getByRole('heading', { name: /forgot your password/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/email address/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /send reset link/i })).toBeInTheDocument()
  })

  it('validates email field', async () => {
    render(<ForgotPasswordForm />)
    
    const submitButton = screen.getByRole('button', { name: /send reset link/i })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Email is required')).toBeInTheDocument()
    })
  })

  it('validates email format', async () => {
    render(<ForgotPasswordForm />)
    
    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send reset link/i })
    
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument()
    })
  })

  it('sends password reset email successfully', async () => {
    mockAuthService.sendPasswordResetEmail.mockResolvedValue({ error: null })
    
    render(<ForgotPasswordForm />)
    
    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send reset link/i })
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(mockAuthService.sendPasswordResetEmail).toHaveBeenCalledWith('test@example.com')
    })
    
    await waitFor(() => {
      expect(screen.getByText('Check your email')).toBeInTheDocument()
      expect(screen.getByText('test@example.com')).toBeInTheDocument()
    })
  })

  it('handles password reset email error', async () => {
    const errorMessage = 'User not found'
    mockAuthService.sendPasswordResetEmail.mockResolvedValue({ 
      error: { message: errorMessage } 
    })
    
    render(<ForgotPasswordForm />)
    
    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send reset link/i })
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText(errorMessage)).toBeInTheDocument()
    })
  })

  it('shows loading state when submitting', async () => {
    mockAuthService.sendPasswordResetEmail.mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ error: null }), 100))
    )
    
    render(<ForgotPasswordForm />)
    
    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send reset link/i })
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.click(submitButton)
    
    expect(screen.getByText('Sending...')).toBeInTheDocument()
    expect(submitButton).toBeDisabled()
  })

  it('calls onBackToLogin when back button is clicked', () => {
    const mockOnBackToLogin = jest.fn()
    render(<ForgotPasswordForm onBackToLogin={mockOnBackToLogin} />)
    
    const backButton = screen.getByText(/back to login/i)
    fireEvent.click(backButton)
    
    expect(mockOnBackToLogin).toHaveBeenCalled()
  })

  it('allows sending another email after success', async () => {
    mockAuthService.sendPasswordResetEmail.mockResolvedValue({ error: null })
    
    render(<ForgotPasswordForm />)
    
    const emailInput = screen.getByLabelText(/email address/i)
    const submitButton = screen.getByRole('button', { name: /send reset link/i })
    
    // Submit form successfully
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } })
    fireEvent.click(submitButton)
    
    await waitFor(() => {
      expect(screen.getByText('Check your email')).toBeInTheDocument()
    })
    
    // Click "Send another email" button
    const sendAnotherButton = screen.getByRole('button', { name: /send another email/i })
    fireEvent.click(sendAnotherButton)
    
    // Should return to form
    expect(screen.getByRole('heading', { name: /forgot your password/i })).toBeInTheDocument()
  })
})
