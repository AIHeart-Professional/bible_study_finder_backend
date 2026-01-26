# Supabase Auth Integration Guide

## Overview
This backend has been migrated to use Supabase's `auth.users` table instead of the custom `users` table for user information retrieval.

## Important Schema Considerations

### Current State
- **Supabase auth.users** uses `id` (UUID) as the primary key
- **Your groups table** may still have `leader_user_id` as BIGINT (from old schema)

### Required Database Migration

You have two options:

#### Option 1: Update groups table to use UUID (Recommended)
```sql
-- Migration: Update groups table to use UUID for leader_user_id
ALTER TABLE groups 
  ALTER COLUMN leader_user_id TYPE UUID USING leader_user_id::text::uuid;

-- Update foreign key constraint
ALTER TABLE groups 
  DROP CONSTRAINT IF EXISTS groups_leader_user_id_fkey;

ALTER TABLE groups 
  ADD CONSTRAINT groups_leader_user_id_fkey 
  FOREIGN KEY (leader_user_id) 
  REFERENCES auth.users(id) 
  ON DELETE SET NULL;
```

#### Option 2: Create a mapping table (If you need to keep BIGINT)
If you need to maintain BIGINT for backward compatibility, create a mapping:
```sql
CREATE TABLE user_id_mapping (
    bigint_id BIGSERIAL PRIMARY KEY,
    uuid_id UUID UNIQUE NOT NULL REFERENCES auth.users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Changes Made

### 1. `users_database.py`
- All queries now use `auth.users` instead of `users`
- User data is extracted from `raw_user_meta_data` JSONB field:
  - `first_name` from `raw_user_meta_data->>'first_name'`
  - `last_name` from `raw_user_meta_data->>'last_name'`
  - `username` from `raw_user_meta_data->>'username'`
- `id` (UUID) is used as `public_id`
- FCM tokens are stored in `raw_user_meta_data`

### 2. `groups_database.py`
- All JOIN queries updated to use `auth.users`
- Username extracted from `raw_user_meta_data->>'username'`
- User ID resolution methods updated to work with UUID

### 3. User ID Resolution
- `_resolve_user_id_from_public_id()` now returns UUID string (not BIGINT)
- `_resolve_user_public_id_from_user_id()` handles both UUID strings and ints for backward compatibility

## Testing Checklist

- [ ] Verify `get_user_by_email()` works with Supabase users
- [ ] Verify `get_user_by_username()` works with Supabase users
- [ ] Verify `get_user_by_public_id()` works with Supabase users
- [ ] Verify group queries return correct leader username
- [ ] Verify group member queries return correct usernames
- [ ] Verify group chat queries return correct usernames
- [ ] Verify group request queries return correct usernames
- [ ] Test FCM token registration/unregistration
- [ ] Test all endpoints that query user information

## Known Issues / TODO

1. **Schema Migration Required**: If your `groups` table still uses BIGINT for `leader_user_id`, you need to migrate it to UUID (see Option 1 above).

2. **User Creation**: The `create_user()` method is disabled because Supabase handles user creation through their Auth API. Users should be created via:
   - Supabase Auth API (recommended)
   - Supabase Dashboard
   - Frontend using Supabase client

3. **Password Verification**: Password verification is handled by Supabase Auth, not in this backend. The `login_user()` method in `users_service.py` may need to be updated to use Supabase Auth API instead of direct database queries.

4. **Foreign Key Constraints**: If you have other tables with foreign keys to the old `users` table, they need to be updated to reference `auth.users(id)` with UUID type.

## Next Steps

1. Run the database migration (Option 1 above) to update `groups.leader_user_id` to UUID
2. Update any other tables that reference users to use UUID
3. Test all endpoints thoroughly
4. Update `users_service.py` login method to use Supabase Auth API if needed
5. Remove or archive the old `users` table if no longer needed

