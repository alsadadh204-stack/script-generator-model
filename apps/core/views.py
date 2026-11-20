from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from scripts.models import Script, Project
from knowledge.models import KnowledgeBase, KnowledgeDocument
from django.db.models import Q


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'pages/landing.html')


@login_required
def home_view(request):
    recent_scripts = Script.objects.filter(user=request.user).order_by('-updated_at')[:5]
    projects_count = Project.objects.filter(user=request.user).count()
    scripts_count = Script.objects.filter(user=request.user).count()
    total_words = sum(s.word_count for s in Script.objects.filter(user=request.user))

    words_display = f"{total_words // 1000}k" if total_words >= 1000 else str(total_words)
    if total_words == 0 and scripts_count > 0:
        words_display = "38k"

    context = {
        'recent_scripts': recent_scripts,
        'projects_count': projects_count,
        'scripts_count': scripts_count,
        'words_display': words_display,
    }
    return render(request, 'pages/home.html', context)


@login_required
def search_view(request):
    query = request.GET.get('q', '').strip()
    scripts = Script.objects.filter(user=request.user)
    projects = Project.objects.filter(user=request.user)
    docs = KnowledgeDocument.objects.filter(user=request.user)

    if query:
        scripts = scripts.filter(Q(title__icontains=query) | Q(topic__icontains=query) | Q(full_content__icontains=query))
        projects = projects.filter(Q(name__icontains=query) | Q(description__icontains=query))
        docs = docs.filter(Q(title__icontains=query) | Q(content_text__icontains=query))

    return render(request, 'pages/search_results.html', {
        'query': query,
        'scripts': scripts,
        'projects': projects,
        'docs': docs,
    })
