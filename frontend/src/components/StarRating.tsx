import { Star } from "lucide-react";

interface StarRatingProps {
  rating: number; // A value from 0 to 10
  voteCount: number;
}

export function StarRating({ rating, voteCount }: StarRatingProps) {
  const ratingOutOfFive = rating / 2;
  const formattedVoteCount = voteCount.toLocaleString('en-US');

  return (
    <div className="flex items-center gap-2">
      <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
      <span className="font-bold text-lg">{ratingOutOfFive.toFixed(1)}</span>
      <span className="text-sm text-muted-foreground">({formattedVoteCount} votes)</span>
    </div>
  );
} 