"use client"
import { createClient } from '@/lib/supabase/client';
import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

export default function AuthCallbackPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    if (code) {
      const supabase = createClient();
      supabase.auth.exchangeCodeForSession(code)
        .then((result) => {
          console.log('exchangeCodeForSession result:', result);
          if (!result.error) {
            router.replace('/');
          } else {
            setError(result.error.message);
          }
        })
        .catch((err) => {
          setError('Lỗi không xác định: ' + err?.message);
          console.error('exchangeCodeForSession catch:', err);
        });
    } else {
      setError('No code found in callback URL.');
    }
    // eslint-disable-next-line
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-[300px]">
      <h2 className="text-xl font-semibold mb-2">Đang xử lý đăng nhập Google...</h2>
      {error && <div className="text-red-500 mt-4">{error}</div>}
    </div>
  );
} 