import Image from "next/image";
import Link from "next/link";

export interface MovieCardProps {
  id: number;
  title: string;
  poster_url: string | null;
  rating?: number;
  vote_average?: number;
}

export function MovieCard({ id, title, poster_url, rating, vote_average }: MovieCardProps) {
  const displayRating = rating ?? vote_average;
  const posterSrc = poster_url ?? "/next.svg"; // fallback
  return (
    <Link
      href={`/movies/${id}`}
      className="group relative flex flex-col overflow-hidden rounded-lg bg-muted/20 shadow-sm transition-transform hover:-translate-y-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
    >
      {/* Poster */}
      <div className="relative aspect-[2/3] w-full overflow-hidden bg-background">
        <Image
          src={posterSrc}
          alt={title}
          fill
          sizes="(max-width: 768px) 50vw, 25vw"
          className="object-cover transition-transform duration-300 group-hover:scale-105"
          priority={false}
        />
        {displayRating !== undefined && (
          <span className="absolute top-2 right-2 rounded-full bg-background/80 px-2 py-1 text-xs font-semibold shadow backdrop-blur">
            {displayRating.toFixed(1)} ★
          </span>
        )}
      </div>
      {/* Title */}
      <h3 className="truncate p-2 text-sm font-medium text-foreground/90 group-hover:text-foreground">
        {title}
      </h3>
    </Link>
  );
} 