# 🎓 Cifix Hub - Student Learning Platform

A comprehensive learning management system designed for young learners with assessment integration, personalized recommendations, and progress tracking.

## ✨ Features

### For Students 👦👧
- **Simple Login**: Just first name + access code
- **Modern Dashboard**: Dark theme with progress tracking and star rewards
- **Weekly Modules**: Interactive lessons with videos and resources
- **Assessment Integration**: Seamless connection to external assessment tools
- **Personalized Recommendations**: AI-generated learning suggestions based on assessment results
- **Gamification**: Star-based reward system (+3 stars per completed module/assessment)

### For Parents 👨‍👩‍👧‍👦
- **Progress Reports**: View child's learning journey with detailed analytics
- **PDF Downloads**: Professional progress reports with assessment results
- **Assessment Insights**: View detailed skill breakdowns and recommendations
- **Star Tracking**: Monitor rewards earned from modules and assessments

### For Admins 🛠️
- **Student Management**: Add students with unique access codes
- **Module Management**: Create weekly lessons with videos and resources
- **Assessment Analytics**: View comprehensive assessment data and recommendations
- **Progress Monitoring**: Track student engagement and completion rates

## 🚀 Tech Stack

- **Backend**: FastAPI with async support and Jinja2 templates
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **UI**: Modern glassmorphism design with Tailwind CSS
- **Auth**: Secure session-based authentication
- **Reports**: WeasyPrint for PDF generation
- **Assessment**: External Streamlit app integration via webhooks
- **Deploy**: Railway and Heroku ready with configuration files

## 🛠️ Setup

### 1. Prerequisites
- Python 3.8+
- PostgreSQL database (or Railway PostgreSQL)

### 2. Installation
```bash
# Clone and enter directory
git clone <repository-url>
cd cifix_hub

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/db
SECRET_KEY=your-super-secret-key-here
ADMIN_PASS=your-admin-password
WEBHOOK_SECRET=assessment-webhook-secret
```

### 4. Database Setup
```bash
# Initialize Alembic
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

### 5. Run Development Server
```bash
# Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000 to see your kid-friendly hub! 🎉

## 📁 Project Structure

```
cifix_hub/
├── app/
│   ├── models/           # SQLAlchemy database models
│   ├── routes/           # FastAPI route handlers
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic (reports, etc.)
│   ├── templates/        # Jinja2 HTML templates
│   ├── static/           # Static files (logo, etc.)
│   ├── config.py         # App configuration
│   ├── deps.py           # Dependencies & auth
│   └── main.py           # FastAPI app entry point
├── alembic/              # Database migrations
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
└── README.md
```

## 🎨 Key Pages

### Student Flow
1. **Landing** (`/`) - Welcome page with login options
2. **Student Login** (`/login`) - Name + access code entry
3. **Dashboard** (`/dashboard`) - Progress overview & quick actions
4. **Module Detail** (`/modules/{id}`) - Individual lesson page
5. **Assessment** (`/assessment/start`) - Redirect to Streamlit app

### Parent Flow
1. **Parent Login** (`/parent`) - Email + child's access code
2. **Progress Report** (`/parent/report`) - Child's learning overview
3. **PDF Download** (`/parent/report.pdf`) - Downloadable report

### Admin Flow
1. **Admin Login** (`/admin`) - Password authentication
2. **Dashboard** (`/admin/dashboard`) - Overview & statistics
3. **Manage Modules** (`/admin/modules`) - Create/edit lessons
4. **Manage Students** (`/admin/students`) - Add students
5. **Export Data** (`/admin/assessments.csv`) - Download CSV

## 🔗 Assessment Integration

The platform seamlessly integrates with external assessment tools:

1. Student clicks "Take Assessment" → Redirects to assessment app with student ID and return URL
2. Assessment completes → Sends results via webhook to `/assessment/webhook`
3. System generates personalized recommendations → Awards +3 stars → Updates dashboard

### Webhook Payload Example:
```json
{
  "student_id": 123,
  "raw_score": 78.5,
  "level": "Explorer",
  "domains": {
    "logic": 15,
    "creativity": 20,
    "math": 18,
    "focus": 25
  }
}
```

## 🚀 Railway Deployment

### 1. Create Railway Project
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and create project
railway login
railway init
```

### 2. Add PostgreSQL Database
- Go to Railway dashboard
- Add PostgreSQL service
- Copy connection URL

### 3. Set Environment Variables
In Railway dashboard → Settings → Variables:
```
DATABASE_URL=<railway-postgres-url>
SECRET_KEY=<generate-long-random-string>
ADMIN_PASS=<choose-strong-password>
WEBHOOK_SECRET=<assessment-webhook-secret>
```

### 4. Deploy
```bash
# Deploy to Railway
railway up
```

Your app will be available at `https://your-app.railway.app` 🎉

## 🎯 Usage Examples

### Create Sample Data (via Admin)

1. **Login as Admin**:
   - Go to `/admin`
   - Enter your admin password

2. **Add a Student**:
   - Go to "Manage Students"
   - Add: Name="Alex", Age=8, Email="parent@example.com", Code="KID001"

3. **Create a Module**:
   - Go to "Manage Modules" 
   - Add: Title="Intro to Python", Week=1, Video URL, Check "Published"

4. **Test Student Flow**:
   - Go to `/login`
   - Enter: Name="Alex", Code="KID001"
   - View dashboard and complete module

5. **Test Parent Flow**:
   - Go to `/parent`
   - Enter: Email="parent@example.com", Code="KID001"
   - Download PDF report

## 🎨 Customization

### Styling
- Edit templates in `app/templates/` for layout changes
- Tailwind classes in templates for styling
- DaisyUI components for consistent UI

### Kid-Friendly Design
- Large buttons with emojis (🚀 Start Learning!)
- Bright colors (blue, green, yellow, purple, pink)
- Rounded corners and shadows
- Star progress system ⭐
- Encouraging messages

### Business Logic
- Modify `app/services/` for report generation
- Update `app/models/` for data structure changes
- Extend `app/routes/` for new features

## 🔒 Security Notes

- Session cookies are HTTP-only
- Admin access via environment password
- Webhook signature verification supported
- Input validation with Pydantic
- No sensitive data in logs/repos

## 📞 Support

For questions or issues:
1. Check this README
2. Review code comments
3. Test with sample data
4. Check Railway deployment logs

---

**Built with ❤️ for young learners** 🌟

*Ready to deploy and start teaching!* 🚀
