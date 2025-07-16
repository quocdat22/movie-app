"use client"

import { useEffect, useState } from "react";
import { CastList } from "@/components/CastList";

interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path: string | null;
}

interface CastData {
  cast: CastMember[];
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function CastSection({ id }: { id: string }) {
  const [data, setData] = useState<CastData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Prevent scroll restoration
    if (typeof window !== 'undefined') {
      window.history.scrollRestoration = 'manual';
    }

    setIsLoading(true);
    fetch(`${API_URL}/api/movies/${id}`)
      .then((res) => res.json())
      .then((result) => {
        setData(result);
        setIsLoading(false);
      })
      .catch((e) => {
        console.error(e);
        setIsLoading(false);
      });
  }, [id]);

  // Show loading skeleton instead of null to prevent layout shift
  if (isLoading) {
    return (
      <div className="mt-12 animate-pulse">
        <div className="h-8 w-48 bg-muted rounded mb-4" />
        <div className="flex gap-4 overflow-x-auto">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-40 w-28 bg-muted rounded flex-shrink-0" />
          ))}
        </div>
      </div>
    );
  }

  if (!data || !data.cast || data.cast.length === 0) {
    return null;
  }

  return (
    <div className="mt-12">
      <h2 className="text-2xl font-semibold">Top Billed Cast</h2>
      <CastList cast={data.cast} />
    </div>
  );
} 

export default CastSection; 