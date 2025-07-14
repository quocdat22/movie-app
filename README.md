# Movie App

A full-stack movie application built with Next.js frontend and FastAPI backend, featuring comprehensive movie browsing, filtering, and Supabase integration.

## Features

- 🎬 Browse and search movies with detailed information
- 🔍 Advanced filtering by genre, release year, and more
- 📱 Responsive design with modern UI components
- 🎭 Cast information and movie details
- 🔄 State preservation for better user experience
- 🚀 Edge functions for data synchronization with TMDB API
- 📊 Pagination and infinite scrolling

## Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety and better development experience
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible UI components
- **Lucide React** - Beautiful icons

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation and serialization
- **Supabase** - PostgreSQL database with real-time features
- **Python 3.11+** - Backend runtime

### Database & Services
- **Supabase** - PostgreSQL database hosting
- **TMDB API** - Movie data source
- **Edge Functions** - Serverless functions for data processing

## Project Structure

```
movie/
├── frontend/           # Next.js application
│   ├── src/
│   │   ├── app/       # App router pages
│   │   ├── components/ # Reusable components
│   │   ├── hooks/     # Custom hooks
│   │   └── lib/       # Utilities and configurations
│   └── public/        # Static assets
├── backend/           # FastAPI application
│   ├── app/
│   │   ├── routers/   # API route handlers
│   │   ├── schemas.py # Pydantic models
│   │   ├── db.py      # Database utilities
│   │   └── main.py    # FastAPI app configuration
│   ├── tests/         # Backend tests
│   └── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 18+
- Python 3.11+
- Supabase account
- TMDB API key

### Environment Setup

1. **Backend Environment** (create `backend/.env`):
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
TMDB_API_KEY=your_tmdb_api_key
```

2. **Frontend Environment** (create `frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_anon_key
```

### Installation & Running

1. **Clone the repository**:
```bash
git clone https://github.com/quocdat22/movie-app.git
cd movie-app
```

2. **Backend Setup**:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

3. **Frontend Setup**:
```bash
cd frontend
npm install
npm run dev
```

4. **Access the application**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Database Setup

The project uses Supabase with the following key functions:
- `filter_movies` - Advanced movie filtering with pagination
- `get_all_genres` - Retrieve unique movie genres

### Edge Functions

- `fetch_popular_movies` - Imports popular movies from TMDB
- `fetch_new_movies` - Imports latest movies with duplicate checking

## API Endpoints

### Movies
- `GET /movies` - List movies with filtering and pagination
- `GET /movies/{id}` - Get movie details
- `GET /movies/search` - Search movies by title
- `GET /movies/genres` - Get all available genres

## Features in Detail

### Movie Browsing
- Grid layout with responsive design
- Movie cards with poster, title, and rating
- Infinite scroll with "Load More" functionality
- State preservation when navigating between pages

### Filtering & Search
- Filter by genre (multi-select)
- Filter by release year (range)
- Text search by movie title
- Sort by release year, title, or creation date

### Movie Details
- Full movie information with cast
- High-quality poster images
- Genre tags and release information
- Back navigation with state preservation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [TMDB API](https://www.themoviedb.org/documentation/api) for movie data
- [Supabase](https://supabase.com/) for database and backend services
- [Next.js](https://nextjs.org/) and [FastAPI](https://fastapi.tiangolo.com/) teams
