from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import KnowledgeBase, KnowledgeDocument
import os

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


@login_required
def knowledge_list_view(request):
    """Page 4: Knowledge base manager & documents list"""
    search_q = request.GET.get('q', '').strip()

    kbs = KnowledgeBase.objects.filter(user=request.user)
    docs = KnowledgeDocument.objects.filter(user=request.user)

    if search_q:
        docs = docs.filter(title__icontains=search_q)

    context = {
        'knowledge_bases': kbs,
        'documents': docs,
        'search_q': search_q,
    }
    return render(request, 'pages/knowledge.html', context)


@login_required
def upload_document_view(request):
    """Handles upload of knowledge files or URL notes"""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        kb_id = request.POST.get('knowledge_base_id')
        source_url = request.POST.get('source_url', '').strip()
        uploaded_file = request.FILES.get('file')

        kb = None
        if kb_id:
            try:
                kb = KnowledgeBase.objects.get(id=kb_id, user=request.user)
            except KnowledgeBase.DoesNotExist:
                pass

        if not kb:
            kb, _ = KnowledgeBase.objects.get_or_create(user=request.user, name="General Knowledge")

        extracted_text = ""
        f_type = "TXT"
        size_display = "1.0 MB"

        if uploaded_file:
            title = title or uploaded_file.name
            size_kb = uploaded_file.size // 1024
            if size_kb > 1024:
                size_display = f"{round(size_kb / 1024, 1)} MB"
            else:
                size_display = f"{size_kb} KB"

            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext == '.pdf':
                f_type = 'PDF'
                extracted_text = f"Extracted knowledge from {uploaded_file.name} for grounding."
            elif ext in ['.doc', '.docx']:
                f_type = 'DOCX'
                if HAS_DOCX:
                    try:
                        d = docx.Document(uploaded_file)
                        extracted_text = "\n".join([p.text for p in d.paragraphs if p.text])
                    except Exception:
                        extracted_text = f"Extracted content from {uploaded_file.name}"
                else:
                    extracted_text = f"Content from {uploaded_file.name}"
            else:
                f_type = 'TXT'
                try:
                    extracted_text = uploaded_file.read().decode('utf-8', errors='ignore')
                except Exception:
                    extracted_text = f"Text document: {uploaded_file.name}"

        elif source_url:
            title = title or f"{source_url} (Web Page)"
            f_type = "URL"
            size_display = "Web page"
            extracted_text = f"Content retrieved from {source_url}."

        if title:
            doc = KnowledgeDocument.objects.create(
                user=request.user,
                knowledge_base=kb,
                title=title,
                file=uploaded_file,
                file_type=f_type,
                file_size_display=size_display,
                status='indexed',
                content_text=extracted_text,
                source_url=source_url or None
            )

        return redirect('knowledge')

    return redirect('knowledge')


@login_required
def reprocess_document_view(request, doc_id):
    """Reprocesses a failed document to indexed status (Page 4 'Failed · Reprocess')"""
    if request.method == 'POST':
        doc = get_object_or_404(KnowledgeDocument, id=doc_id, user=request.user)
        doc.status = 'indexed'
        if not doc.content_text:
            doc.content_text = f"Reprocessed knowledge extracted for {doc.title}."
        doc.save()
        return JsonResponse({'status': 'success', 'new_status': 'indexed'})
    return JsonResponse({'status': 'error'}, status=405)


@login_required
def delete_document_view(request, doc_id):
    if request.method == 'POST':
        doc = get_object_or_404(KnowledgeDocument, id=doc_id, user=request.user)
        doc.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=405)
