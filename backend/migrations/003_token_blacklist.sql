-- Sprint 3 Task 3: Token Blacklist Table
-- This table stores revoked JWT tokens for security

CREATE TABLE IF NOT EXISTS token_blacklist (
    id SERIAL PRIMARY KEY,
    jti VARCHAR(255) NOT NULL UNIQUE,  -- JWT ID (unique token identifier)
    user_id UUID NOT NULL,             -- User who owned the token
    blacklisted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    reason VARCHAR(255) DEFAULT 'logout',  -- Reason for blacklisting
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_token_blacklist_jti ON token_blacklist(jti);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_user_id ON token_blacklist(user_id);
CREATE INDEX IF NOT EXISTS idx_token_blacklist_expires_at ON token_blacklist(expires_at);

-- Cleanup function to remove expired tokens
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM token_blacklist 
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Optional: Create a scheduled job to cleanup expired tokens
-- This would typically be set up in your deployment environment
-- COMMENT: Consider running cleanup_expired_tokens() daily via cron or similar

-- Row Level Security (RLS) policies
ALTER TABLE token_blacklist ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own blacklisted tokens
CREATE POLICY token_blacklist_user_policy ON token_blacklist
    FOR ALL USING (auth.uid() = user_id);

-- Policy: Service accounts can manage all tokens
CREATE POLICY token_blacklist_service_policy ON token_blacklist
    FOR ALL USING (auth.jwt() ->> 'role' = 'service_role');

-- Grant permissions
GRANT SELECT, INSERT, DELETE ON token_blacklist TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON token_blacklist TO service_role;
