# MyWork Framework - Example Projects

## 🚀 **Complete Working Examples**

Learn by exploring real, working applications built with the MyWork framework. Each example includes full source code, documentation, and step-by-step build instructions.

---

## 📋 **Example Projects**

### 🔧 **CLI Tools**

| Project | Description | Complexity | Tutorial |
|---------|-------------|------------|----------|
| [**Task Manager CLI**](cli-task-manager/) | Personal todo management from terminal | Beginner | [Tutorial 1](../docs/tutorials/01-first-project.md) |
| [**File Organizer**](cli-file-organizer/) | Batch organize files by type/date | Beginner | - |
| [**Log Analyzer**](cli-log-analyzer/) | Parse and analyze server logs | Intermediate | - |

### 🌐 **Web Applications**

| Project | Description | Complexity | Tutorial |
|---------|-------------|------------|----------|
| [**Todo Web App**](web-todo-app/) | Task management with auth & categories | Intermediate | [Tutorial 2](../docs/tutorials/02-gsd-basics.md) |
| [**Blog Platform**](web-blog-platform/) | Multi-user blogging with admin panel | Advanced | [Tutorial 3](../docs/tutorials/03-autocoder-basics.md) |
| [**Analytics Dashboard**](web-analytics-dashboard/) | Real-time data visualization | Advanced | [Tutorial 5](../docs/tutorials/05-fullstack-mastery.md) |

### 🔗 **API Services**

| Project | Description | Complexity | Tutorial |
|---------|-------------|------------|----------|
| [**REST API**](api-task-service/) | Task management REST API | Intermediate | - |
| [**GraphQL API**](api-graphql-blog/) | Blog API with GraphQL | Advanced | - |
| [**Webhook Processor**](api-webhook-processor/) | Process GitHub/Stripe webhooks | Intermediate | [Tutorial 4](../docs/tutorials/04-n8n-workflows.md) |

### 🤖 **Automation & AI**

| Project | Description | Complexity | Tutorial |
|---------|-------------|------------|----------|
| [**Email Automation**](automation-email-workflows/) | n8n + AI for smart email responses | Intermediate | [Tutorial 4](../docs/tutorials/04-n8n-workflows.md) |
| [**Content Generator**](automation-content-ai/) | AI-powered blog post generation | Advanced | - |
| [**Data Pipeline**](automation-data-pipeline/) | ETL with n8n + Python | Advanced | - |

### 🏢 **Full-Stack Applications**

| Project | Description | Complexity | Tutorial |
|---------|-------------|------------|----------|
| [**SaaS Starter**](fullstack-saas-starter/) | Complete SaaS template with billing | Expert | [Tutorial 5](../docs/tutorials/05-fullstack-mastery.md) |
| [**E-commerce MVP**](fullstack-ecommerce/) | Online store with payments | Expert | - |

---

## 🎯 **Quick Start Any Example**

### **1. Choose and copy an example:**
```bash
cd /Users/dansidanutz/Desktop/MyWork
cp -r examples/web-todo-app projects/my-todo-app
cd projects/my-todo-app
```

### **2. Follow the example's README:**
```bash
cat README.md  # Specific setup instructions
```

### **3. Run the example:**
```bash
# Most examples support:
npm start        # or
python main.py   # or
./start.sh
```

---

## 📚 **Learning Path by Examples**

### **🚀 Beginner Path** *(Start here)*
1. **CLI Task Manager** - Learn GSD basics
2. **Todo Web App** - Understand full-stack development
3. **Webhook Processor** - Experience automation

### **⚡ Intermediate Path** *(After beginner)*
1. **Blog Platform** - Complex data relationships
2. **Analytics Dashboard** - Real-time features
3. **Email Automation** - AI + automation

### **🏆 Advanced Path** *(Ready for production)*
1. **SaaS Starter** - Complete business application
2. **E-commerce MVP** - Payment processing
3. **Data Pipeline** - Enterprise automation

---

## 🔧 **Example Structure**

Each example follows a consistent structure:

```
example-project/
├── README.md                   # Setup and usage instructions
├── .planning/                  # GSD project structure
│   ├── PROJECT.md              # Vision and goals
│   ├── ROADMAP.md              # Development phases
│   ├── STATE.md                # Current status
│   └── phases/                 # Detailed plans and summaries
├── src/ or app/                # Source code
├── tests/                      # Test suite
├── docs/                       # Additional documentation
├── scripts/                    # Helper scripts
├── package.json or requirements.txt  # Dependencies
└── .env.example                # Environment variables template
```

---

## 🎓 **What You'll Learn**

### **From CLI Examples:**
- ✅ Argument parsing and command structure
- ✅ File I/O and data persistence
- ✅ Error handling and user feedback
- ✅ Testing CLI applications
- ✅ Packaging and distribution

### **From Web Examples:**
- ✅ Frontend/backend separation
- ✅ Authentication and authorization
- ✅ Database design and migrations
- ✅ API design and documentation
- ✅ Responsive UI development
- ✅ Testing full-stack applications

### **From API Examples:**
- ✅ RESTful API design
- ✅ GraphQL schema and resolvers
- ✅ Input validation and sanitization
- ✅ Rate limiting and security
- ✅ API documentation with OpenAPI
- ✅ Testing API endpoints

### **From Automation Examples:**
- ✅ n8n workflow design
- ✅ Webhook processing
- ✅ AI integration patterns
- ✅ Error handling in workflows
- ✅ Monitoring and logging
- ✅ Scalable automation architecture

### **From Full-Stack Examples:**
- ✅ Complete application architecture
- ✅ User management and billing
- ✅ Payment processing integration
- ✅ Production deployment
- ✅ Monitoring and analytics
- ✅ Performance optimization

---

## 🛠️ **Customizing Examples**

### **Use examples as templates:**

1. **Copy the structure:**
   ```bash
   cp -r examples/web-todo-app projects/my-custom-app
   ```

2. **Adapt the planning:**
   ```bash
   cd projects/my-custom-app
   # Edit .planning/PROJECT.md with your vision
   # Update .planning/REQUIREMENTS.md with your needs
   ```

3. **Re-run GSD planning:**
   ```bash
   mw gsd plan-phase [phase]  # Re-plan any phase
   mw gsd execute-phase [phase]  # Build your version
   ```

### **Mix and match components:**
- Take auth from one example
- Take UI patterns from another
- Combine API patterns from multiple examples

---

## 🧪 **Testing Examples**

### **All examples include:**
- ✅ **Unit tests** - Test individual functions and components
- ✅ **Integration tests** - Test feature interactions
- ✅ **E2E tests** - Test complete user workflows
- ✅ **Performance tests** - Test under load (where applicable)

### **Run tests:**
```bash
# In any example directory:
npm test           # JavaScript/TypeScript projects
python -m pytest  # Python projects
./test.sh          # Custom test scripts
```

---

## 📈 **Production Deployment**

### **Examples include production configs for:**
- ✅ **Vercel** - Frontend hosting
- ✅ **Railway** - Backend hosting
- ✅ **Neon** - PostgreSQL database
- ✅ **Upstash** - Redis caching
- ✅ **GitHub Actions** - CI/CD pipelines

### **Deploy any example:**
```bash
# Follow example's deployment guide
cat deployment/README.md

# Use included deploy scripts
./deploy.sh production
```

---

## 🤝 **Contributing Examples**

### **Add your own example:**

1. **Create the structure:**
   ```bash
   mkdir examples/my-example
   cp examples/_template/* examples/my-example/
   ```

2. **Build with MyWork:**
   ```bash
   cd examples/my-example
   mw gsd new-project
   # Follow normal development workflow
   ```

3. **Document thoroughly:**
   - Clear README with setup steps
   - Include .env.example
   - Add comprehensive tests
   - Document any gotchas or requirements

4. **Submit PR:**
   ```bash
   git checkout -b add-example-my-project
   git add examples/my-example/
   git commit -m "add: [example-name] example project"
   git push origin add-example-my-project
   ```

---

## 📚 **Additional Resources**

- [**Framework Documentation →**](../docs/) - Complete guides and API reference
- [**Tutorial Series →**](../docs/tutorials/) - Step-by-step learning path
- [**Architecture Overview →**](../docs/architecture/) - Understanding the 3-layer system
- [**GitHub Discussions →**](https://github.com/MyWork-AI/framework/discussions) - Community help

---

*💡 **Pro Tip:** Start with the example closest to what you want to build, then customize it using GSD planning to match your specific requirements.*