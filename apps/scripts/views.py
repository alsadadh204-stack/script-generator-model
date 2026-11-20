from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
import json

from .models import Script, ScriptVersion, Project
from knowledge.models import KnowledgeBase
from ai_engine.services import ClaudeService
from .export_service import ScriptExportService


# ---------------- CATEGORIES & WIZARD ----------------

@login_required
def categories_view(request):
    """Page 2: Category and script type picker"""
    return render(request, 'pages/create_categories.html')


@login_required
def wizard_view(request, category='youtube'):
    """Pages 7, 8, 9, 10: Multi-step script generation wizard"""
    knowledge_bases = KnowledgeBase.objects.filter(user=request.user)
    user_model = request.user.profile.preferred_model if hasattr(request.user, 'profile') else 'claude-3-5-sonnet'

    # Predefined category defaults
    category_defaults = {
        'youtube': {'title': 'Why Small Ports Win', 'topic': 'How regional ports compete with mega-hubs', 'platform': 'youtube', 'duration': '8 min', 'tone': 'Informative'},
        'shorts': {'title': '3 Micro-Habits for Deep Focus', 'topic': 'Productivity hacks that actually work', 'platform': 'youtube_shorts', 'duration': '60 sec', 'tone': 'Bold'},
        'reels': {'title': 'Launch Day Reel', 'topic': 'Behind the scenes product release', 'platform': 'instagram_reels', 'duration': '45 sec', 'tone': 'Energetic'},
        'tiktok': {'title': 'The Truth About Side Hustles', 'topic': 'Debunking online passive income myths', 'platform': 'tiktok', 'duration': '30 sec', 'tone': 'Conversational'},
        'film': {'title': 'The Last Ferry', 'topic': 'Two captains stranded at midnight crossing', 'platform': 'short_film', 'duration': 'Scene 4 · 4 min', 'tone': 'Dramatic'},
        'screenplay': {'title': 'Submerged Signal', 'topic': 'Deep-sea research station mystery', 'platform': 'movie', 'duration': '15 min', 'tone': 'Cinematic'},
        'podcast': {'title': 'Supply Chains Decoded', 'topic': 'Interview with logistics pioneers', 'platform': 'podcast', 'duration': '15 min', 'tone': 'Conversational'},
    }
    defaults = category_defaults.get(category, category_defaults['youtube'])

    context = {
        'category': category,
        'knowledge_bases': knowledge_bases,
        'user_model': user_model,
        'defaults': defaults,
    }
    return render(request, 'pages/create_wizard.html', context)


@login_required
def wizard_api_generate_outline(request):
    """Step 4/5: Generates 6-beat structured outline"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        title = data.get('title', 'Untitled Script')
        topic = data.get('topic', '')
        description = data.get('description', '')
        audience = data.get('audience', 'General')
        platform = data.get('platform', 'YouTube')
        duration = data.get('duration', '8 min')
        tone = data.get('tone', 'Informative')
        more_options = data.get('more_options', '')
        model_name = data.get('model', 'claude-3-5-sonnet')
        kb_id = data.get('knowledge_base_id')

        knowledge_text = ""
        if kb_id:
            try:
                kb = KnowledgeBase.objects.get(id=kb_id, user=request.user)
                knowledge_text = " ".join([d.content_text for d in kb.documents.all()[:3]])
            except KnowledgeBase.DoesNotExist:
                pass

        service = ClaudeService(model=model_name)
        outline = service.generate_outline(
            title=title,
            topic=topic,
            description=description,
            audience=audience,
            platform=platform,
            duration=duration,
            tone=tone,
            more_options=more_options,
            knowledge_text=knowledge_text
        )

        return JsonResponse({
            'status': 'success',
            'outline': outline,
            'summary': f"{platform.title()} · {tone.lower()} · about {duration}"
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def wizard_api_generate_script(request):
    """Step 6: Writes the full script and persists to database"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        title = data.get('title', 'Why Small Ports Win')
        topic = data.get('topic', '')
        description = data.get('description', '')
        audience = data.get('audience', 'Students')
        platform = data.get('platform', 'youtube')
        duration = data.get('duration', '8 min')
        tone = data.get('tone', 'Informative')
        model_name = data.get('model', 'claude-3-5-sonnet')
        outline_list = data.get('outline', [])
        kb_id = data.get('knowledge_base_id')

        kb = None
        knowledge_text = ""
        if kb_id:
            try:
                kb = KnowledgeBase.objects.get(id=kb_id, user=request.user)
                knowledge_text = " ".join([d.content_text for d in kb.documents.all()[:3]])
            except KnowledgeBase.DoesNotExist:
                pass

        service = ClaudeService(model=model_name)
        script_parts = service.generate_full_script(
            title=title,
            topic=topic,
            description=description,
            audience=audience,
            platform=platform,
            duration=duration,
            tone=tone,
            outline_list=outline_list,
            knowledge_text=knowledge_text
        )

        # Create or update Script record
        script = Script.objects.create(
            user=request.user,
            title=title,
            topic=topic,
            description=description,
            audience=audience,
            platform=platform,
            duration=duration,
            tone=tone,
            claude_model=model_name,
            knowledge_base=kb,
            use_knowledge_base=bool(kb),
            outline_data=outline_list,
            hook=script_parts.get('hook', ''),
            introduction=script_parts.get('introduction', ''),
            main_content=script_parts.get('main_content', ''),
            conclusion=script_parts.get('conclusion', ''),
            call_to_action=script_parts.get('call_to_action', ''),
            full_content=script_parts.get('full_content', ''),
            status='draft',
            version=1,
            sources_used_count=3 if kb else 1
        )

        # Create initial version snapshot
        ScriptVersion.objects.create(
            script=script,
            version_number=1,
            content_snapshot=script.get_full_text(),
            note="Initial generation from Claude"
        )

        # Update user profile statistics
        if hasattr(request.user, 'profile'):
            request.user.profile.scripts_generated_count += 1
            request.user.profile.words_generated_count += script.word_count
            request.user.profile.save()

        return JsonResponse({
            'status': 'success',
            'script_id': script.id,
            'hook': script.hook,
            'introduction': script.introduction,
            'redirect_url': f'/editor/{script.id}/'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


# ---------------- SCRIPT EDITOR WORKSPACE ----------------

@login_required
def editor_view(request, script_id):
    """Page 11: Main Script Editor Workspace with section pills & Ask AI drawer"""
    script = get_object_or_404(Script, id=script_id, user=request.user)
    versions = script.versions.all()[:10]
    chat_messages = script.chat_messages.all()

    context = {
        'script': script,
        'versions': versions,
        'chat_messages': chat_messages,
    }
    return render(request, 'pages/editor.html', context)


@login_required
def save_script_api(request, script_id):
    """AJAX auto-save & manual save endpoint"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        script = get_object_or_404(Script, id=script_id, user=request.user)
        data = json.loads(request.body)

        if 'title' in data:
            script.title = data['title']
        if 'hook' in data:
            script.hook = data['hook']
        if 'introduction' in data:
            script.introduction = data['introduction']
        if 'main_content' in data:
            script.main_content = data['main_content']
        if 'conclusion' in data:
            script.conclusion = data['conclusion']
        if 'call_to_action' in data:
            script.call_to_action = data['call_to_action']
        if 'full_content' in data:
            script.full_content = data['full_content']

        # Increment version on explicit major save
        create_new_version = data.get('create_new_version', False)
        if create_new_version:
            script.version += 1
            ScriptVersion.objects.create(
                script=script,
                version_number=script.version,
                content_snapshot=script.get_full_text(),
                note=data.get('version_note', f"Revision {script.version}")
            )

        script.save()

        return JsonResponse({
            'status': 'success',
            'version': script.version,
            'word_count': f"{script.word_count:,}",
            'char_count': f"{script.char_count:,}",
            'estimated_time': f"about {max(1, round(script.estimated_speaking_minutes))} min"
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def toggle_script_favorite(request, script_id):
    """Toggles script favorite status"""
    if request.method == 'POST':
        script = get_object_or_404(Script, id=script_id, user=request.user)
        script.is_favorite = not script.is_favorite
        script.save()
        return JsonResponse({'status': 'success', 'is_favorite': script.is_favorite})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def script_version_history_api(request, script_id):
    """Returns version history list for script"""
    script = get_object_or_404(Script, id=script_id, user=request.user)
    versions_data = [
        {
            'version': v.version_number,
            'note': v.note or f"Version {v.version_number}",
            'created_at': v.created_at.strftime("%b %d, %H:%M"),
            'content': v.content_snapshot
        }
        for v in script.versions.all()
    ]
    return JsonResponse({'status': 'success', 'versions': versions_data})


# ---------------- EXPORT ----------------

@login_required
def export_script_view(request, script_id, format_type):
    """Page 13: Export script as PDF, DOCX, TXT, or Markdown"""
    script = get_object_or_404(Script, id=script_id, user=request.user)
    format_type = format_type.lower()

    if format_type == 'pdf':
        return ScriptExportService.export_pdf(script)
    elif format_type == 'docx':
        return ScriptExportService.export_docx(script)
    elif format_type == 'txt':
        return ScriptExportService.export_txt(script)
    elif format_type in ['markdown', 'md']:
        return ScriptExportService.export_markdown(script)
    else:
        return HttpResponse("Unsupported export format", status=400)


# ---------------- PROJECTS / FOLDERS ----------------

@login_required
def projects_list_view(request):
    """Pages 3 & 14: Projects list, offline simulator, and favorites"""
    filter_type = request.GET.get('filter', 'all')
    search_q = request.GET.get('q', '').strip()

    projects = Project.objects.filter(user=request.user)
    if filter_type == 'favorites':
        projects = projects.filter(is_favorite=True)
    elif filter_type == 'recent':
        projects = projects.order_by('-updated_at')

    if search_q:
        projects = projects.filter(name__icontains=search_q)

    knowledge_bases = KnowledgeBase.objects.filter(user=request.user)
    all_scripts = Script.objects.filter(user=request.user).order_by('-updated_at')

    context = {
        'projects': projects,
        'knowledge_bases': knowledge_bases,
        'scripts': all_scripts,
        'active_filter': filter_type,
        'search_q': search_q,
    }
    return render(request, 'pages/projects.html', context)


@login_required
def project_create_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        category = request.POST.get('category', 'General')
        kb_id = request.POST.get('knowledge_base_id')

        kb = None
        if kb_id:
            try:
                kb = KnowledgeBase.objects.get(id=kb_id, user=request.user)
            except KnowledgeBase.DoesNotExist:
                pass

        if name:
            project = Project.objects.create(
                user=request.user,
                name=name,
                description=description,
                category=category,
                knowledge_base=kb
            )
            return redirect('projects')

    return redirect('projects')


@login_required
def toggle_project_favorite(request, project_id):
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id, user=request.user)
        project.is_favorite = not project.is_favorite
        project.save()
        return JsonResponse({'status': 'success', 'is_favorite': project.is_favorite})
    return JsonResponse({'status': 'error'}, status=405)
