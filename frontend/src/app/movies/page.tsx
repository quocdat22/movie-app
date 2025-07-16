"use client"

import { useEffect, useState, useCallback } from "react"
import { useSearchParams, useRouter } from "next/navigation"

import { MovieList } from "@/components/MovieList"
import { MovieFilters, type FilterState } from "@/components/MovieFilters"
import { Button } from "@/components/ui/button"

interface Movie {
  id: number
  title: string
  poster_url: string | null
  rating?: number
  release_year?: number
  vote_average?: number
}

interface Pagination {
  page: number
  page_size: number
  total_pages: number
  total_items: number
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

// Debounce function
function debounce<F extends (...args: any[]) => any>(func: F, waitFor: number) {
    let timeout: ReturnType<typeof setTimeout> | null = null;
    return (...args: Parameters<F>): void => {
        if (timeout !== null) {
            clearTimeout(timeout);
        }
        timeout = setTimeout(() => func(...args), waitFor);
    };
}


export default function MoviesPage() {
  const router = useRouter()
  const searchParams = useSearchParams()

  const [movies, setMovies] = useState<Movie[]>([])
  const [pagination, setPagination] = useState<Pagination | null>(null)
  const [genres, setGenres] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingMore, setIsLoadingMore] = useState(false)

  const hasMore = pagination ? pagination.page < pagination.total_pages : false

  const fetchMovies = useCallback(async (params: URLSearchParams, loadMore = false) => {
    if(!loadMore) {
        setIsLoading(true);
        setMovies([]); // Reset movies on new filter/sort
    } else {
        setIsLoadingMore(true);
    }

    try {
      const res = await fetch(`${API_URL}/api/movies?${params.toString()}`)
      if (!res.ok) throw new Error("Failed to fetch movies")
      const body = await res.json()

      if(loadMore) {
        setMovies((prev) => [...prev, ...body.movies])  // Fixed: body.movies instead of body.data
      } else {
        setMovies(body.movies)  // Fixed: body.movies instead of body.data
      }
      // Fixed: extract pagination from top level response
      setPagination({
        page: body.page,
        page_size: body.per_page,
        total_pages: body.total_pages,
        total_items: body.total
      })
    } catch (error) {
      console.error(error)
      // TODO: show toast notification
    } finally {
      setIsLoading(false)
      setIsLoadingMore(false)
    }
  }, []);

  const fetchGenres = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/movies/genres`)
      if (!res.ok) throw new Error("Failed to fetch genres")
      const body = await res.json()
      setGenres(body.data)  // This is correct - genres API returns { data: [...] }
    } catch (error) {
      console.error(error)
    }
  }, []);

  useEffect(() => {
    fetchGenres()
  }, [fetchGenres])
  
  useEffect(() => {
    const params = new URLSearchParams(searchParams.toString())
    if(!params.has("page")) params.set("page", "1")
    if(!params.has("page_size")) params.set("page_size", "20")
    fetchMovies(params)
  }, [searchParams, fetchMovies])

  const handleFilterChange = (newFilters: FilterState) => {
    const params = new URLSearchParams(window.location.search)
    
    if (newFilters.genre) params.set("genre", newFilters.genre)
    else params.delete("genre")
    
    if (newFilters.year) params.set("release_year", newFilters.year)
    else params.delete("release_year")

    params.set("page", "1"); // Reset to first page on filter change
    router.push(`?${params.toString()}`)
  }
  
  const loadMoreMovies = () => {
    if (!pagination || isLoadingMore) return;
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", String(pagination.page + 1));
    fetchMovies(params, true);
  }

  const initialFilters: FilterState = {
    genre: searchParams.get("genre") || "",
    year: searchParams.get("release_year") || "",
  };

  return (
    <div className="container py-8">
      <MovieFilters genres={genres} onFilterChange={handleFilterChange} initialFilters={initialFilters} />
      
      {isLoading ? (
        <div className="text-center p-8">Loading movies...</div>
      ) : (
        <>
            <MovieList movies={movies} />
            <div className="mt-8 flex justify-center">
                {hasMore && (
                <Button onClick={loadMoreMovies} disabled={isLoadingMore}>
                    {isLoadingMore ? 'Loading...' : 'Load More'}
                </Button>
                )}
            </div>
        </>
      )}
    </div>
  )
} 