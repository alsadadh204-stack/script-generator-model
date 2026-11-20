from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json

from scripts.models import Script
from .models import AIChatMessage, GenerationLog
from .services import ClaudeService


@login_required
def ai_tools_page_view(request):
    """Standalone page for Quick AI Tools (Rewrite, Hook, Title, Idea, Repurpose, Scene breakdown)"""
    user_scripts = Script.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'pages/ai_tools.html', {'scripts': user_scripts})


@login_required
def ai_chat_api(request):
    """Page 12: Contextual AI Assistant Chat Drawer endpoint"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        script_id = data.get('script_id')
        message = data.get('message', '').strip()
        context_section = data.get('context_section', 'hook')

        if not message:
            return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)

        script = get_object_or_404(Script, id=script_id, user=request.user)

        # Save user message
        AIChatMessage.objects.create(
            script=script,
            user=request.user,
            role='user',
            content=message
        )

        # Get recent history
        recent_chats = [
            {'role': m.role, 'content': m.content}
            for m in script.chat_messages.all()[:8]
        ]

        service = ClaudeService(model=script.claude_model)
        result = service.assistant_chat(
            script_title=script.title,
            script_content=script.get_full_text(),
            chat_history=recent_chats,
            user_message=message,
            context_section=context_section
        )

        # Save assistant message
        bot_msg = AIChatMessage.objects.create(
            script=script,
            user=request.user,
            role='assistant',
            content=result['text'],
            suggested_action=result.get('suggested_action', ''),
            suggested_snippet=result.get('suggested_snippet', ''),
            target_section=context_section
        )

        return JsonResponse({
            'status': 'success',
            'reply': result['text'],
            'suggested_action': result.get('suggested_action', ''),
            'suggested_snippet': result.get('suggested_snippet', ''),
            'target_section': context_section,
            'message_id': bot_msg.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def ai_context_action_api(request):
    """Floating selection popup: Rewrite, Expand, Shorten, Improve"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        action = data.get('action', 'Rewrite')
        selected_text = data.get('text', '').strip()

        if not selected_text:
            return JsonResponse({'status': 'error', 'message': 'No text selected'}, status=400)

        service = ClaudeService()
        revised = service.context_action(action, selected_text)

        return JsonResponse({
            'status': 'success',
            'revised_text': revised,
            'action': action
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def ai_run_standalone_tool_api(request):
    """Executes standalone AI tools: hooks, titles, ideas, rewriter, repurpose, scene breakdown"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        tool = data.get('tool')  # 'hooks', 'titles', 'ideas', 'repurpose', 'scene_breakdown'
        service = ClaudeService()

        if tool == 'hooks':
            topic = data.get('topic', 'Why Small Ports Win')
            platform = data.get('platform', 'YouTube')
            results = service.generate_hooks(topic, platform)
            return JsonResponse({'status': 'success', 'results': results, 'tool': tool})

        elif tool == 'titles':
            topic = data.get('topic', 'Why Small Ports Win')
            results = service.generate_titles(topic)
            return JsonResponse({'status': 'success', 'results': results, 'tool': tool})

        elif tool == 'ideas':
            niche = data.get('niche', 'Supply Chain & Logistics')
            results = service.generate_ideas(niche)
            return JsonResponse({'status': 'success', 'results': results, 'tool': tool})

        elif tool == 'scene_breakdown':
            content = data.get('content', '')
            scenes = [
                {
                    "scene_number": 1,
                    "heading": "SCENE 1 - EXT. CARGO DOCKS - DAWN",
                    "visual": "Wide drone reveal of a bustling container vessel. Fog clings to the cranes.",
                    "audio": "Distant foghorn, diesel engines idling.",
                    "dialogue_or_vo": "VO: 'Every big port makes headlines. The small ones quietly make money.'",
                    "duration": "15 sec"
                },
                {
                    "scene_number": 2,
                    "heading": "SCENE 2 - INT. LOGISTICS CONTROL ROOM - DAY",
                    "visual": "Dual-monitor setup displaying rapid customs turnaround metrics in green.",
                    "audio": "Soft keyboard clicks and ambient radio chatter.",
                    "dialogue_or_vo": "VO: 'Today we look at three regional hubs that grew by doing less, not more.'",
                    "duration": "30 sec"
                },
                {
                    "scene_number": 3,
                    "heading": "SCENE 3 - EXT. BERTH 4 - DAY",
                    "visual": "Time-lapse of specialized cold-chain reefers being loaded in under 4 hours.",
                    "audio": "Upbeat, rhythmic synth bassline kicks in.",
                    "dialogue_or_vo": "VO: 'Point one: shorter queues beat bigger cranes.'",
                    "duration": "45 sec"
                }
            ]
            return JsonResponse({'status': 'success', 'scenes': scenes, 'tool': tool})

        elif tool == 'repurpose':
            source_text = data.get('content', '')
            target_format = data.get('target_format', 'tiktok')
            repurposed = (
                f"🔥 QUICK REEL / TIKTOK HOOK:\n"
                f"Stop watching mega-hubs. Here is how small ports are secretly winning.\n\n"
                f"⚡ 3 FAST BEATS:\n"
                f"1. Zero anchor wait times (6-hour turnaround vs 14 days)\n"
                f"2. Niche high-margin cold chain cargo\n"
                f"3. Velocity beats scale every time.\n\n"
                f"👉 Drop a comment: Would you invest in regional infrastructure?"
            )
            return JsonResponse({'status': 'success', 'repurposed_content': repurposed, 'tool': tool})

        return JsonResponse({'status': 'error', 'message': 'Unknown tool'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
