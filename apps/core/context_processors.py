from datetime import datetime


def global_ui_context(request):
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 18:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    profile = None
    scripts_count = 24
    words_count = "38k"
    projects_count = 6
    unread_notifications = 2

    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            profile = request.user.profile
            scripts_count = request.user.scripts.count()
            user_words = sum(s.word_count for s in request.user.scripts.all())
            if user_words >= 1000:
                words_count = f"{round(user_words / 1000, 1)}k" if user_words % 1000 != 0 else f"{user_words // 1000}k"
            else:
                words_count = str(user_words)
            projects_count = request.user.projects.count()

    return {
        'APP_NAME': 'ScriptForge AI',
        'APP_ALT_NAME': 'SCRIPTLY AI',
        'APP_TAGLINE': 'Your ideas. Perfectly scripted.',
        'greeting': greeting,
        'user_profile': profile,
        'global_scripts_count': scripts_count,
        'global_words_count': words_count,
        'global_projects_count': projects_count,
        'unread_notifications': unread_notifications,
    }
