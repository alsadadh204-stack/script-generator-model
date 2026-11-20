from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ScriptTemplate


@login_required
def templates_list_view(request):
    """Template Library page"""
    category = request.GET.get('category', 'all').lower()
    templates = ScriptTemplate.objects.all()

    if category != 'all':
        templates = templates.filter(category=category)

    context = {
        'templates': templates,
        'active_category': category,
    }
    return render(request, 'pages/templates.html', context)
