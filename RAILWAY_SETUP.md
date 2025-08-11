# Railway Deployment Setup

## Quick Fix for Database Error

The "Internal Server Error" on `/register` is due to missing PostgreSQL database. Follow these steps:

### 1. Add PostgreSQL Database
1. Go to Railway dashboard → Your project
2. Click "Add Service" → "Database" → "PostgreSQL"
3. Wait for provisioning (1-2 minutes)

### 2. Environment Variables (Auto-set by Railway)
Railway automatically sets `DATABASE_URL` when PostgreSQL is added.

### 3. Manual Environment Variables (if needed)
Add these in Railway dashboard → Settings → Variables:
```
SECRET_KEY=your-long-random-secret-key-here
ADMIN_PASS=your-admin-password
WEBHOOK_SECRET=your-webhook-secret
```

### 4. Test Health Check
Visit: `https://your-app.railway.app/health`

Should return:
```json
{
  "status": "healthy",
  "message": "CIFIX Kids Hub is running!",
  "database": "connected"
}
```

### 5. Test Registration
Visit: `https://your-app.railway.app/register`

## Troubleshooting
- **Database disconnected**: Add PostgreSQL service in Railway
- **App won't start**: Check build logs in Railway dashboard
- **Still errors**: Check deployment logs for specific error messages