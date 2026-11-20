from django.urls import path
from . import views

urlpatterns = [
    # Categories & Generation Wizard
    path('create/', views.categories_view, name='create'),
    path('wizard/', views.wizard_view, name='wizard'),
    path('wizard/<str:category>/', views.wizard_view, name='wizard_category'),
    path('api/wizard/outline/', views.wizard_api_generate_outline, name='wizard_api_outline'),
    path('api/wizard/generate/', views.wizard_api_generate_script, name='wizard_api_generate'),

    # Script Editor Workspace
    path('editor/<int:script_id>/', views.editor_view, name='editor'),
    path('api/editor/<int:script_id>/save/', views.save_script_api, name='save_script_api'),
    path('api/editor/<int:script_id>/favorite/', views.toggle_script_favorite, name='toggle_script_favorite'),
    path('api/editor/<int:script_id>/versions/', views.script_version_history_api, name='script_version_history'),
    path('editor/<int:script_id>/export/<str:format_type>/', views.export_script_view, name='export_script'),

    # Projects
    path('projects/', views.projects_list_view, name='projects'),
    path('projects/new/', views.project_create_view, name='project_create'),
    path('projects/<int:project_id>/toggle-fav/', views.toggle_project_favorite, name='toggle_project_favorite'),
]
