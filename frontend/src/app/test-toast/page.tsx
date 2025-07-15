'use client'

import { Button } from '@/components/ui/button'
import { toast } from 'react-hot-toast'

export default function ToastTestPage() {
  const testToasts = () => {
    toast.success('Success toast test!')
    toast.error('Error toast test!')
    toast('Info toast test!', { icon: '🔍' })
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-md">
      <h1 className="text-2xl font-bold mb-8">Toast Test Page</h1>
      <Button onClick={testToasts} className="w-full">
        Test Toasts
      </Button>
    </div>
  )
}
