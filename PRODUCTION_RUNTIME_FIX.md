# ONA Towers production runtime fix

This revision separates **fatal runtime configuration errors** from **security hardening warnings**.

## What no longer takes the customer API offline

- A Supabase URL that omits `sslmode=require` is normalized automatically.
- An `ADMIN_PASSWORD` that is shorter than the recommended production length is reported as a warning instead of blocking residences, enquiries, analytics, or other public API routes.
- The production bootstrap password is not required to match the hash already stored in `admin_team_members` for normal admin sessions.

## What still blocks unsafe/broken runtime configuration

- `APP_ENV` is not `production` while the runtime is a Vercel production deployment.
- `DATABASE_URL` is not PostgreSQL in production.
- `DATABASE_URL` contains placeholder values instead of a real database connection string.

## Admin recovery behavior

Admin authentication remains database-backed. If the primary admin email is configured in `ADMIN_EMAIL`, the server-side `ADMIN_PASSWORD` may recover that primary account when the supplied login password matches the Vercel environment value. This supports deliberate password rotation without deleting the admin row.

`ADMIN_SESSION_SECRET` is still required for production admin sessions and should be a unique random value at least 32 characters long.

## Required Vercel variables

Set these in Vercel Project Settings and redeploy:

```text
APP_ENV=production
APP_DEBUG=false
AUTO_INIT_DB=false
DATABASE_URL=<exact Supabase pooler connection string>
ADMIN_EMAIL=<primary staff email>
ADMIN_PASSWORD=<server-side recovery/bootstrap password>
ADMIN_SESSION_SECRET=<unique random secret, 32+ characters>
VITE_API_BASE_URL=/api
```

Use the Supabase transaction pooler (port 6543) for the Vercel runtime when possible. The code also supports the session pooler, but reports it as a non-fatal production warning.

Keep `MIGRATION_DATABASE_URL` local for Alembic migrations rather than exposing it to the browser.

## Verification URLs

After deployment:

```text
/api/health
/api/health/config
/api/health/database
/api/residences
```

Expected behavior:

- `/api/health` -> HTTP 200
- `/api/health/config` -> HTTP 200 when there are no fatal operational errors; `warnings` may still be present
- `/api/health/database` -> HTTP 200, `schema: ready`
- `/api/residences` -> HTTP 200 with residence data

Then test a customer enquiry and admin sign-in.
