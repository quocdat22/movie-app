"use client"

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

export function BackButton() {
  const router = useRouter()

  const handleBack = () => {
    // Always use browser back to preserve state
    // The movies list page already has state management for this scenario
    if (typeof window !== 'undefined' && window.history.length > 1) {
      router.back()
    } else {
      // Fallback to movies page if no history
      router.push('/movies')
    }
  }

  return (
    <Button
      variant="outline"
      size="sm"
      onClick={handleBack}
      className="mb-6 inline-flex items-center gap-2 hover:bg-accent transition-colors"
    >
      <ArrowLeft className="h-4 w-4" />
      Back to Movies
    </Button>
  )
}
