# 🔐 Authentication Guide

**Type:** Simple password-based authentication  
**Purpose:** Prevent public access while keeping implementation minimal  
**Security Level:** Basic (suitable for non-sensitive data)

---

## 🎯 Overview

This app uses a simple site-wide password gate to restrict access. All users share the same password, and authentication is tracked via a session cookie.

### How It Works

1. User visits any page → redirected to `/login` if not authenticated
2. User enters password → validated against environment variable
3. On success → cookie is set for 7 days
4. User can access all pages while cookie is valid
5. Logout button available on all pages (top-right corner)

---

## ⚙️ Setup

### 1. Set Environment Variable

**For Local Development:**

Create a `.env` file in the project root:

```bash
GLOBA_SITE_PASSWORD=your-secret-password-here
```

**For Vercel Deployment:**

1. Go to your project settings in Vercel
2. Navigate to "Environment Variables"
3. Add: `GLOBA_SITE_PASSWORD` = `your-secret-password-here`
4. Redeploy

### 2. Default Password

If no environment variable is set, the default password is:

```
kinderspiele2024
```

**⚠️ IMPORTANT:** Change this before deploying to production!

---

## 🏗️ Implementation Details

### Files Created

```
src/
├── hooks.server.ts                    # Middleware to protect all routes (excludes /api/auth)
├── routes/
│   ├── login/
│   │   └── +page.svelte              # Login page
│   └── api/
│       └── auth/
│           ├── login/+server.ts      # Login endpoint
│           └── logout/+server.ts     # Logout endpoint
```

### How It Works

The `hooks.server.ts` middleware:
- Checks for `authenticated` cookie on every request
- **Allows** `/api/auth/*` endpoints (so login can work)
- **Allows** `/login` page
- **Redirects** all other routes to `/login` if not authenticated
- **Redirects** to home if authenticated user tries to access `/login`

### Cookie Details

- **Name:** `authenticated`
- **Type:** HttpOnly, SameSite=strict
- **Secure:** Only in production (HTTPS) - disabled for local dev
- **Duration:** 7 days
- **Path:** `/` (applies to entire site)

### Protected Routes

All routes are protected except:
- `/login` - The login page itself
- `/api/auth/*` - Authentication API endpoints (login/logout)

If a user tries to access any page without being authenticated, they're redirected to `/login`.

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

