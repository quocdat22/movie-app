"use client"

import * as React from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Button } from "./ui/button"

export interface FilterState {
  genre: string
  year: string
}

interface MovieFiltersProps {
  genres: string[]
  onFilterChange: (filters: FilterState) => void
  initialFilters: FilterState
}

export function MovieFilters({
  genres,
  onFilterChange,
  initialFilters,
}: MovieFiltersProps) {
  const [filters, setFilters] = React.useState<FilterState>(initialFilters)

  const handleGenreChange = (value: string) => {
    setFilters((prev) => ({ ...prev, genre: value === "all" ? "" : value }))
  }

  const handleYearChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFilters((prev) => ({ ...prev, year: event.target.value }))
  }

  const handleApplyFilters = () => {
    onFilterChange(filters)
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 border-b">
      <div className="space-y-2">
        <Label htmlFor="genre">Genre</Label>
        <Select value={filters.genre || "all"} onValueChange={handleGenreChange}>
          <SelectTrigger id="genre">
            <SelectValue placeholder="Select a genre" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Genres</SelectItem>
            {genres.map((genre) => (
              <SelectItem key={genre} value={genre}>
                {genre}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label htmlFor="year">Year</Label>
        <Input
          id="year"
          type="text"
          inputMode="numeric"
          pattern="[0-9]*"
          placeholder="e.g., 2023"
          value={filters.year}
          onChange={handleYearChange}
        />
      </div>

      <div className="flex items-end">
        <Button onClick={handleApplyFilters} className="w-full">Apply Filters</Button>
      </div>
    </div>
  )
} 