import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ixova.settings')
django.setup()

from core.models import Opportunity, Course

opportunities = [
    {"title": "Frontend Developer Intern", "company": "TechNova", "description": "Build modern React UIs for our SaaS product. Work with senior engineers.", "type": "internship", "category": "Web Dev", "stipend": "₹15,000/mo", "is_trending": True},
    {"title": "Python Backend Intern", "company": "DataFlow", "description": "Develop REST APIs using Django and FastAPI. Real-world project experience.", "type": "internship", "category": "Backend", "stipend": "₹12,000/mo", "is_trending": True},
    {"title": "UI/UX Design Freelance", "company": "PixelCraft", "description": "Design mobile app screens and web dashboards for startup clients.", "type": "freelance", "category": "Design", "stipend": "₹5,000–20,000", "is_trending": True},
    {"title": "Content Writing Gig", "company": "BlogHub", "description": "Write SEO-optimized articles on tech, business, and lifestyle topics.", "type": "gig", "category": "Writing", "stipend": "₹500/article", "is_trending": False},
    {"title": "Social Media Manager", "company": "BrandBoost", "description": "Manage Instagram and LinkedIn for growing D2C brands.", "type": "freelance", "category": "Marketing", "stipend": "₹8,000/mo", "is_trending": True},
    {"title": "Data Analysis Intern", "company": "InsightLab", "description": "Analyze datasets using Python and create visual reports with Tableau.", "type": "internship", "category": "Data Science", "stipend": "₹10,000/mo", "is_trending": False},
    {"title": "Mobile App Developer", "company": "AppWorks", "description": "Build Flutter-based cross-platform apps for clients.", "type": "freelance", "category": "Mobile Dev", "stipend": "₹25,000–50,000", "is_trending": True},
    {"title": "Video Editing Gig", "company": "CreativeHub", "description": "Edit YouTube videos and reels for content creators.", "type": "gig", "category": "Creative", "stipend": "₹1,000–3,000/video", "is_trending": False},
]

courses = [
    {"title": "Python for Beginners", "description": "Learn Python from scratch with hands-on projects and real-world examples.", "category": "tech", "duration": "6 weeks", "is_premium": False},
    {"title": "Freelancing Masterclass", "description": "Start and scale your freelance career. Find clients, set rates, deliver work.", "category": "freelancing", "duration": "4 weeks", "is_premium": False},
    {"title": "UI/UX Design Fundamentals", "description": "Master Figma and design principles to create stunning user interfaces.", "category": "tech", "duration": "5 weeks", "is_premium": True},
    {"title": "Digital Marketing Bootcamp", "description": "SEO, social media, email marketing — everything to grow a brand online.", "category": "business", "duration": "8 weeks", "is_premium": True},
    {"title": "React.js Complete Guide", "description": "Build modern web apps with React, hooks, and state management.", "category": "tech", "duration": "10 weeks", "is_premium": True},
    {"title": "Business Communication", "description": "Write emails, pitch ideas, and communicate professionally in any workplace.", "category": "business", "duration": "3 weeks", "is_premium": False},
]

for o in opportunities:
    Opportunity.objects.get_or_create(title=o['title'], company=o['company'], defaults=o)

for c in courses:
    Course.objects.get_or_create(title=c['title'], defaults=c)

print("✅ Sample data seeded successfully!")
