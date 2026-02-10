# Release Workflow

Comprehensive workflow for version management, changelog updates, Git tagging, GitHub releases, and marketplace updates.

## Pre-Release Preparation

### 1. Release Planning
- [ ] **Feature Freeze**: Complete all features for this release
- [ ] **Bug Fixes**: Address critical bugs and issues
- [ ] **Testing**: Complete integration and regression testing
- [ ] **Documentation**: Update user-facing documentation

### 2. Version Strategy
- [ ] **Version Number**: Determine version using semantic versioning (semver)
  - **MAJOR**: Breaking changes
  - **MINOR**: New features, backwards compatible
  - **PATCH**: Bug fixes, backwards compatible
- [ ] **Release Type**: Alpha, Beta, RC (Release Candidate), or Stable

### 3. Quality Assurance
- [ ] **Code Review**: All changes reviewed and approved
- [ ] **Test Coverage**: Minimum coverage threshold met
- [ ] **Performance**: No performance regressions
- [ ] **Security**: Security scan passed

## Release Process

### Step 1: Version Bump

#### Automatic Version Bump (Recommended)
```bash
# Using npm version (for Node.js projects)
npm version patch    # 1.0.0 -> 1.0.1
npm version minor    # 1.0.0 -> 1.1.0
npm version major    # 1.0.0 -> 2.0.0

# Using Python semantic-release
semantic-release version

# Using standard-version
npx standard-version
```

#### Manual Version Bump
```bash
# Update version in package.json, setup.py, etc.
# Update version constants in code
# Commit version bump
git add .
git commit -m "bump: version 1.2.3"
```

### Step 2: Changelog Update

#### Automated Changelog (Recommended)
```bash
# Using conventional-changelog
npx conventional-changelog -p angular -i CHANGELOG.md -s

# Using git-cliff
git-cliff --output CHANGELOG.md

# Using github-changelog-generator
github_changelog_generator
```

#### Manual Changelog Update
```markdown
# Changelog Template
## [1.2.3] - 2024-02-10

### Added
- New user authentication system
- Dashboard analytics widget

### Changed
- Updated API response format
- Improved error handling

### Fixed
- Fixed memory leak in background processing
- Resolved login redirect issue

### Deprecated
- Old authentication endpoints (will be removed in v2.0.0)

### Removed
- Legacy user preferences API

### Security
- Fixed potential XSS vulnerability
```

### Step 3: Git Tagging

#### Create Release Tag
```bash
# Create annotated tag
git tag -a v1.2.3 -m "Release version 1.2.3

Features:
- New authentication system
- Dashboard improvements

Bug fixes:
- Memory leak fix
- Login redirect fix"

# Push tag to remote
git push origin v1.2.3

# Or push all tags
git push origin --tags
```

#### Tag Naming Conventions
- **Stable**: `v1.2.3`, `1.2.3`
- **Pre-release**: `v1.2.3-beta.1`, `v1.2.3-rc.1`
- **Development**: `v1.2.3-dev.20240210`

### Step 4: GitHub Release

#### Using GitHub CLI (Recommended)
```bash
# Install GitHub CLI
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update && sudo apt install gh

# Login
gh auth login

# Create release
gh release create v1.2.3 \
  --title "Version 1.2.3" \
  --notes-file CHANGELOG.md \
  --latest

# Upload release assets
gh release upload v1.2.3 dist/*.zip dist/*.tar.gz
```

#### Using GitHub Web Interface
1. Go to repository → Releases → "Create a new release"
2. Choose tag: Select existing tag or create new one
3. Release title: "Version 1.2.3"
4. Description: Copy relevant section from CHANGELOG.md
5. Upload release assets (binaries, packages, etc.)
6. Check "Set as the latest release" if applicable
7. Click "Publish release"

#### Release Notes Template
```markdown
# Release v1.2.3

## 🚀 What's New
- **Authentication System**: Complete rewrite with JWT support
- **Dashboard Analytics**: Real-time metrics and charts
- **Mobile Responsive**: Improved mobile experience

## 🐛 Bug Fixes
- Fixed memory leak in background processing
- Resolved login redirect issues
- Fixed date picker timezone handling

## ⚠️ Breaking Changes
None in this release.

## 🔧 Technical Changes
- Updated to Node.js 18
- Migrated from MySQL to PostgreSQL
- Improved test coverage to 90%

## 📦 Installation
```bash
npm install mypackage@1.2.3
# or
pip install mypackage==1.2.3
```

## 🙏 Contributors
Thanks to @user1, @user2, and @user3 for their contributions!

**Full Changelog**: https://github.com/owner/repo/compare/v1.2.2...v1.2.3
```

### Step 5: Marketplace Updates

#### NPM Package Release
```bash
# Login to NPM
npm login

# Publish package
npm publish

# Publish with specific tag
npm publish --tag beta
npm publish --tag latest
```

#### Python Package (PyPI) Release
```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI
twine upload dist/*

# Upload to test PyPI first
twine upload --repository testpypi dist/*
```

#### Docker Registry Release
```bash
# Build Docker image
docker build -t myapp:1.2.3 .
docker tag myapp:1.2.3 myapp:latest

# Push to Docker Hub
docker push myapp:1.2.3
docker push myapp:latest

# Push to GitHub Container Registry
docker tag myapp:1.2.3 ghcr.io/owner/myapp:1.2.3
docker push ghcr.io/owner/myapp:1.2.3
```

#### Chrome Extension/Add-on Stores
```bash
# Build extension
npm run build:extension

# Upload to Chrome Web Store via API
# (Requires Web Store API setup)

# Upload to Firefox Add-ons
# (Requires AMO API setup)
```

## Post-Release Actions

### 1. Deployment
- [ ] **Production Deployment**: Deploy to production environment
- [ ] **Health Check**: Verify deployment health and functionality
- [ ] **Rollback Plan**: Have rollback procedure ready
- [ ] **Monitoring**: Monitor for issues in production

### 2. Communication
- [ ] **Release Announcement**: Notify users about the release
- [ ] **Documentation Update**: Update user guides and API docs
- [ ] **Social Media**: Share release on social platforms
- [ ] **Team Notification**: Inform team about successful release

### 3. Feedback Collection
- [ **User Feedback**: Set up channels for user feedback
- [ ] **Issue Tracking**: Monitor for new issues or bugs
- [ ] **Analytics**: Track adoption and usage metrics
- [ ] **Support Preparation**: Prepare support team for questions

## Automated Release Pipeline

### GitHub Actions Workflow
```yaml
name: Release
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build
        run: npm run build
      
      - name: Generate changelog
        run: npx conventional-changelog -p angular -i CHANGELOG.md -s
      
      - name: Create GitHub Release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          body_path: CHANGELOG.md
          draft: false
          prerelease: false
      
      - name: Publish to NPM
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v2
        with:
          push: true
          tags: myapp:${{ github.ref_name }},myapp:latest
```

## Release Checklist Templates

### Major Release Checklist
- [ ] **Breaking Changes**: Document all breaking changes
- [ ] **Migration Guide**: Provide upgrade/migration instructions
- [ ] **Deprecation Notices**: Warn about deprecated features
- [ ] **Performance Testing**: Extensive performance testing
- [ ] **Security Audit**: Complete security review
- [ ] **Beta Testing**: Extended beta testing period
- [ ] **Documentation Overhaul**: Major documentation updates

### Minor Release Checklist
- [ ] **Feature Documentation**: Document new features
- [ ] **API Changes**: Update API documentation
- [ ] **Backward Compatibility**: Ensure backward compatibility
- [ ] **Integration Testing**: Test with existing integrations
- [ ] **Performance Impact**: Measure performance impact

### Patch Release Checklist
- [ ] **Bug Fix Verification**: Verify all bugs are fixed
- [ ] **Regression Testing**: Ensure no new regressions
- [ ] **Hot Fix Process**: Fast-track critical fixes
- [ ] **Quick Deployment**: Rapid deployment process

## Rollback Procedures

### Git-based Rollback
```bash
# Revert to previous version
git revert v1.2.3
git push origin main

# Or reset to previous tag
git reset --hard v1.2.2
git push origin main --force
```

### Package Rollback
```bash
# NPM deprecate
npm deprecate mypackage@1.2.3 "Contains critical bug, use 1.2.2"

# Docker image rollback
docker tag myapp:1.2.2 myapp:latest
docker push myapp:latest
```

### Deployment Rollback
- Use deployment platform's rollback feature
- Monitor metrics during rollback
- Communicate rollback to users
- Document issues for future prevention

## Best Practices

### Release Management
1. **Regular Releases**: Release early and often
2. **Semantic Versioning**: Follow semver strictly
3. **Release Notes**: Write clear, user-focused release notes
4. **Testing**: Comprehensive testing before release
5. **Automation**: Automate repetitive release tasks

### Communication
1. **Advance Notice**: Give users advance notice of major changes
2. **Migration Guides**: Provide clear upgrade instructions
3. **Support Channels**: Have support ready for release day
4. **Feedback Loop**: Collect and act on user feedback
5. **Transparency**: Be transparent about issues and fixes