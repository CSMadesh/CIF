from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from functools import wraps
import json
from .models import Profile, Course, Opportunity, Application, SavedOpportunity, SubAdmin, ChatMessage


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


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        first_name = request.POST.get('first_name', '')
        form_data = {'username': username, 'email': email, 'first_name': first_name}
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


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, 'Invalid credentials.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def dashboard(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    profile.profile_views += 1
    profile.save()
    trending = Opportunity.objects.filter(is_trending=True)[:6]
    saved_count = SavedOpportunity.objects.filter(user=request.user).count()
    applications = Application.objects.filter(user=request.user).count()

    import random
    from datetime import date
    quotes = [
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
        {"text": "Success usually comes to those who are too busy to be looking for it.", "author": "Henry David Thoreau"},
        {"text": "Don't be afraid to give up the good to go for the great.", "author": "John D. Rockefeller"},
        {"text": "I find that the harder I work, the more luck I seem to have.", "author": "Thomas Jefferson"},
        {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
        {"text": "In the middle of every difficulty lies opportunity.", "author": "Albert Einstein"},
        {"text": "It always seems impossible until it's done.", "author": "Nelson Mandela"},
        {"text": "Push yourself, because no one else is going to do it for you.", "author": "Unknown"},
        {"text": "Great things never come from comfort zones.", "author": "Unknown"},
        {"text": "Wake up with determination. Go to bed with satisfaction.", "author": "Unknown"},
        {"text": "Little things make big days.", "author": "Unknown"},
        {"text": "Dream it. Wish it. Do it.", "author": "Unknown"},
        {"text": "Stay foolish to stay sane.", "author": "Maxime Lagacé"},
        {"text": "What you get by achieving your goals is not as important as what you become.", "author": "Zig Ziglar"},
        {"text": "You are never too old to set another goal or to dream a new dream.", "author": "C.S. Lewis"},
        {"text": "Strive not to be a success, but rather to be of value.", "author": "Albert Einstein"},
        {"text": "Two roads diverged in a wood, and I took the one less traveled by.", "author": "Robert Frost"},
        {"text": "I attribute my success to this: I never gave or took any excuse.", "author": "Florence Nightingale"},
        {"text": "You miss 100% of the shots you don't take.", "author": "Wayne Gretzky"},
    ]
    rng = random.Random(date.today().toordinal())
    quote = rng.choice(quotes)

    context = {
        'profile': profile,
        'trending': trending,
        'saved_count': saved_count,
        'applications': applications,
        'quote': quote,
    }
    return render(request, 'dashboard.html', context)


@login_required
def discover(request):
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    opportunities = Opportunity.objects.all()
    if query:
        opportunities = opportunities.filter(Q(title__icontains=query) | Q(company__icontains=query) | Q(category__icontains=query))
    if type_filter:
        opportunities = opportunities.filter(type=type_filter)
    courses = Course.objects.all()[:6]
    return render(request, 'discover.html', {'opportunities': opportunities, 'courses': courses, 'query': query, 'type_filter': type_filter})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        request.user.email = request.POST.get('email', request.user.email)
        request.user.save()
        profile.bio = request.POST.get('bio', profile.bio)
        profile.skills = request.POST.get('skills', profile.skills)
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    applications = Application.objects.filter(user=request.user).select_related('opportunity')

    # ── Profile completion ──
    steps = [
        ('first_name',  'Add your first name',    bool(request.user.first_name)),
        ('last_name',   'Add your last name',      bool(request.user.last_name)),
        ('email',       'Add your email',          bool(request.user.email)),
        ('avatar',      'Upload a profile photo',  bool(profile.avatar)),
        ('bio',         'Write a bio',             bool(profile.bio)),
        ('skills',      'Add your skills',         bool(profile.skills)),
    ]
    completed = sum(1 for _, _, done in steps if done)
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

    # ── Calculate real AI score ──────────────────────────────
    score = 0
    breakdown = []

    if request.user.first_name:
        score += 10
        breakdown.append({'label': 'First Name', 'pts': 10, 'done': True})
    else:
        breakdown.append({'label': 'First Name', 'pts': 10, 'done': False})

    if request.user.last_name:
        score += 10
        breakdown.append({'label': 'Last Name', 'pts': 10, 'done': True})
    else:
        breakdown.append({'label': 'Last Name', 'pts': 10, 'done': False})

    if request.user.email:
        score += 10
        breakdown.append({'label': 'Email', 'pts': 10, 'done': True})
    else:
        breakdown.append({'label': 'Email', 'pts': 10, 'done': False})

    if profile.avatar:
        score += 15
        breakdown.append({'label': 'Profile Photo', 'pts': 15, 'done': True})
    else:
        breakdown.append({'label': 'Profile Photo', 'pts': 15, 'done': False})

    if profile.bio:
        score += 15
        breakdown.append({'label': 'Bio', 'pts': 15, 'done': True})
    else:
        breakdown.append({'label': 'Bio', 'pts': 15, 'done': False})

    skill_pts = min(len(skills_list) * 5, 20)
    score += skill_pts
    breakdown.append({'label': f'Skills ({len(skills_list)} added)', 'pts': 20, 'done': skill_pts == 20})

    apps_count = Application.objects.filter(user=request.user).count()
    app_pts = min(apps_count * 5, 20)
    score += app_pts
    breakdown.append({'label': f'Applications ({apps_count} submitted)', 'pts': 20, 'done': app_pts == 20})

    score = min(score, 100)

    # Save updated score
    if profile.ai_score != score:
        profile.ai_score = score
        profile.save()

    # ── Tips based on what's missing ────────────────────────
    tips = []
    if not profile.bio:
        tips.append("Add a bio to increase profile visibility by 40%.")
    if len(skills_list) < 4:
        tips.append(f"Add {4 - len(skills_list)} more skill(s) to earn full skill points.")
    if not profile.avatar:
        tips.append("Upload a profile photo to boost engagement.")
    if not request.user.first_name or not request.user.last_name:
        tips.append("Complete your full name to look more professional.")
    if apps_count < 4:
        tips.append(f"Apply to {4 - apps_count} more opportunit{'y' if 4 - apps_count == 1 else 'ies'} to earn full application points.")

    # ── Profile completion % (same logic as profile page) ───
    steps = [
        bool(request.user.first_name),
        bool(request.user.last_name),
        bool(request.user.email),
        bool(profile.avatar),
        bool(profile.bio),
        bool(profile.skills),
    ]
    profile_pct = int((sum(steps) / len(steps)) * 100)

    return render(request, 'ai_tools.html', {
        'profile': profile,
        'tips': tips,
        'skills': skills_list,
        'breakdown': breakdown,
        'profile_pct': profile_pct,
        'apps_count': apps_count,
    })


@login_required
def apply_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    Application.objects.get_or_create(user=request.user, opportunity=opportunity)
    messages.success(request, f'Applied to {opportunity.title} successfully!')
    return redirect('discover')


@login_required
def save_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    obj, created = SavedOpportunity.objects.get_or_create(user=request.user, opportunity=opportunity)
    if not created:
        obj.delete()
        messages.info(request, 'Opportunity removed from saved.')
    else:
        messages.success(request, 'Opportunity saved!')
    return redirect('discover')


@login_required
def saved_opportunities(request):
    saved = SavedOpportunity.objects.filter(user=request.user).select_related('opportunity')
    return render(request, 'saved.html', {'saved': saved})


# ── Sub-Admin Views ──────────────────────────────────────────────────────────

@subadmin_required()
def subadmin_dashboard(request):
    stats = {
        'users': User.objects.count(),
        'opportunities': Opportunity.objects.count(),
        'courses': Course.objects.count(),
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
        user.save()
        messages.success(request, f"User '{user.username}' {'activated' if user.is_active else 'deactivated'}.")
    return redirect('subadmin_users')


@subadmin_required('can_manage_opportunities')
def subadmin_opportunities(request):
    opportunities = Opportunity.objects.order_by('-created_at')
    return render(request, 'subadmin/opportunities.html', {'opportunities': opportunities})


@subadmin_required('can_manage_opportunities')
def subadmin_delete_opportunity(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    opportunity.delete()
    messages.success(request, 'Opportunity deleted.')
    return redirect('subadmin_opportunities')


@subadmin_required('can_manage_courses')
def subadmin_courses(request):
    courses = Course.objects.order_by('-created_at')
    return render(request, 'subadmin/courses.html', {'courses': courses})


@subadmin_required('can_manage_courses')
def subadmin_add_course(request):
    if request.method == 'POST':
        course = Course.objects.create(
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
        course.title = request.POST['title']
        course.description = request.POST['description']
        course.category = request.POST['category']
        course.duration = request.POST['duration']
        course.is_premium = bool(request.POST.get('is_premium'))
        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']
        if 'video' in request.FILES:
            course.video = request.FILES['video']
        course.save()
        messages.success(request, f'Course "{course.title}" updated.')
        return redirect('subadmin_courses')
    return render(request, 'subadmin/course_form.html', {'action': 'Edit', 'course': course})


@subadmin_required('can_manage_courses')
def subadmin_delete_course(request, pk):
    course = get_object_or_404(Course, pk=pk)
    course.delete()
    messages.success(request, 'Course deleted.')
    return redirect('subadmin_courses')


@login_required
def subadmin_manage(request):
    if not request.user.is_superuser:
        messages.error(request, 'Superuser access required.')
        return redirect('dashboard')
    subadmins = SubAdmin.objects.select_related('user', 'assigned_by').order_by('-created_at')
    regular_users = User.objects.filter(sub_admin__isnull=True, is_superuser=False).order_by('username')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'create':
            user_id = request.POST.get('user_id')
            role = request.POST.get('role')
            user = get_object_or_404(User, pk=user_id)
            SubAdmin.objects.create(
                user=user,
                role=role,
                can_manage_users=bool(request.POST.get('can_manage_users')),
                can_manage_opportunities=bool(request.POST.get('can_manage_opportunities')),
                can_manage_courses=bool(request.POST.get('can_manage_courses')),
                can_manage_applications=bool(request.POST.get('can_manage_applications')),
                assigned_by=request.user,
            )
            messages.success(request, f"Sub-admin '{user.username}' created.")
        elif action == 'revoke':
            sa_id = request.POST.get('sa_id')
            sa = get_object_or_404(SubAdmin, pk=sa_id)
            sa.is_active = not sa.is_active
            sa.save()
            messages.success(request, f"Sub-admin '{sa.user.username}' {'activated' if sa.is_active else 'deactivated'}.")
        elif action == 'delete':
            sa_id = request.POST.get('sa_id')
            sa = get_object_or_404(SubAdmin, pk=sa_id)
            sa.delete()
            messages.success(request, 'Sub-admin removed.')
        return redirect('subadmin_manage')
    return render(request, 'subadmin/manage.html', {'subadmins': subadmins, 'regular_users': regular_users})


# ── Chatbot ──────────────────────────────────────────────────────────────────

def _bot_reply(user, text):
    t = text.lower().strip()

    # ── Greetings ──
    if any(w in t for w in ['hello', 'hi', 'hey', 'hii', 'helo', 'sup', 'yo']):
        name = user.first_name or user.username
        return f"Hey {name}! 👋 I'm IXOVA Assistant. Ask me about opportunities, courses, your applications, or your profile."

    # ── Help ──
    if any(w in t for w in ['help', 'what can you do', 'commands', 'options', 'menu']):
        return (
            "Here's what I can help you with:\n"
            "• **Opportunities** — find internships, freelance & gigs\n"
            "• **Courses** — browse learning resources\n"
            "• **My applications** — check your application status\n"
            "• **My profile** — view your AI score & stats\n"
            "• **Trending** — see what's hot right now\n"
            "Just ask naturally! 😊"
        )

    # ── Opportunities ──
    if any(w in t for w in ['opportunit', 'internship', 'freelance', 'gig', 'job', 'work', 'opening']):
        type_map = {'internship': 'internship', 'freelance': 'freelance', 'gig': 'gig'}
        filter_type = next((v for k, v in type_map.items() if k in t), None)
        qs = Opportunity.objects.all()
        if filter_type:
            qs = qs.filter(type=filter_type)
        qs = qs.order_by('-is_trending', '-created_at')[:5]
        if not qs.exists():
            return "No opportunities found right now. Check back soon! 🔍"
        lines = [f"Here are some {'**' + filter_type + '**' if filter_type else ''} opportunities for you:\n"]
        for o in qs:
            stipend = f" · 💰 {o.stipend}" if o.stipend else ""
            trending = " 🔥" if o.is_trending else ""
            lines.append(f"• **{o.title}** at {o.company}{stipend}{trending}")
        lines.append("\nGo to [Discover](/discover/) to apply!")
        return "\n".join(lines)

    # ── Courses ──
    if any(w in t for w in ['course', 'learn', 'skill', 'study', 'training', 'tutorial']):
        cat_map = {'tech': 'tech', 'technology': 'tech', 'business': 'business', 'freelanc': 'freelancing'}
        filter_cat = next((v for k, v in cat_map.items() if k in t), None)
        qs = Course.objects.all()
        if filter_cat:
            qs = qs.filter(category=filter_cat)
        qs = qs.order_by('is_premium', '-created_at')[:5]
        if not qs.exists():
            return "No courses available right now. Stay tuned! 📚"
        lines = ["Here are some courses you can explore:\n"]
        for c in qs:
            tag = "⭐ Premium" if c.is_premium else "✅ Free"
            lines.append(f"• **{c.title}** ({c.get_category_display()}) · {c.duration} · {tag}")
        lines.append("\nHead to [Discover](/discover/) to view all courses!")
        return "\n".join(lines)

    # ── My Applications ──
    if any(w in t for w in ['my application', 'applied', 'application status', 'my status', 'application']):
        apps = Application.objects.filter(user=user).select_related('opportunity').order_by('-applied_at')[:5]
        if not apps.exists():
            return "You haven't applied to anything yet. Visit [Discover](/discover/) to find opportunities! 🚀"
        lines = ["Here are your recent applications:\n"]
        status_icons = {'applied': '📤', 'reviewing': '🔍', 'interview': '🗓️', 'accepted': '✅', 'rejected': '❌'}
        for a in apps:
            icon = status_icons.get(a.status, '📋')
            lines.append(f"• **{a.opportunity.title}** at {a.opportunity.company} — {icon} {a.get_status_display()}")
        return "\n".join(lines)

    # ── Saved ──
    if any(w in t for w in ['saved', 'bookmark', 'wishlist', 'favourite', 'favorite']):
        saved = SavedOpportunity.objects.filter(user=user).select_related('opportunity')[:5]
        if not saved.exists():
            return "You haven't saved any opportunities yet. Browse [Discover](/discover/) and save ones you like! 🔖"
        lines = ["Your saved opportunities:\n"]
        for s in saved:
            lines.append(f"• **{s.opportunity.title}** at {s.opportunity.company}")
        lines.append("\nView all at [Saved](/saved/)")
        return "\n".join(lines)

    # ── Profile / AI Score ──
    if any(w in t for w in ['profile', 'ai score', 'score', 'my score', 'bio', 'skills', 'avatar']):
        try:
            profile = user.profile
            score = profile.ai_score
            tips = []
            if not profile.bio:
                tips.append("add a bio")
            if not profile.skills:
                tips.append("add your skills")
            if not profile.avatar:
                tips.append("upload a profile photo")
            tip_str = ", ".join(tips)
            msg = f"Your AI Score is **{score}/100**. "
            if score >= 80:
                msg += "Excellent! Your profile is highly attractive. 🌟"
            elif score >= 50:
                msg += f"Good progress! To improve, {tip_str}. 💪"
            else:
                msg += f"Let's boost it! Try: {tip_str}. 🚀"
            msg += "\n\nVisit your [Profile](/profile/) to update it."
            return msg
        except Profile.DoesNotExist:
            return "I couldn't find your profile. Try visiting [Profile](/profile/) to set it up."

    # ── Trending ──
    if any(w in t for w in ['trending', 'popular', 'hot', 'top']):
        qs = Opportunity.objects.filter(is_trending=True)[:5]
        if not qs.exists():
            return "No trending opportunities right now. Check [Discover](/discover/) for all listings! 🔥"
        lines = ["🔥 Trending right now:\n"]
        for o in qs:
            stipend = f" · 💰 {o.stipend}" if o.stipend else ""
            lines.append(f"• **{o.title}** at {o.company} ({o.get_type_display()}){stipend}")
        return "\n".join(lines)

    # ── Stats ──
    if any(w in t for w in ['how many', 'count', 'total', 'stats', 'statistics', 'number']):
        return (
            f"📊 Platform stats:\n"
            f"• **{Opportunity.objects.count()}** opportunities listed\n"
            f"• **{Course.objects.count()}** courses available\n"
            f"• **{User.objects.count()}** members on IXOVA\n"
            f"• **{Application.objects.count()}** total applications submitted"
        )

    # ── Navigation ──
    nav = {
        'dashboard': '/dashboard/', 'discover': '/discover/',
        'profile': '/profile/', 'ai tools': '/ai-tools/',
        'saved': '/saved/', 'login': '/login/', 'register': '/register/',
    }
    for key, url in nav.items():
        if key in t:
            return f"Sure! Head over to [{key.title()}]({url}) 👉"

    # ── Goodbye ──
    if any(w in t for w in ['bye', 'goodbye', 'see you', 'thanks', 'thank you', 'thx']):
        return "You're welcome! Good luck on your journey. See you around! 👋😊"

    # ── Fallback ──
    return (
        "I'm not sure about that, but I can help you with:\n"
        "• Finding **opportunities** (internships, freelance, gigs)\n"
        "• Browsing **courses**\n"
        "• Checking your **applications** or **profile**\n"
        "• Seeing what's **trending**\n\n"
        "Try asking something like *'show me internships'* or *'what's my AI score?'* 😊"
    )


@login_required
def chat_page(request):
    history = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:30]
    history = list(reversed(history))
    return render(request, 'chat.html', {'history': history})


@login_required
@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body)
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
