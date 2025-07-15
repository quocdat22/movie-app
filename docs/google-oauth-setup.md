# Google OAuth Integration Setup

This guide explains how to set up Google OAuth integration for the Movie App authentication system.

## Prerequisites

1. A Google Cloud Project
2. Supabase project configured
3. Movie App frontend and backend running

## Google Cloud Setup

### 1. Create OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project or create a new one
3. Navigate to **APIs & Services** > **Credentials**
4. Click **Create Credentials** > **OAuth Client ID**
5. Choose **Web application** as the application type

### 2. Configure OAuth Client

#### Authorized JavaScript Origins
Add your application domains:
- `http://localhost:3000` (for local development)
- `https://your-production-domain.com` (for production)

#### Authorized Redirect URIs
Add your Supabase Auth callback URL:
- `https://<your-supabase-project-ref>.supabase.co/auth/v1/callback`

You can find this URL in your Supabase Dashboard:
1. Go to **Authentication** > **Providers**
2. Expand the **Google** provider section
3. Copy the callback URL shown

### 3. Configure Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Choose **External** user type
3. Fill in the required information:
   - App name: "Movie App"
   - User support email
   - Developer contact information
4. Add authorized domains:
   - `<your-supabase-project-ref>.supabase.co`
   - Your production domain (if applicable)
5. Configure scopes:
   - `../auth/userinfo.email`
   - `../auth/userinfo.profile`
   - `openid`

## Supabase Configuration

### 1. Enable Google Provider

1. Go to your [Supabase Dashboard](https://supabase.com/dashboard)
2. Navigate to **Authentication** > **Providers**
3. Find **Google** and toggle it **enabled**
4. Add your Google OAuth credentials:
   - **Client ID**: From Google Cloud Console
   - **Client Secret**: From Google Cloud Console

### 2. Configure Redirect URLs

In your Supabase Dashboard:
1. Go to **Authentication** > **URL Configuration**
2. Add your application URLs to the redirect allow list:
   - `http://localhost:3000/auth/callback` (development)
   - `https://your-domain.com/auth/callback` (production)

## Environment Variables

Update your `.env.local` file:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project-ref.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-supabase-anon-key

# Site URL for OAuth redirects
NEXT_PUBLIC_SITE_URL=http://localhost:3000

# Google OAuth (Optional - only needed for Google One-Tap)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
```

## Testing the Integration

### 1. Development Testing

1. Start your Next.js application: `npm run dev`
2. Go to `/auth/login`
3. Click "Continue with Google"
4. Complete the OAuth flow
5. Verify you're redirected back and logged in

### 2. Error Handling

If authentication fails, users will be redirected to `/auth/auth-code-error` with helpful error messages.

## Security Considerations

1. **HTTPS in Production**: Always use HTTPS for OAuth redirects in production
2. **Domain Validation**: Ensure your authorized domains are correctly configured
3. **Client Secret**: Keep your Google OAuth client secret secure and never expose it in frontend code
4. **Redirect URL Validation**: Only add trusted domains to your redirect allow list

## Troubleshooting

### Common Issues

1. **"redirect_uri_mismatch" error**
   - Check that your redirect URI exactly matches what's configured in Google Cloud Console
   - Ensure the Supabase callback URL is added to Google OAuth settings

2. **"origin_mismatch" error**
   - Verify that your JavaScript origins are correctly configured
   - Check for trailing slashes or protocol mismatches

3. **Authentication fails silently**
   - Check browser developer tools for console errors
   - Verify environment variables are set correctly
   - Ensure Supabase Google provider is enabled

### Debug Steps

1. Check browser network tab for failed requests
2. Verify environment variables are loaded
3. Check Supabase Auth logs in the dashboard
4. Test with a fresh browser session (clear cookies)

## Features Implemented

- ✅ Google OAuth sign-in button
- ✅ Seamless authentication flow
- ✅ Error handling and user feedback
- ✅ Integration with existing auth system
- ✅ Support for both login and register pages
- ✅ Proper redirect handling
- ✅ Middleware protection for OAuth routes

## Next Steps (Not Required)

Consider implementing:
- [ ] Google One-Tap integration for improved UX
- [ ] Additional OAuth providers (GitHub, Facebook, etc.)
- [ ] Account linking for users with multiple sign-in methods
- [ ] Profile picture from Google account
