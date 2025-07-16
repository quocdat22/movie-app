import { createClient } from "@supabase/supabase-js";

/**
 * Legacy Supabase client for backward compatibility.
 * For new auth features, use the clients from /lib/supabase/ directory.
 * DO NOT expose service_role key here. Use only the public anon key.
 */
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
);

// Re-export auth-specific clients for convenience
export { createClient as createBrowserClient } from './supabase/client'
export { createClient as createServerClient } from './supabase/server' 