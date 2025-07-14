import Image from 'next/image';

interface CastMember {
  id: number;
  name: string;
  character: string;
  profile_path: string | null;
}

interface CastListProps {
  cast: CastMember[];
}

export function CastList({ cast }: CastListProps) {
  return (
    <div className="flex space-x-4 overflow-x-auto pb-4">
      {cast.map((member) => (
        <div key={member.id} className="w-32 shrink-0 flex flex-col items-center text-center">
          <div className="relative h-32 w-32 overflow-hidden rounded-full bg-muted">
            <Image
              src={member.profile_path ?? '/next.svg'}
              alt={member.name}
              fill
              sizes="128px"
              className="object-cover"
            />
          </div>
          <p className="mt-2 w-full truncate font-semibold">{member.name}</p>
          <p className="w-full truncate text-sm text-muted-foreground">{member.character}</p>
        </div>
      ))}
    </div>
  );
} 