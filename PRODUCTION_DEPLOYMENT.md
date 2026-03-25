# Production Deployment Guide

## Overview
This guide covers deploying the Agentic Search Engine (ASE) to production with the latest production-ready configurations.

## Key Updates for Production

### 1. API Connection ✅
- **Production API URL**: `https://api.ase.penivera.me`
- **SKILL.md Updated**: Contains production URL
- **Frontend Configuration**: Uses `VITE_API_URL` environment variable
- **CORS Enabled**: Backend configured to accept requests from:
  - `https://ase.penivera.me`
  - `https://www.ase.penivera.me`
  - Development localhost:3000, localhost:5173, localhost:5174

### 2. Frontend Configuration ✅
- **Environment Variables**:
  - `.env` - Local development
  - `.env.development` - Dev builds
  - `.env.production` - Production build
- **API Service**: `src/services/api.ts`
  - Provides TypeScript-typed API functions
  - Error handling and logging
  - Bearer token support for protected endpoints
- **Real API Integration**: SearchResults page now fetches from production API
- **Build Optimization**: 
  - Minification enabled
  - Terser config drops console logs
  - Code splitting for vendor libraries
  - No sourcemaps in production

### 3. Backend Configuration ✅
- **CORS Middleware**: Added to handle frontend requests
- **Health Check**: `GET /health` endpoint for monitoring
- **Dynamic Database**: Uses `DATABASE_URL` from environment
- **Dynamic Alembic**: Migrations read from config
- **Production-Ready**:
  - Pydantic validation
  - Error handling with proper HTTP status codes
  - Bearer token authentication
  - Query logging and caching

### 4. Docker Support ✅
- **Dockerfile.backend**: 
  - Python 3.12-slim base
  - Auto-runs migrations
  - Health checks included
  - Production-optimized
- **Dockerfile.frontend**:
  - Multi-stage build (smaller final image)
  - Uses `serve` for production serving
  - Health checks included
- **docker-compose.yml**:
  - PostgreSQL database (optional)
  - Containerized backend
  - Containerized frontend
  - Automatic health checks

## Deployment Options

### Option 1: Render Platform (Current Setup)

#### Backend Deployment
```bash
# Environment variables needed in Render:
DATABASE_URL=postgresql://user:password@host/dbname
INGEST_API_TOKENS=your-secret-tokens
SEARCH_CACHE_TTL_SECONDS=60
```

#### Frontend Deployment
```bash
# Build command:
cd frontend && npm run build

# Start command:
npm run preview
# or use: serve -s dist -l 3000

# Environment variables:
VITE_API_URL=https://api.ase.penivera.me/api
```

### Option 2: Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Option 3: Kubernetes

Create ConfigMap for environment variables:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ase-config
data:
  VITE_API_URL: "https://api.ase.penivera.me/api"
  DATABASE_URL: "postgresql://..."
```

## Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/ase_db

# Authentication
INGEST_API_TOKENS=token1,token2,token3

# Cache
SEARCH_CACHE_TTL_SECONDS=60

# Python Version (for Render)
PYTHON_VERSION=3.12.0
```

### Frontend
```env
# Production
VITE_API_URL=https://api.ase.penivera.me/api

# Development
VITE_API_URL=http://localhost:8000/api
```

## Production Checklist

- ✅ SKILL.md updated with production URL
- ✅ Frontend connected to production API
- ✅ CORS middleware configured
- ✅ Environment variables set up
- ✅ Database migrations automated
- ✅ Health check endpoints added
- ✅ Docker images created
- ✅ Error handling implemented
- ✅ API service layer created
- ✅ Production build optimization enabled

## Monitoring & Healthchecks

### Backend Health
```bash
curl https://api.ase.penivera.me/health
# Response:
# {"status": "ok", "database": "postgres"}
```

### Frontend Health
```bash
curl https://ase.penivera.me/
# Response: HTML page loads
```

### API Documentation
```bash
# Auto-generated Swagger docs
https://api.ase.penivera.me/docs
```

## Performance Optimization

### Frontend
- Tree-shaking enabled
- CSS minification via TailwindCSS
- JavaScript code splitting
- Lazy loading routes (recommended for future)
- Cache busting with content hashing

### Backend
- Query result caching (60s default)
- Precomputed embeddings stored in DB
- Async/await for non-blocking I/O
- Connection pooling for PostgreSQL

## Security Considerations

1. **API Key Management**
   - Use environment variables (never hardcode)
   - Rotate tokens regularly
   - Use different tokens per environment

2. **CORS Configuration**
   - Explicit allowed origins
   - No wildcard in production
   - Credentials enabled only when needed

3. **Database**
   - Use strong passwords
   - Enable SSL connections
   - Regular backups
   - Use managed PostgreSQL (Render, AWS RDS, etc.)

4. **Secrets Management**
   - Never commit .env files
   - Use platform-specific secrets (Render, GitHub, etc.)
   - Rotate sensitive data regularly

## Troubleshooting

### Frontend can't reach API
- Check `VITE_API_URL` environment variable
- Verify backend CORS configuration
- Check network tab in browser DevTools
- Ensure backend is running and accessible

### Database connection errors
- Verify `DATABASE_URL` format
- Check database credentials
- Ensure migrations ran: `alembic upgrade head`
- Test connection: `psql <DATABASE_URL>`

### API searches return no results
- Check database has data
- Verify embeddings were computed
- Check query is not empty
- Test directly: `curl 'https://api.ase.penivera.me/api/search?query=test'`

## Next Steps

1. **CI/CD Integration**
   - GitHub Actions for automated testing and deployment

2. **Advanced Monitoring**
   - Application Performance Monitoring (APM)
   - Error tracking (Sentry)
   - Analytics (Plausible, Mixpanel)

3. **Scaling**
   - Database replication
   - Caching layer (Redis)
   - Load balancing
   - CDN for static assets

4. **Enhanced Features**
   - User authentication
   - Rate limiting
   - API versioning
   - Webhook integrations

---

## Deployment Status: ✅ PRODUCTION READY

All necessary configurations have been implemented to make the Agentic Search Engine production-ready.
