# Deploy to Vercel Workflow

Step-by-step workflow for deploying projects to Vercel with pre and post-deploy verification.

## Pre-Deploy Checklist

### 1. Code Quality Checks
- [ ] **Lint Check**: Run `npm run lint` or `python -m pylint`
- [ ] **Type Check**: Run `npm run type-check` or `mypy .`
- [ ] **Format Check**: Run `prettier --check .` or `black --check .`
- [ ] **Security Scan**: Run `npm audit` or `safety check`

### 2. Build Verification
- [ ] **Local Build**: Run `npm run build` successfully
- [ ] **Bundle Size**: Check bundle size is within limits
- [ ] **Environment Variables**: Verify all required env vars are set
- [ ] **Dependencies**: Ensure all dependencies are installed

### 3. Testing
- [ ] **Unit Tests**: Run `npm test` or `pytest`
- [ ] **Integration Tests**: Run end-to-end tests
- [ ] **Manual Testing**: Test critical user flows locally

### 4. Configuration
- [ ] **Vercel Configuration**: Verify `vercel.json` is correct
- [ ] **Environment Variables**: Set production env vars in Vercel dashboard
- [ ] **Domain Settings**: Configure custom domains if needed
- [ ] **Build Settings**: Verify build commands and output directory

## Deployment Process

### Method 1: Git-based Deployment (Recommended)

```bash
# 1. Commit and push changes
git add .
git commit -m "feat: ready for deployment"
git push origin main

# 2. Vercel automatically deploys from main branch
# Monitor deployment at https://vercel.com/dashboard
```

### Method 2: CLI Deployment

```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Login to Vercel
vercel login

# 3. Deploy
vercel --prod

# 4. Follow prompts to configure project
```

### Method 3: Manual Deploy

```bash
# 1. Build locally
npm run build

# 2. Deploy build folder
vercel --prod --prebuilt
```

## Post-Deploy Verification

### 1. Functional Testing
- [ ] **Homepage**: Verify homepage loads correctly
- [ ] **Navigation**: Test all main navigation links
- [ ] **Forms**: Test contact forms, sign-up flows
- [ ] **API Endpoints**: Verify API routes work correctly

### 2. Performance Testing
- [ ] **Page Speed**: Check loading times with DevTools
- [ ] **Lighthouse Score**: Run Lighthouse audit
- [ ] **Core Web Vitals**: Verify LCP, FID, CLS metrics
- [ ] **Mobile Performance**: Test on mobile devices

### 3. SEO & Metadata
- [ ] **Meta Tags**: Verify title, description, OG tags
- [ ] **Sitemap**: Ensure sitemap.xml is accessible
- [ ] **Robots.txt**: Verify robots.txt is correct
- [ ] **Schema Markup**: Test structured data

### 4. Monitoring Setup
- [ ] **Error Tracking**: Configure Sentry or similar
- [ ] **Analytics**: Set up Google Analytics
- [ ] **Uptime Monitoring**: Configure uptime checks
- [ ] **Performance Monitoring**: Set up Web Vitals tracking

## Rollback Procedure

If deployment fails or issues are found:

### 1. Quick Rollback
```bash
# Rollback to previous deployment via Vercel dashboard
# Or redeploy previous Git commit
vercel --prod --force
```

### 2. Fix and Redeploy
```bash
# 1. Fix the issue locally
git add .
git commit -m "fix: resolve deployment issue"

# 2. Test fix locally
npm run build && npm run test

# 3. Deploy fix
git push origin main
```

## Environment-Specific Configuration

### Development
```bash
# Deploy to preview environment
vercel

# Test with preview URL before production
```

### Staging
```bash
# Deploy to staging branch
git checkout staging
git merge main
git push origin staging

# Vercel deploys staging branch to staging.domain.com
```

### Production
```bash
# Deploy to production
git checkout main
vercel --prod
```

## Troubleshooting

### Common Issues

**Build Failures**
- Check Node.js version compatibility
- Verify package.json scripts
- Check for missing dependencies

**Environment Variables**
- Ensure all required env vars are set in Vercel
- Check variable names match exactly
- Verify sensitive variables are encrypted

**Domain Issues**
- Check DNS settings
- Verify domain ownership
- Wait for DNS propagation (up to 24 hours)

**Performance Issues**
- Optimize images and assets
- Enable compression
- Configure caching headers
- Use CDN for static assets

### Support Resources
- [Vercel Documentation](https://vercel.com/docs)
- [Vercel Discord](https://discord.gg/vercel)
- Check deployment logs in Vercel dashboard

## Best Practices

### 1. Automated Deployments
- Set up GitHub Actions for CI/CD
- Use branch protection rules
- Require passing checks before merge

### 2. Environment Management
- Use different environments for dev/staging/prod
- Keep environment variables in secure management
- Document all required environment variables

### 3. Monitoring
- Set up alerts for deployment failures
- Monitor performance metrics
- Track error rates and user feedback

### 4. Security
- Regular security audits
- Keep dependencies updated
- Use HTTPS everywhere
- Configure security headers