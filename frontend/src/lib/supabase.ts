import { createClient } from "@supabase/supabase-js";

/**
 * Reusable Supabase client for the browser and Server Components.
 * DO NOT expose service_role key here.  Use only the public anon key.
 */
export const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL!,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
); 