# Admin Security Setup Guide

## Overview

The admin panel is now secured with a whitelist system. Only authorized email addresses or usernames can register as admin or be granted admin privileges.

## How to Configure Admin Whitelist

### Option 1: Using Environment Variables (Recommended)

Create a `.env` file in your project root (or set environment variables) with:

```env
ADMIN_WHITELIST=admin@example.com,superadmin@example.com,admin_user,another.admin@university.edu
```

**Format:**
- Comma-separated list of emails or usernames
- Case-insensitive (automatically converted to lowercase)
- Whitespace is automatically trimmed

### Option 2: Direct Configuration

Edit `config.py` and modify the `ADMIN_WHITELIST` directly:

```python
ADMIN_WHITELIST = [
    'admin@example.com',
    'superadmin@example.com',
    'admin_user',
    'another.admin@university.edu'
]
```

## Security Features

1. **Public Registration Protection:**
   - Admin role option has been removed from the public registration form
   - Even if someone tries to register as admin via API/form manipulation, they will be blocked unless whitelisted

2. **Admin Panel Protection:**
   - When creating new users in the admin panel, only whitelisted emails/usernames can be assigned admin role
   - When changing user roles, only whitelisted accounts can be promoted to admin

3. **Validation:**
   - Checks both email and username against the whitelist
   - Case-insensitive matching
   - Clear error messages when unauthorized attempts are made

## Example Setup

For a university system, you might set:

```env
ADMIN_WHITELIST=admin@university.edu,it.admin@university.edu,superadmin
```

This allows:
- `admin@university.edu` - can register as admin or be granted admin role
- `it.admin@university.edu` - can register as admin or be granted admin role
- `superadmin` (username) - can register as admin or be granted admin role

## Important Notes

- **Empty Whitelist = No Admins:** If `ADMIN_WHITELIST` is empty, NO ONE can register as admin or be granted admin role (except existing admins in the database)
- **Existing Admins:** Users who are already admins in the database are not affected by this change
- **Case Sensitivity:** All comparisons are case-insensitive
- **Security:** Keep your `.env` file secure and never commit it to version control

## Testing

1. Try registering with a non-whitelisted email as admin - should be blocked
2. Try registering with a whitelisted email as admin - should succeed
3. Try creating a user in admin panel with admin role but non-whitelisted email - should be blocked
4. Try changing a user's role to admin with non-whitelisted email - should be blocked

