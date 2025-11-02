# 🔐 Authentication Guide

**Type:** Two-tier password-based authentication
**Purpose:** Site-wide access control + admin panel access
**Security Level:** Basic (suitable for non-sensitive data)
**Last Updated:** 2025-11-02

---

## 🎯 Overview

This app uses a **two-tier authentication system**:

1. **Site-Wide Authentication:** Password gate for all users (shared password)
2. **Admin Authentication:** Separate password for admin panel access

Both authentication levels use environment variables and session cookies.

### Site-Wide Authentication Flow

1. User visits any page → redirected to `/login` if not authenticated
2. User enters password → validated against `GLOBA_SITE_PASSWORD` env var
3. On success → `authenticated` cookie set for 7 days
4. User can access all pages while cookie is valid

### Admin Authentication Flow

1. User with site access visits `/admin` → redirected to `/admin/login` if not admin
2. User enters admin password → validated against env var
3. On success → `admin_authenticated` cookie set
4. User can access admin panel

---

## ⚙️ Setup

### Environment Variables

Create a `.env` file in the project root:

```bash
# Site-wide authentication (required)
GLOBA_SITE_PASSWORD=your-site-password-here

# Admin authentication (optional, only if you need admin panel)
ADMIN_PASSWORD=your-admin-password-here

# Note: Environment variable has a typo ("GLOBA" not "GLOBAL")
# This is intentional to match the existing implementation
```

**⚠️ IMPORTANT:** The site password variable is named `GLOBA_SITE_PASSWORD` (typo in original implementation)

---

## 🏗️ Implementation Details

### Files

```
src/
├── hooks.server.ts                         # Middleware for both auth layers
├── routes/
│   ├── login/
│   │   └── +page.svelte                   # Site-wide login page
│   ├── admin/
│   │   ├── +page.svelte                   # Admin panel
│   │   └── login/
│   │       └── +page.svelte               # Admin login page
│   └── api/
│       ├── auth/
│       │   ├── login/+server.ts           # Site-wide login endpoint
│       │   └── logout/+server.ts          # Site-wide logout endpoint
│       └── admin/
│           └── verify/+server.ts          # Admin verification endpoint
```

### Middleware (hooks.server.ts)

The `hooks.server.ts` file implements both authentication layers:

**Site-Wide Auth:**
- Checks for `authenticated` cookie
- Allows `/login` and `/api/auth/*`
- Redirects unauthenticated users to `/login`

**Admin Auth:**
- Checks for `admin_authenticated` cookie
- Allows `/admin/login` and `/api/admin/*`
- Redirects non-admin users to `/admin/login`

### Cookies

**Site-Wide Cookie:**
- Name: `authenticated`
- Type: HttpOnly, SameSite=strict
- Duration: 7 days
- Path: `/`

**Admin Cookie:**
- Name: `admin_authenticated`
- Type: HttpOnly, SameSite=strict
- Duration: Session-based
- Path: `/admin`

### Protected Routes

**Site-Wide Protection (all routes except):**
- `/login` - Site login page
- `/api/auth/*` - Site auth endpoints

**Admin Protection (requires both cookies):**
- `/admin` - Admin panel
- `/admin/*` - Admin sub-pages

**Note:** Admin routes require BOTH site-wide authentication AND admin authentication.

---

## 🔄 User Flow

```
┌─────────────────────────────────────────────────┐
│ User visits https://yoursite.com/               │
└────────────┬────────────────────────────────────┘
             │
             ▼
    ┌────────────────────┐
    │ Has valid cookie?  │
    └────────┬───────────┘
             │
        ┌────┴────┐
        │         │
       No        Yes
        │         │
        ▼         ▼
  ┌──────────┐  ┌──────────────────┐
  │ Redirect │  │ Show requested   │
  │ to       │  │ page             │
  │ /login   │  └──────────────────┘
  └────┬─────┘
       │
       ▼
  ┌─────────────────────┐
  │ Login page          │
  │ Enter password      │
  └────┬────────────────┘
       │
       ▼
  ┌─────────────────────┐
  │ Submit to           │
  │ /api/auth/login     │
  └────┬────────────────┘
       │
       ▼
  ┌────────────────────┐
  │ Password correct?  │
  └────┬───────────────┘
       │
  ┌────┴────┐
  │         │
 Yes       No
  │         │
  │         ▼
  │    ┌──────────┐
  │    │ Show     │
  │    │ error    │
  │    └──────────┘
  │
  ▼
┌───────────────────┐
│ Set cookie        │
│ Redirect to home  │
└───────────────────┘
```

---

## 🧪 Testing

### Test Login

1. Start the dev server: `npm run dev`
2. Visit `http://localhost:5173`
3. You should be redirected to `/login`
4. Enter the password (from `.env` or default)
5. You should be redirected to home page
6. Try refreshing - you should stay logged in

### Test Logout

1. Click "Abmelden" button in top-right corner
2. You should be redirected to `/login`
3. Try visiting any page - you should be redirected back to `/login`

### Test on Vercel

After deployment:
1. Visit your Vercel URL
2. Confirm you're redirected to login
3. Test with correct password
4. Test with incorrect password
5. Test logout functionality

---

## 🔒 Security Considerations

### Current Security Level

- ✅ Prevents casual/public access
- ✅ HttpOnly cookies (can't be accessed by JavaScript)
- ✅ Secure flag (HTTPS only in production)
- ✅ SameSite strict (prevents CSRF)
- ❌ Single shared password (no individual users)
- ❌ Password stored in environment variable (not hashed)
- ❌ No rate limiting on login attempts
- ❌ No password recovery

### What This Is Good For

- ✅ Family/small group access
- ✅ Development/staging environments
- ✅ Non-sensitive data
- ✅ Quick deployment needs

### What This Is NOT Good For

- ❌ Sensitive personal data
- ❌ Multiple users with different permissions
- ❌ GDPR/compliance-critical applications
- ❌ Financial data
- ❌ Health data

### Improving Security (Optional)

If you need stronger security later:

1. **Add rate limiting:** Use Vercel Edge Config or a service like Upstash
2. **Hash passwords:** Use bcrypt instead of plain text comparison
3. **Individual users:** Add proper user accounts with separate passwords
4. **Two-factor auth:** Use services like Auth0, Clerk, or Supabase Auth
5. **Audit logging:** Track login attempts and access

---

## 🛠️ Customization

### Change Password Location

Edit `src/hooks.server.ts` and `src/routes/api/auth/login/+server.ts`:

```typescript
// Instead of environment variable
const SITE_PASSWORD = 'hardcoded-password';
```

### Change Cookie Duration

Edit `src/routes/api/auth/login/+server.ts`:

```typescript
cookies.set('authenticated', 'true', {
  // ...
  maxAge: 60 * 60 * 24 * 30  // 30 days instead of 7
});
```

### Change Login Page Styling

Edit `src/routes/login/+page.svelte` to customize the gradient, colors, text, etc.

### Add Multiple Passwords

Edit the validation logic to check against multiple passwords:

```typescript
const ALLOWED_PASSWORDS = ['password1', 'password2', 'password3'];

if (ALLOWED_PASSWORDS.includes(password)) {
  // Login successful
}
```

---

## 🐛 Troubleshooting

### "Redirect loop" after login

**Cause:** Cookie not being set properly  
**Solution:** Check that `secure: true` is compatible with your environment (use `secure: process.env.NODE_ENV === 'production'` for local dev)

### Can't access login page

**Cause:** Hooks logic error  
**Solution:** Check `src/hooks.server.ts` excludes `/login` from auth check

### Password not working

**Cause:** Environment variable not loaded  
**Solution:** 
- Check `.env` file exists
- Restart dev server after changing `.env`
- For Vercel: check environment variable is set in project settings

### Logged out after page refresh (local dev)

**Cause:** Secure cookie flag with HTTP  
**Solution:** Temporarily set `secure: false` for local development

---

## 📚 Related Documentation

- [CLAUDE.md](./CLAUDE.md) - Main entry point
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [API-REFERENCE.md](./API-REFERENCE.md) - API endpoints

---

**This simple auth system is perfect for family/small group deployments. For production apps with sensitive data, consider upgrading to a proper authentication service.**

