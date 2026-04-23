from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache, cache_page
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings as django_settings
from functools import wraps
import json
import random
import string
from datetime import date
from .models import Profile, Course, Opportunity, Application, SavedOpportunity, SubAdmin, ChatMessage, PasswordResetOTP


# ── Quotes (module-level so not rebuilt every request) ──────────────────────
QUOTES = [
    {"text": "The secret of getting ahead is getting started.", "author": "Mark Twain"},
    {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "Your time is limited, don't waste it living someone else's life.", "author": "Steve Jobs"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
    {"text": "Opportunities don't happen. You create them.", "author": "Chris Grosser"},
    {"text": "Hard work beats talent when talent doesn't work hard.", "author": "Tim Notke"},
    {"text": "Dream big and dare to fail.", "author": "Norman Vaughan"},
    {"text": "You don't have to be great to start, but you have to start to be great.", "author": "Zig Ziglar"},
    {"text": "Act as if what you do makes a difference. It does.", "author": "William James"},
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
    {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
    {"text": "Push yourself, because no one else is going to do it for you.", "author": "Unknown"},
    {"text": "Great things never come from comfort zones.", "author": "Unknown"},
    {"text": "You miss 100% of the shots you don't take.", "author": "Wayne Gretzky"},
]


def subadmin_required(perm=None):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            try:
                sa = request.user.sub_admin
                if not sa.is_active:
                    messages.error(request, 'Your sub-admin access has been revoked.')
                    return redirect('dashboard')
                if perm and not getattr(sa, perm, False):
                    messages.error(request, 'You do not have permission for this action.')
                    return redirect('subadmin_dashboard')
            except SubAdmin.DoesNotExist:
                messages.error(request, 'Sub-admin access required.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


@never_cache
def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password   = request.POST.get('password', '')
        first_name = request.POST.get('first_name', '').strip()
        form_data  = {'username': username, 'email': email, 'first_name': first_name}

        if not username or not email or not password:
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html', {'form_data': form_data})
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken. Please choose a different one.')
            return render(request, 'register.html', {'form_data': form_data})
        if User.objects.filter(email=email).exists():
            messages.error(request, 'An account with this email already exists.')
            return render(request, 'register.html', {'form_data': form_data})

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name)
        Profile.objects.create(user=user, ai_score=42)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'register.html')


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username or not password:
            messages.error(request, 'Please enter both username and password.')
            return render(request, 'login.html')
        user = authenticate(request, username=username, password=password)
        if user:
            if not user.is_active:
                messages.error(request, 'Your account has been deactivated.')
                return render(request, 'login.html')
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    Profile.objects.filter(pk=profile.pk).update(profile_views=profile.profile_views + 1)
    profile.profile_views += 1

    # Cache trending for 2 minutes
    trending = cache.get('trending_opps')
    if trending is None:
        trending = list(Opportunity.objects.filter(is_trending=True).only(
            'title', 'company', 'type', 'category', 'stipend', 'is_trending'
        )[:6])
        cache.set('trending_opps', trending, 120)

    saved_count  = SavedOpportunity.objects.filter(user=request.user).count()
    applications = Application.objects.filter(user=request.user).count()
    quote        = random.Random(date.today().toordinal()).choice(QUOTES)

    return render(request, 'dashboard.html', {
        'profile': profile,
        'trending': trending,
        'saved_count': saved_count,
        'applications': applications,
        'quote': quote,
    })


@login_required
def discover(request):
    query       = request.GET.get('q', '').strip()
    type_filter = request.GET.get('type', '').strip()
    opps = Opportunity.objects.only('title', 'company', 'type', 'category', 'stipend', 'is_trending', 'deadline')
    if query:
        opps = opps.filter(Q(title__icontains=query) | Q(company__icontains=query) | Q(category__icontains=query))
    if type_filter:
        opps = opps.filter(type=type_filter)

    # Cache courses list for 5 minutes
    courses = cache.get('courses_list')
    if courses is None:
        courses = list(Course.objects.only('title', 'category', 'duration', 'is_premium', 'thumbnail')[:6])
        cache.set('courses_list', courses, 300)

    return render(request, 'discover.html', {
        'opportunities': opps,
        'courses': courses,
        'query': query,
        'type_filter': type_filter,
    })


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name  = request.POST.get('last_name',  request.user.last_name)
        request.user.email      = request.POST.get('email',      request.user.email)
        request.user.save(update_fields=['first_name', 'last_name', 'email'])

        profile.bio    = request.POST.get('bio',    profile.bio)
        profile.skills = request.POST.get('skills', profile.skills)
        update_fields  = ['bio', 'skills']
        if 'avatar' in request.FILES:
            try:
                profile.avatar = request.FILES['avatar']
                update_fields.append('avatar')
            except Exception:
                messages.warning(request, 'Profile updated but avatar upload failed. Please try again.')
        profile.save(update_fields=update_fields)
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')

    applications = Application.objects.filter(user=request.user).select_related('opportunity').only(
        'status', 'applied_at', 'opportunity__title', 'opportunity__company'
    )
    steps = [
        ('first_name', 'Add your first name',   bool(request.user.first_name)),
        ('last_name',  'Add your last name',     bool(request.user.last_name)),
        ('email',      'Add your email',         bool(request.user.email)),
        ('avatar',     'Upload a profile photo', bool(profile.avatar)),
        ('bio',        'Write a bio',            bool(profile.bio)),
        ('skills',     'Add your skills',        bool(profile.skills)),
    ]
    completed      = sum(1 for _, _, done in steps if done)
    completion_pct = int((completed / len(steps)) * 100)

    return render(request, 'profile.html', {
        'profile': profile,
        'applications': applications,
        'steps': steps,
        'completion_pct': completion_pct,
        'completed': completed,
        'total_steps': len(steps),
    })


@login_required
def ai_tools(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    skills_list = [s.strip() for s in profile.skills.split(',') if s.strip()] if profile.skills else []
    apps_count  = Application.objects.filter(user=request.user).count()

    score = 0
    breakdown = []
    for label, pts, cond in [
        ('First Name',    10, bool(request.user.first_name)),
        ('Last Name',     10, bool(request.user.last_name)),
        ('Email',         10, bool(request.user.email)),
        ('Profile Photo', 15, bool(profile.avatar)),
        ('Bio',           15, bool(profile.bio)),
    ]:
        if cond: score += pts
        breakdown.append({'label': label, 'pts': pts, 'done': cond})

    skill_pts = min(len(skills_list) * 5, 20)
    score += skill_pts
    breakdown.append({'label': f'Skills ({len(skills_list)} added)', 'pts': 20, 'done': skill_pts == 20})

    app_pts = min(apps_count * 5, 20)
    score += app_pts
    breakdown.append({'label': f'Applications ({apps_count} submitted)', 'pts': 20, 'done': app_pts == 20})

    score = min(score, 100)
    if profile.ai_score != score:
        Profile.objects.filter(pk=profile.pk).update(ai_score=score)
        profile.ai_score = score

    tips = []
    if not profile.bio:        tips.append("Add a bio to increase profile visibility by 40%.")
    if len(skills_list) < 4:   tips.append(f"Add {4 - len(skills_list)} more skill(s) to earn full skill points.")
    if not profile.avatar:     tips.append("Upload a profile photo to boost engagement.")
    if not request.user.first_name or not request.user.last_name:
        tips.append("Complete your full name to look more professional.")
    if apps_count < 4:
        tips.append(f"Apply to {4 - apps_count} more opportunit{'y' if 4 - apps_count == 1 else 'ies'} to earn full application points.")

    steps      = [bool(request.user.first_name), bool(request.user.last_name), bool(request.user.email), bool(profile.avatar), bool(profile.bio), bool(profile.skills)]
    profile_pct = int((sum(steps) / len(steps)) * 100)

    return render(request, 'ai_tools.html', {
        'profile': profile, 'tips': tips, 'skills': skills_list,
        'breakdown': breakdown, 'profile_pct': profile_pct, 'apps_count': apps_count,
    })


@login_required
def apply_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity.objects.only('pk', 'title'), pk=pk)
    _, created = Application.objects.get_or_create(user=request.user, opportunity=opportunity)
    if created:
        messages.success(request, f'Applied to {opportunity.title} successfully!')
    else:
        messages.info(request, f'You already applied to {opportunity.title}.')
    return redirect('discover')


@login_required
def save_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity.objects.only('pk', 'title'), pk=pk)
    obj, created = SavedOpportunity.objects.get_or_create(user=request.user, opportunity=opportunity)
    if not created:
        obj.delete()
        messages.info(request, 'Opportunity removed from saved.')
    else:
        messages.success(request, 'Opportunity saved!')
    return redirect('discover')


@login_required
def saved_opportunities(request):
    saved = SavedOpportunity.objects.filter(user=request.user).select_related('opportunity').order_by('-saved_at')
    return render(request, 'saved.html', {'saved': saved})


# ── Sub-Admin Views ──────────────────────────────────────────────────────────

@subadmin_required()
def subadmin_dashboard(request):
    stats = {
        'users':        User.objects.count(),
        'opportunities': Opportunity.objects.count(),
        'courses':      Course.objects.count(),
        'applications': Application.objects.count(),
    }
    try:
        sa = request.user.sub_admin
    except SubAdmin.DoesNotExist:
        sa = None
    return render(request, 'subadmin/dashboard.html', {'stats': stats, 'sa': sa})


@subadmin_required('can_manage_users')
def subadmin_users(request):
    users = User.objects.select_related('profile').order_by('-date_joined')
    return render(request, 'subadmin/users.html', {'users': users})


@subadmin_required('can_manage_users')
def subadmin_toggle_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user and not user.is_superuser:
        user.is_active = not user.is_active
        user.save(update_fields=['is_active'])
        messages.success(request, f"User '{user.username}' {'activated' if user.is_active else 'deactivated'}.")
    return redirect('subadmin_users')


@subadmin_required('can_manage_opportunities')
def subadmin_opportunities(request):
    opportunities = Opportunity.objects.order_by('-created_at')
    return render(request, 'subadmin/opportunities.html', {'opportunities': opportunities})


@subadmin_required('can_manage_opportunities')
def subadmin_delete_opportunity(request, pk):
    get_object_or_404(Opportunity, pk=pk).delete()
    messages.success(request, 'Opportunity deleted.')
    return redirect('subadmin_opportunities')


@subadmin_required('can_manage_courses')
def subadmin_courses(request):
    courses = Course.objects.order_by('-created_at')
    return render(request, 'subadmin/courses.html', {'courses': courses})


@subadmin_required('can_manage_courses')
def subadmin_add_course(request):
    if request.method == 'POST':
        course = Course(
            title=request.POST['title'],
            description=request.POST['description'],
            category=request.POST['category'],
            duration=request.POST['duration'],
            is_premium=bool(request.POST.get('is_premium')),
        )
        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']
        if 'video' in request.FILES:
            course.video = request.FILES['video']
        course.save()
        messages.success(request, f'Course "{course.title}" added successfully.')
        return redirect('subadmin_courses')
    return render(request, 'subadmin/course_form.html', {'action': 'Add'})


@subadmin_required('can_manage_courses')
def subadmin_edit_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        course.title      = request.POST['title']
        course.description = request.POST['description']
        course.category   = request.POST['category']
        course.duration   = request.POST['duration']
        course.is_premium = bool(request.POST.get('is_premium'))
        update_fields = ['title', 'description', 'category', 'duration', 'is_premium']
        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']
            update_fields.append('thumbnail')
        if 'video' in request.FILES:
            course.video = request.FILES['video']
            update_fields.append('video')
        course.save(update_fields=update_fields)
        messages.success(request, f'Course "{course.title}" updated.')
        return redirect('subadmin_courses')
    return render(request, 'subadmin/course_form.html', {'action': 'Edit', 'course': course})


@subadmin_required('can_manage_courses')
def subadmin_delete_course(request, pk):
    get_object_or_404(Course, pk=pk).delete()
    messages.success(request, 'Course deleted.')
    return redirect('subadmin_courses')


@login_required
def subadmin_manage(request):
    if not request.user.is_superuser:
        messages.error(request, 'Superuser access required.')
        return redirect('dashboard')
    subadmins     = SubAdmin.objects.select_related('user', 'assigned_by').order_by('-created_at')
    regular_users = User.objects.filter(sub_admin__isnull=True, is_superuser=False).only('pk', 'username').order_by('username')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            user = get_object_or_404(User, pk=request.POST.get('user_id'))
            SubAdmin.objects.create(
                user=user, role=request.POST.get('role'),
                can_manage_users=bool(request.POST.get('can_manage_users')),
                can_manage_opportunities=bool(request.POST.get('can_manage_opportunities')),
                can_manage_courses=bool(request.POST.get('can_manage_courses')),
                can_manage_applications=bool(request.POST.get('can_manage_applications')),
                assigned_by=request.user,
            )
            messages.success(request, f"Sub-admin '{user.username}' created.")
        elif action in ('revoke', 'delete'):
            sa = get_object_or_404(SubAdmin, pk=request.POST.get('sa_id'))
            if action == 'revoke':
                sa.is_active = not sa.is_active
                sa.save(update_fields=['is_active'])
                messages.success(request, f"Sub-admin '{sa.user.username}' {'activated' if sa.is_active else 'deactivated'}.")
            else:
                sa.delete()
                messages.success(request, 'Sub-admin removed.')
        return redirect('subadmin_manage')
    return render(request, 'subadmin/manage.html', {'subadmins': subadmins, 'regular_users': regular_users})


# ── Chatbot ──────────────────────────────────────────────────────────────────

def _bot_reply(user, text):
    t = text.lower().strip()

    if any(w in t for w in ['hello', 'hi', 'hey', 'hii', 'helo', 'sup', 'yo']):
        return f"Hey {user.first_name or user.username}! 👋 I'm IXOVA Assistant. Ask me about opportunities, courses, your applications, or your profile."

    if any(w in t for w in ['help', 'what can you do', 'commands', 'options', 'menu']):
        return ("Here's what I can help you with:\n"
                "• **Opportunities** — find internships, freelance & gigs\n"
                "• **Courses** — browse learning resources\n"
                "• **My applications** — check your application status\n"
                "• **My profile** — view your AI score & stats\n"
                "• **Trending** — see what's hot right now\nJust ask naturally! 😊")

    if any(w in t for w in ['opportunit', 'internship', 'freelance', 'gig', 'job', 'work', 'opening']):
        type_map    = {'internship': 'internship', 'freelance': 'freelance', 'gig': 'gig'}
        filter_type = next((v for k, v in type_map.items() if k in t), None)
        qs = Opportunity.objects.only('title', 'company', 'stipend', 'is_trending')
        if filter_type: qs = qs.filter(type=filter_type)
        qs = qs.order_by('-is_trending', '-created_at')[:5]
        if not qs.exists(): return "No opportunities found right now. Check back soon! 🔍"
        lines = [f"Here are some {'**' + filter_type + '**' if filter_type else ''} opportunities:\n"]
        for o in qs:
            lines.append(f"• **{o.title}** at {o.company}{' · 💰 ' + o.stipend if o.stipend else ''}{' 🔥' if o.is_trending else ''}")
        lines.append("\nGo to [Discover](/discover/) to apply!")
        return "\n".join(lines)

    if any(w in t for w in ['course', 'learn', 'skill', 'study', 'training', 'tutorial']):
        cat_map    = {'tech': 'tech', 'technology': 'tech', 'business': 'business', 'freelanc': 'freelancing'}
        filter_cat = next((v for k, v in cat_map.items() if k in t), None)
        qs = Course.objects.only('title', 'category', 'duration', 'is_premium')
        if filter_cat: qs = qs.filter(category=filter_cat)
        qs = qs.order_by('is_premium', '-created_at')[:5]
        if not qs.exists(): return "No courses available right now. Stay tuned! 📚"
        lines = ["Here are some courses you can explore:\n"]
        for c in qs:
            lines.append(f"• **{c.title}** ({c.get_category_display()}) · {c.duration} · {'⭐ Premium' if c.is_premium else '✅ Free'}")
        lines.append("\nHead to [Discover](/discover/) to view all courses!")
        return "\n".join(lines)

    if any(w in t for w in ['my application', 'applied', 'application status', 'application']):
        apps = Application.objects.filter(user=user).select_related('opportunity').only(
            'status', 'applied_at', 'opportunity__title', 'opportunity__company'
        ).order_by('-applied_at')[:5]
        if not apps.exists(): return "You haven't applied to anything yet. Visit [Discover](/discover/) to find opportunities! 🚀"
        icons = {'applied': '📤', 'reviewing': '🔍', 'interview': '🗓️', 'accepted': '✅', 'rejected': '❌'}
        lines = ["Here are your recent applications:\n"]
        for a in apps:
            lines.append(f"• **{a.opportunity.title}** at {a.opportunity.company} — {icons.get(a.status,'📋')} {a.get_status_display()}")
        return "\n".join(lines)

    if any(w in t for w in ['saved', 'bookmark', 'wishlist', 'favourite', 'favorite']):
        saved = SavedOpportunity.objects.filter(user=user).select_related('opportunity').only('opportunity__title', 'opportunity__company')[:5]
        if not saved.exists(): return "You haven't saved any opportunities yet. Browse [Discover](/discover/) and save ones you like! 🔖"
        lines = ["Your saved opportunities:\n"] + [f"• **{s.opportunity.title}** at {s.opportunity.company}" for s in saved]
        lines.append("\nView all at [Saved](/saved/)")
        return "\n".join(lines)

    if any(w in t for w in ['profile', 'ai score', 'score', 'my score', 'bio', 'skills', 'avatar']):
        try:
            p = user.profile
            tips = [x for x in [
                "add a bio" if not p.bio else None,
                "add your skills" if not p.skills else None,
                "upload a profile photo" if not p.avatar else None,
            ] if x]
            msg = f"Your AI Score is **{p.ai_score}/100**. "
            if p.ai_score >= 80:   msg += "Excellent! Your profile is highly attractive. 🌟"
            elif p.ai_score >= 50: msg += f"Good progress! To improve, {', '.join(tips)}. 💪"
            else:                  msg += f"Let's boost it! Try: {', '.join(tips)}. 🚀"
            return msg + "\n\nVisit your [Profile](/profile/) to update it."
        except Profile.DoesNotExist:
            return "I couldn't find your profile. Try visiting [Profile](/profile/) to set it up."

    if any(w in t for w in ['trending', 'popular', 'hot', 'top']):
        qs = Opportunity.objects.filter(is_trending=True).only('title', 'company', 'type', 'stipend')[:5]
        if not qs.exists(): return "No trending opportunities right now. Check [Discover](/discover/) for all listings! 🔥"
        lines = ["🔥 Trending right now:\n"] + [f"• **{o.title}** at {o.company} ({o.get_type_display()}){' · 💰 ' + o.stipend if o.stipend else ''}" for o in qs]
        return "\n".join(lines)

    if any(w in t for w in ['how many', 'count', 'total', 'stats', 'statistics', 'number']):
        return (f"📊 Platform stats:\n"
                f"• **{Opportunity.objects.count()}** opportunities listed\n"
                f"• **{Course.objects.count()}** courses available\n"
                f"• **{User.objects.count()}** members on IXOVA\n"
                f"• **{Application.objects.count()}** total applications submitted")

    nav = {'dashboard': '/dashboard/', 'discover': '/discover/', 'profile': '/profile/',
           'ai tools': '/ai-tools/', 'saved': '/saved/', 'login': '/login/', 'register': '/register/'}
    for key, url in nav.items():
        if key in t:
            return f"Sure! Head over to [{key.title()}]({url}) 👉"

    if any(w in t for w in ['bye', 'goodbye', 'see you', 'thanks', 'thank you', 'thx']):
        return "You're welcome! Good luck on your journey. See you around! 👋😊"

    return ("I'm not sure about that, but I can help you with:\n"
            "• Finding **opportunities** (internships, freelance, gigs)\n"
            "• Browsing **courses**\n"
            "• Checking your **applications** or **profile**\n"
            "• Seeing what's **trending**\n\n"
            "Try asking something like *'show me internships'* or *'what's my AI score?'* 😊")


@login_required
def chat_page(request):
    history = list(ChatMessage.objects.filter(user=request.user).only(
        'message', 'reply', 'created_at'
    ).order_by('-created_at')[:30])
    history.reverse()
    return render(request, 'chat.html', {'history': history})


@login_required
@require_POST
def chat_api(request):
    try:
        data     = json.loads(request.body)
        user_msg = data.get('message', '').strip()
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request'}, status=400)

    if not user_msg:
        return JsonResponse({'error': 'Empty message'}, status=400)
    if len(user_msg) > 500:
        return JsonResponse({'error': 'Message too long'}, status=400)

    reply = _bot_reply(request.user, user_msg)
    ChatMessage.objects.create(user=request.user, message=user_msg, reply=reply)
    return JsonResponse({'reply': reply})


# ── Password Reset via OTP ───────────────────────────────────────────────────

import logging
_log = logging.getLogger(__name__)


@never_cache
def forgot_password(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if not email:
            messages.error(request, 'Please enter your email address.')
            return render(request, 'forgot_password.html')

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            messages.success(request, 'If that email is registered, an OTP has been sent.')
            return render(request, 'forgot_password.html')

        otp = ''.join(random.choices(string.digits, k=6))

        try:
            # Verify email is configured before attempting to send
            if not django_settings.EMAIL_HOST_USER or not django_settings.EMAIL_HOST_PASSWORD:
                _log.error(f'Email not configured: EMAIL_HOST_USER or EMAIL_HOST_PASSWORD missing')
                messages.error(request, 'Email service is not properly configured. Please contact support.')
                return render(request, 'forgot_password.html')
            
            send_mail(
                subject='IXOVA — Your Password Reset OTP',
                message=(
                    f'Hello {user.first_name or user.username},\n\n'
                    f'Your OTP to reset your IXOVA password is:\n\n'
                    f'  {otp}\n\n'
                    f'This code expires in 10 minutes. Do not share it with anyone.\n\n'
                    f'If you did not request this, ignore this email.\n\n'
                    f'— The IXOVA Team'
                ),
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            _log.info(f'OTP email sent successfully to {user.email}')
        except Exception as e:
            _log.error(f'OTP email failed for {email}: {str(e)}')
            messages.error(request, f'Could not send email: {str(e)[:100]}. Please try again later.')
            return render(request, 'forgot_password.html')

        PasswordResetOTP.objects.filter(user=user, is_used=False).update(is_used=True)
        PasswordResetOTP.objects.create(user=user, otp=otp)
        request.session['otp_email'] = user.email
        messages.success(request, f'OTP sent to {user.email}. Check your inbox and spam folder.')
        return redirect('verify_otp')

    return render(request, 'forgot_password.html')


@never_cache
def verify_otp(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    email = request.session.get('otp_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        entered = request.POST.get('otp', '').strip()
        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return redirect('forgot_password')

        otp_obj = PasswordResetOTP.objects.filter(
            user=user, otp=entered, is_used=False
        ).order_by('-created_at').first()

        if not otp_obj or not otp_obj.is_valid():
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'verify_otp.html', {'email': email})

        otp_obj.is_used = True
        otp_obj.save(update_fields=['is_used'])
        request.session['otp_verified_email'] = email
        request.session.pop('otp_email', None)
        return redirect('reset_password')

    return render(request, 'verify_otp.html', {'email': email})


@never_cache
def reset_password(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    email = request.session.get('otp_verified_email')
    if not email:
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if not password1 or not password2:
            messages.error(request, 'Both fields are required.')
            return render(request, 'reset_password.html')
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'reset_password.html')
        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
            return render(request, 'reset_password.html')

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return redirect('forgot_password')

        user.set_password(password1)
        user.save(update_fields=['password'])
        request.session.pop('otp_verified_email', None)
        messages.success(request, 'Password reset successfully! You can now sign in.')
        return redirect('login')

    return render(request, 'reset_password.html')
