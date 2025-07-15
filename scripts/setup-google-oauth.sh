#!/bin/bash

# Google OAuth Setup Script for Supabase
# Run this script after you have created Google OAuth credentials

echo "🔧 Google OAuth Setup for Supabase"
echo "=================================="
echo ""

# Check if required environment variables are set
if [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
    echo "❌ SUPABASE_ACCESS_TOKEN is not set"
    echo "   Get your access token from: https://supabase.com/dashboard/account/tokens"
    echo "   Then run: export SUPABASE_ACCESS_TOKEN='your-token'"
    exit 1
fi

if [ -z "$GOOGLE_CLIENT_ID" ]; then
    echo "❌ GOOGLE_CLIENT_ID is not set"
    echo "   Get this from Google Cloud Console OAuth credentials"
    echo "   Then run: export GOOGLE_CLIENT_ID='your-client-id'"
    exit 1
fi

if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "❌ GOOGLE_CLIENT_SECRET is not set"
    echo "   Get this from Google Cloud Console OAuth credentials"
    echo "   Then run: export GOOGLE_CLIENT_SECRET='your-client-secret'"
    exit 1
fi

PROJECT_REF="vpwvtaetbqzvzknokkso"

echo "📡 Enabling Google OAuth provider..."
echo "Project: $PROJECT_REF"
echo ""

# Enable Google OAuth provider
response=$(curl -s -X PATCH "https://api.supabase.com/v1/projects/$PROJECT_REF/config/auth" \
  -H "Authorization: Bearer $SUPABASE_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"external_google_enabled\": true,
    \"external_google_client_id\": \"$GOOGLE_CLIENT_ID\",
    \"external_google_secret\": \"$GOOGLE_CLIENT_SECRET\"
  }")

if [ $? -eq 0 ]; then
    echo "✅ Google OAuth provider configuration sent successfully!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Verify the configuration in your Supabase Dashboard"
    echo "2. Test the Google sign-in in your application"
    echo "3. Make sure your Google OAuth redirect URI is set to:"
    echo "   https://vpwvtaetbqzvzknokkso.supabase.co/auth/v1/callback"
else
    echo "❌ Failed to configure Google OAuth provider"
    echo "Response: $response"
fi

echo ""
echo "🔗 Useful links:"
echo "   • Supabase Dashboard: https://supabase.com/dashboard/project/vpwvtaetbqzvzknokkso/auth/providers"
echo "   • Google Cloud Console: https://console.cloud.google.com/apis/credentials"
echo ""
