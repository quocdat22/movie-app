'use client'

import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { AlertCircle } from 'lucide-react'

export default function AuthCodeErrorPage() {
  const router = useRouter()

  return (
    <div className="container mx-auto px-4 py-8 max-w-md">
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <AlertCircle className="h-16 w-16 text-red-500" />
        </div>
        
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">Authentication Error</h1>
          <p className="text-muted-foreground">
            There was an error processing your authentication request. This could be due to:
          </p>
        </div>
        
        <div className="text-left space-y-2 text-sm text-muted-foreground">
          <ul className="list-disc list-inside space-y-1">
            <li>The authentication code has expired</li>
            <li>The authentication was cancelled</li>
            <li>There was a network error during the process</li>
            <li>Invalid or missing authentication parameters</li>
          </ul>
        </div>
        
        <div className="flex flex-col space-y-3">
          <Button 
            onClick={() => router.push('/auth/login')}
            className="w-full"
          >
            Try Again
          </Button>
          
          <Button 
            variant="outline" 
            onClick={() => router.push('/')}
            className="w-full"
          >
            Go Home
          </Button>
        </div>
      </div>
    </div>
  )
}
