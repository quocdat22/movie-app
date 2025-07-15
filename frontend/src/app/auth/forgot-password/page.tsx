'use client'

import { useRouter } from 'next/navigation'
import { NewForgotPasswordForm } from '@/components/auth/NewForgotPasswordForm'

export default function ForgotPasswordPage() {
  const router = useRouter()

  return (
    <div className="container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
      <NewForgotPasswordForm 
        onBack={() => router.push('/auth/login')}
      />
    </div>
  )
}
