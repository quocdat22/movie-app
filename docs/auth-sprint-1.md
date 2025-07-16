# Sprint 1: Foundation & Setup - Implementation Guide

## Overview
This sprint implements the foundation for Supabase Auth integration in the Movie App. It sets up the basic infrastructure needed for user authentication without implementing the full UI components.

## ✅ Completed Features

### Frontend Setup
1. **Supabase SSR Integration**
   - Installed `@supabase/ssr` package (replacing deprecated auth helpers)
   - Created client-side, server-side, and middleware Supabase clients
   - Set up authentication middleware for session management

2. **Auth Utilities & Types**
   - Created TypeScript interfaces for auth state management
   - Implemented `AuthService` class with core auth methods
   - Added support for sign in, sign up, sign out, and session management

3. **Environment Configuration**
   - Updated `.env.example` with auth-related environment variables
   - Structured auth configuration for development and production

### Backend Setup
1. **Authentication Dependencies**
   - Added PyJWT, cryptography, and python-multipart to requirements
   - Created JWT verification utilities
   - Implemented FastAPI auth dependencies

2. **Auth Router**
   - Created `/auth/me` endpoint for user profile retrieval
   - Added `/auth/status` endpoint for authentication status checking
   - Integrated with existing Supabase client

### Database Schema
1. **User Profiles Table**
   - Created `profiles` table extending `auth.users`
   - Implemented Row Level Security (RLS) policies
   - Added automatic profile creation trigger
   - Set up proper foreign key relationships

2. **Security Setup**
   - Enabled RLS on auth tables
   - Created policies for profile access control
   - Added automatic timestamp updates

## 🔧 File Structure

```
frontend/
├── src/
│   ├── lib/
│   │   ├── auth.ts                    # Auth service class
│   │   └── supabase/
│   │       ├── client.ts              # Browser client
│   │       ├── server.ts              # Server client
│   │       └── middleware.ts          # Auth middleware
│   ├── types/
│   │   └── auth.ts                    # Auth TypeScript interfaces
│   └── middleware.ts                  # Next.js middleware
└── .env.example                       # Environment variables

backend/
├── app/
│   ├── auth.py                        # JWT verification utilities
│   └── routers/
│       └── auth.py                    # Auth endpoints
├── requirements.txt                   # Updated dependencies
└── .env.example                       # Backend environment variables

database/
└── auth_schema.sql                    # Database schema setup
```

## 🚀 Environment Setup

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url
NEXT_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

### Backend (.env)
```env
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_JWT_SECRET=your_supabase_jwt_secret
TMDB_API_KEY=your_tmdb_api_key
```

## 📝 Database Setup Instructions

1. Run the SQL schema in Supabase SQL Editor:
   ```sql
   -- Execute the contents of database/auth_schema.sql
   ```

2. Verify the following tables and functions are created:
   - `public.profiles` table
   - RLS policies for profiles
   - `handle_new_user()` trigger function
   - `handle_updated_at()` trigger function

## 🔍 Testing the Setup

### Backend Endpoints
1. **Health Check**: `GET /healthz`
2. **Auth Status**: `GET /auth/status`
3. **User Profile**: `GET /auth/me` (requires authentication)

### Frontend Auth Service
```typescript
import { authService } from '@/lib/auth'

// Get current session
const { user, session, error } = await authService.getSession()

// Sign up new user
const result = await authService.signUp('email@example.com', 'password')
```

## 🎯 Next Steps (Sprint 2)

Sprint 1 provides the foundation. The next sprint will focus on:
1. Login/Register UI components
2. Route protection implementation
3. User context and state management
4. Auth forms with validation

## 🐛 Known Issues & Notes

1. **Import Errors**: Backend import errors are expected until dependencies are installed
2. **JWT Secret**: Must obtain JWT secret from Supabase dashboard → Settings → API
3. **CORS**: Currently allows all origins - restrict for production
4. **Error Handling**: Basic error handling implemented, can be enhanced in future sprints

## 🔒 Security Considerations

- All sensitive data stored in environment variables
- RLS enabled on user-related tables
- JWT tokens properly verified on backend
- Auto-generated profiles prevent orphaned users
- Middleware handles session refresh automatically
