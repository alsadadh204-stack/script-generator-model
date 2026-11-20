from django.test import TestCase, Client
from django.contrib.auth.models import User
from accounts.models import UserProfile
from scripts.models import Script, Project, ScriptVersion
from knowledge.models import KnowledgeBase, KnowledgeDocument
import json


class ScriptForgeAITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='tester@example.com',
            email='tester@example.com',
            password='testpassword'
        )
        self.profile = self.user.profile
        self.profile.full_name = "Test User"
        self.profile.save()

        # Seed KB
        self.kb = KnowledgeBase.objects.create(
            user=self.user,
            name="Brand Guide",
            description="Brand voice rules"
        )
        self.doc = KnowledgeDocument.objects.create(
            user=self.user,
            knowledge_base=self.kb,
            title="brand-voice.pdf",
            status="indexed",
            content_text="Key tone: authoritative, witty, concise."
        )

        # Seed Project & Script
        self.project = Project.objects.create(
            user=self.user,
            name="Harbor Stories",
            category="Video"
        )
        self.script = Script.objects.create(
            user=self.user,
            project=self.project,
            title="Why Small Ports Win",
            topic="How regional ports compete with mega-hubs",
            platform="youtube",
            duration="8 min",
            tone="Informative",
            hook="Every big port makes headlines. The small ones quietly make money.",
            introduction="Today we look at three regional ports that grew by doing less, not more.",
            main_content="Point one: shorter queues beat bigger cranes.",
            conclusion="Efficiency beats raw scale.",
            call_to_action="Subscribe for more case studies.",
            status="draft",
            version=1
        )

    def test_landing_page(self):
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Your ideas.")

    def test_authentication(self):
        login_success = self.client.login(username='tester@example.com', password='testpassword')
        self.assertTrue(login_success)

        # Access Home
        resp = self.client.get('/home/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Welcome back")
        self.assertContains(resp, "Why Small Ports Win")

    def test_categories_and_wizard(self):
        self.client.login(username='tester@example.com', password='testpassword')
        resp = self.client.get('/create/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "YouTube Scripts")

        # Outline API
        outline_resp = self.client.post(
            '/api/wizard/outline/',
            data=json.dumps({
                'title': 'Test Script',
                'topic': 'Maritime logistics',
                'audience': 'Students',
                'platform': 'youtube',
                'duration': '8 min',
                'tone': 'Informative'
            }),
            content_type='application/json'
        )
        self.assertEqual(outline_resp.status_code, 200)
        outline_data = outline_resp.json()
        self.assertEqual(outline_data['status'], 'success')
        self.assertEqual(len(outline_data['outline']), 6)

        # Generation API
        gen_resp = self.client.post(
            '/api/wizard/generate/',
            data=json.dumps({
                'title': 'Generated Port Script',
                'topic': 'Regional ports',
                'audience': 'Founders',
                'platform': 'youtube',
                'duration': '8 min',
                'tone': 'Informative',
                'outline': outline_data['outline']
            }),
            content_type='application/json'
        )
        self.assertEqual(gen_resp.status_code, 200)
        gen_data = gen_resp.json()
        self.assertEqual(gen_data['status'], 'success')
        self.assertIn('script_id', gen_data)

    def test_editor_and_autosave(self):
        self.client.login(username='tester@example.com', password='testpassword')
        resp = self.client.get(f'/editor/{self.script.id}/')
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Why Small Ports Win")

        # Auto-save API
        save_resp = self.client.post(
            f'/api/editor/{self.script.id}/save/',
            data=json.dumps({
                'title': 'Why Small Ports Win (Updated)',
                'hook': 'Revised Hook: Every big port makes headlines.',
                'create_new_version': True
            }),
            content_type='application/json'
        )
        self.assertEqual(save_resp.status_code, 200)
        save_data = save_resp.json()
        self.assertEqual(save_data['version'], 2)

    def test_export_formats(self):
        self.client.login(username='tester@example.com', password='testpassword')
        # PDF
        pdf_resp = self.client.get(f'/editor/{self.script.id}/export/pdf/')
        self.assertEqual(pdf_resp.status_code, 200)
        self.assertEqual(pdf_resp['Content-Type'], 'application/pdf')

        # DOCX
        docx_resp = self.client.get(f'/editor/{self.script.id}/export/docx/')
        self.assertEqual(docx_resp.status_code, 200)

        # TXT
        txt_resp = self.client.get(f'/editor/{self.script.id}/export/txt/')
        self.assertEqual(txt_resp.status_code, 200)
        self.assertContains(txt_resp, "Why Small Ports Win")

        # Markdown
        md_resp = self.client.get(f'/editor/{self.script.id}/export/markdown/')
        self.assertEqual(md_resp.status_code, 200)
        self.assertContains(md_resp, "# Why Small Ports Win")

    def test_ai_tools_and_assistant(self):
        self.client.login(username='tester@example.com', password='testpassword')
        # AI tools page
        resp = self.client.get('/ai-tools/')
        self.assertEqual(resp.status_code, 200)

        # Standalone Hook generator API
        hook_resp = self.client.post(
            '/api/ai/run-tool/',
            data=json.dumps({'tool': 'hooks', 'topic': 'Boutique Coffee'}),
            content_type='application/json'
        )
        self.assertEqual(hook_resp.status_code, 200)
        self.assertTrue(len(hook_resp.json()['results']) > 0)

        # Contextual AI Chat Assistant
        chat_resp = self.client.post(
            '/api/ai/chat/',
            data=json.dumps({
                'script_id': self.script.id,
                'message': 'Give me an alternative opening'
            }),
            content_type='application/json'
        )
        self.assertEqual(chat_resp.status_code, 200)
        self.assertEqual(chat_resp.json()['status'], 'success')
        self.assertIn('suggested_snippet', chat_resp.json())

    def test_knowledge_and_projects(self):
        self.client.login(username='tester@example.com', password='testpassword')
        # Knowledge page
        k_resp = self.client.get('/knowledge/')
        self.assertEqual(k_resp.status_code, 200)
        self.assertContains(k_resp, "brand-voice.pdf")

        # Projects page
        p_resp = self.client.get('/projects/')
        self.assertEqual(p_resp.status_code, 200)
        self.assertContains(p_resp, "Harbor Stories")
