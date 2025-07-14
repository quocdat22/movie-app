'use client';

import { MovieCard } from '@/components/MovieCard';

// This should align with the props in MovieCard.tsx
export interface MovieCardProps {
  id: number;
  title: string;
  poster_url: string | null;
  rating?: number;
  vote_average?: number;
}


interface MovieListProps {
  movies: MovieCardProps[];
}

export function MovieList({ movies }: MovieListProps) {
  return (
      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {movies.map((movie) => (
          <MovieCard
            key={movie.id}
            id={movie.id}
            title={movie.title}
            poster_url={movie.poster_url}
          rating={movie.rating ?? movie.vote_average}
          />
        ))}
      </div>
  );
} 