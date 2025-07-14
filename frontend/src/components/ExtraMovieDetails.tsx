"use client"

import { useEffect, useState } from "react";
import { StarRating } from "@/components/StarRating";
import { TrailerModal } from "@/components/TrailerModal";

interface MovieDetails {
  id: number;
  vote_average: number | null;
  vote_count: number | null;
  trailer_key: string | null;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export function ExtraMovieDetails({ id }: { id: string }) {
  const [data, setData] = useState<MovieDetails | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/movies/${id}`)
      .then((res) => res.json())
      .then(setData)
      .catch((e) => console.error(e));
  }, [id]);

  if (!data) {
    // skeleton placeholder for ratings and trailer
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-6 w-32 bg-muted rounded" />
        <div className="h-10 w-24 bg-muted rounded" />
      </div>
    );
  }

  return (
    <>
      {data.vote_average != null && data.vote_count != null && (
        <div className="mt-4">
          <StarRating rating={data.vote_average} voteCount={data.vote_count} />
        </div>
      )}

      {data.trailer_key && (
        <div className="mt-6">
          <TrailerModal videoId={data.trailer_key} title="Trailer" />
        </div>
      )}
    </>
  );
} 