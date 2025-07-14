import Image from 'next/image';
import { notFound } from 'next/navigation';

// Component Imports
import { Suspense } from 'react';
import dynamic from 'next/dynamic';
import { BackButton } from '@/components/BackButton';

const ExtraMovieDetails = dynamic(() => import('@/components/ExtraMovieDetails').then(m => m.ExtraMovieDetails), { ssr: false });
const CastSection = dynamic(() => import('@/components/CastSection'), { ssr: false });

interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path: string | null;
}

interface MovieLite {
  id: number;
  title: string;
  overview: string | null;
  release_year: number | null;
  poster_url: string | null;
  genre: string[] | null;
  /* heavy fields omitted in lite*/
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function getMovieLite(id: string): Promise<MovieLite | null> {
  try {
    const res = await fetch(`${API_URL}/movies/${id}?lite=true`, { next: { revalidate: 3600 } });
    if (!res.ok) {
      if (res.status === 404) {
        return null;
      }
      throw new Error('Failed to fetch movie');
    }
    return res.json();
  } catch (error) {
    console.error(error);
    return null;
  }
}

export default async function MovieDetailPage({ params }: { params: { id: string } }) {
  const movie = await getMovieLite(params.id);

  if (!movie) {
    notFound();
  }

  const posterSrc = movie.poster_url ?? '/next.svg';

  return (
    <div className="container py-8">
      <BackButton />
      
      <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
        {/* Poster */}
        <div className="md:col-span-1">
          <div className="relative aspect-[2/3] w-full max-w-sm mx-auto overflow-hidden rounded-lg shadow-lg">
            <Image
              src={posterSrc}
              alt={movie.title}
              fill
              sizes="(max-width: 768px) 90vw, 33vw"
              className="object-cover"
            />
          </div>
        </div>

        {/* Details */}
        <div className="md:col-span-2">
          <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">{movie.title}</h1>
          
          <div className="mt-2 flex items-center gap-4 text-sm text-muted-foreground">
            {movie.release_year && <span>{movie.release_year}</span>}
            {movie.release_year && movie.genre && <span>•</span>}
            {movie.genre && movie.genre.length > 0 && (
              <span>{movie.genre.join(', ')}</span>
            )}
          </div>

          <div className="mt-6">
            <h2 className="text-xl font-semibold">Overview</h2>
            <p className="mt-2 text-foreground/80">{movie.overview || 'No overview available.'}</p>
          </div>

          {/* Extra heavy details loaded progressively - moved back to original position */}
          <Suspense fallback={<div className="mt-6 animate-pulse h-40 bg-muted rounded" />}> 
            <ExtraMovieDetails id={params.id} />
          </Suspense>
        </div>
      </div>

      {/* Cast section at the bottom - with minimal height to prevent layout shift */}
      <div className="mt-12">
        <Suspense fallback={<div className="animate-pulse h-48 bg-muted rounded" />}>
          <CastSection id={params.id} />
        </Suspense>
      </div>
    </div>
  );
} 