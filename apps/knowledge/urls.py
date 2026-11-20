from django.urls import path
from . import views

urlpatterns = [
    path('knowledge/', views.knowledge_list_view, name='knowledge'),
    path('knowledge/upload/', views.upload_document_view, name='knowledge_upload'),
    path('knowledge/reprocess/<int:doc_id>/', views.reprocess_document_view, name='knowledge_reprocess'),
    path('knowledge/delete/<int:doc_id>/', views.delete_document_view, name='knowledge_delete'),
]
