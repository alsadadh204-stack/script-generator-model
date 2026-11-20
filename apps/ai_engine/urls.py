from django.urls import path
from . import views

urlpatterns = [
    path('ai-tools/', views.ai_tools_page_view, name='ai_tools'),
    path('api/ai/chat/', views.ai_chat_api, name='ai_chat_api'),
    path('api/ai/context-action/', views.ai_context_action_api, name='ai_context_action'),
    path('api/ai/run-tool/', views.ai_run_standalone_tool_api, name='ai_run_tool'),
]
