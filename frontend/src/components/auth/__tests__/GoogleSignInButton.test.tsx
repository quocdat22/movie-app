import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { GoogleSignInButton } from '@/components/auth/GoogleSignInButton'
import { authService } from '@/lib/auth'

// Mock the auth service
jest.mock('@/lib/auth', () => ({
  authService: {
    signInWithGoogle: jest.fn()
  }
}))

const mockAuthService = authService as jest.Mocked<typeof authService>

describe('GoogleSignInButton', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('renders correctly', () => {
    render(<GoogleSignInButton />)
    
    expect(screen.getByRole('button')).toBeInTheDocument()
    expect(screen.getByText('Continue with Google')).toBeInTheDocument()
  })

  it('shows loading state when clicked', async () => {
    mockAuthService.signInWithGoogle.mockResolvedValue({ error: null })
    
    render(<GoogleSignInButton />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    expect(screen.getByText('Signing in...')).toBeInTheDocument()
    expect(button).toBeDisabled()
  })

  it('calls authService.signInWithGoogle when clicked', async () => {
    mockAuthService.signInWithGoogle.mockResolvedValue({ error: null })
    
    render(<GoogleSignInButton />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(mockAuthService.signInWithGoogle).toHaveBeenCalledTimes(1)
    })
  })

  it('calls onError when authentication fails', async () => {
    const mockOnError = jest.fn()
    const errorMessage = 'Authentication failed'
    
    mockAuthService.signInWithGoogle.mockResolvedValue({ 
      error: { message: errorMessage } 
    })
    
    render(<GoogleSignInButton onError={mockOnError} />)
    
    const button = screen.getByRole('button')
    fireEvent.click(button)
    
    await waitFor(() => {
      expect(mockOnError).toHaveBeenCalledWith(errorMessage)
    })
  })

  it('can be disabled', () => {
    render(<GoogleSignInButton disabled />)
    
    const button = screen.getByRole('button')
    expect(button).toBeDisabled()
  })

  it('accepts custom children', () => {
    const customText = 'Sign in with Google Account'
    render(<GoogleSignInButton>{customText}</GoogleSignInButton>)
    
    expect(screen.getByText(customText)).toBeInTheDocument()
  })
})
