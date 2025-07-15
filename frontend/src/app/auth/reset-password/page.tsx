'use client'

import { NewResetPasswordForm } from '@/components/auth/NewResetPasswordForm'

export default function ResetPasswordPage() {
  return (
    <div className="container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
      <NewResetPasswordForm 
        onSuccess={() => {
          console.log('Password reset completed successfully')
        }}
      />
    </div>
  )
}
