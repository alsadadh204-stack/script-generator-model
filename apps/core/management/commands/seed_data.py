from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile
from knowledge.models import KnowledgeBase, KnowledgeDocument
from scripts.models import Project, Script, ScriptVersion
from templates_manager.models import ScriptTemplate
from ai_engine.models import AIChatMessage


class Command(BaseCommand):
    help = 'Seeds initial demo database matching ScriptForge AI / Scriptly AI design references'

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # 1. Create or get user
        user, created = User.objects.get_or_create(
            username='you@example.com',
            defaults={
                'email': 'you@example.com',
                'first_name': 'Your',
                'last_name': 'name',
            }
        )
        user.set_password('password123')
        user.save()

        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.full_name = "Your name"
        profile.plan = "Pro plan"
        profile.plan_resets_on = "the 1st"
        profile.theme = "dark"
        profile.language = "English"
        profile.preferred_model = "claude-3-5-sonnet"
        profile.scripts_generated_count = 24
        profile.words_generated_count = 38000
        profile.usage_percentage = 45
        profile.save()

        # 2. Knowledge Bases
        kb_brand, _ = KnowledgeBase.objects.get_or_create(
            user=user,
            name="Brand Guide",
            defaults={"description": "Corporate tone guidelines and value propositions"}
        )

        kb_research, _ = KnowledgeBase.objects.get_or_create(
            user=user,
            name="Research Notes",
            defaults={"description": "Interviews, competitor notes, and empirical research"}
        )

        # Knowledge Documents
        docs = [
            (kb_brand, "brand-voice.pdf", "PDF", "2.1 MB", "indexed", "Core Brand Voice: Bold, intellectual, authoritative yet accessible."),
            (kb_brand, "brand-strategy.docx", "DOCX", "1.5 MB", "indexed", "Our target is enterprise buyers seeking simplicity and speed."),
            (kb_brand, "messaging-pillars.pdf", "PDF", "850 KB", "indexed", "Three pillars: Zero latency, total transparency, elegant simplicity."),
            (kb_brand, "tone-matrix.pdf", "PDF", "420 KB", "indexed", "High-contrast visual pacing, avoid passive voice, deliver instant hooks."),
            (kb_research, "interview.docx", "DOCX", "640 KB", "indexing", "Subject: Port logistics executive on supply chain bottlenecks."),
            (kb_research, "competitor-page (URL)", "URL", "Web page", "failed", "Competitor positioning analysis across top 5 maritime hubs."),
            (kb_research, "market-analysis.pdf", "PDF", "3.4 MB", "indexed", "Global container shipping trends and regional hub dynamics."),
            (kb_research, "user-survey-q3.csv", "CSV", "1.1 MB", "indexed", "Survey data showing 74% preference for regional direct shipping."),
        ]

        for kb, title, f_type, size, status, content in docs:
            doc, _ = KnowledgeDocument.objects.get_or_create(
                user=user,
                knowledge_base=kb,
                title=title,
                defaults={
                    "file_type": f_type,
                    "file_size_display": size,
                    "status": status,
                    "content_text": content,
                }
            )

        # 3. Projects
        p1, _ = Project.objects.get_or_create(
            user=user,
            name="Harbor Stories",
            defaults={"knowledge_base": kb_brand, "is_favorite": True, "category": "Video"}
        )
        p2, _ = Project.objects.get_or_create(
            user=user,
            name="Midnight Ferry",
            defaults={"is_favorite": True, "category": "Film"}
        )
        p3, _ = Project.objects.get_or_create(
            user=user,
            name="Spring Launch Campaign",
            defaults={"is_favorite": True, "category": "Marketing"}
        )
        p4, _ = Project.objects.get_or_create(
            user=user,
            name="Pilot Podcast",
            defaults={"is_favorite": False, "category": "Audio"}
        )

        # 4. Scripts
        s1, _ = Script.objects.get_or_create(
            user=user,
            title="Why Small Ports Win",
            defaults={
                "project": p1,
                "knowledge_base": kb_brand,
                "topic": "How regional ports compete with mega-hubs",
                "description": "An explainer for supply chain beginners.",
                "audience": "Students",
                "platform": "youtube",
                "duration": "8 min",
                "tone": "Informative",
                "language": "English",
                "claude_model": "claude-3-5-sonnet",
                "creativity": "Balanced",
                "script_length": "Medium",
                "use_knowledge_base": True,
                "sources_used_count": 3,
                "version": 3,
                "word_count": 1240,
                "char_count": 6980,
                "estimated_speaking_minutes": 8.0,
                "status": "draft",
                "sync_status": "synced",
                "is_favorite": True,
                "hook": "Every big port makes headlines. The small ones quietly make money.",
                "introduction": "Today we look at three regional ports that grew by doing less, not more.",
                "main_content": (
                    "Point one: shorter queues beat bigger cranes.\n\n"
                    "[VISUAL: Split screen comparison between a crowded mega-terminal with 14-day anchor wait times vs a sleek regional hub.]\n\n"
                    "While mega-hubs invest billions into deeper berths and gigantic machinery, turnaround latency kills profitability. "
                    "A medium-scale facility with predictable 6-hour docking cycles captures higher margin shipping every single quarter.\n\n"
                    "Point two: specialized throughput and agile customs.\n\n"
                    "[VISUAL: Drone shot gliding over dedicated cold-chain corridors.]\n\n"
                    "By focusing on specific cargo categories—high-value refrigerated goods and express freight—smaller operations "
                    "eliminate general congestion entirely. They don't compete on volume; they compete on velocity."
                ),
                "conclusion": "Scale looks impressive from an airplane. But efficiency, focus, and low friction are what actually drive sustained yield. When you optimize for speed rather than vanity metrics, the smaller player wins every time.",
                "call_to_action": "Subscribe for the next case study.",
                "outline_data": [
                    {"step": 1, "title": "Hook", "description": "Open with a surprising comparison"},
                    {"step": 2, "title": "Introduction", "description": "Why small ports matter"},
                    {"step": 3, "title": "Main content", "description": "Three regional ports, one lesson each"},
                    {"step": 4, "title": "Engagement", "description": "Ask viewers to pick a port"},
                    {"step": 5, "title": "Conclusion", "description": "Recap the three lessons"},
                    {"step": 6, "title": "Call to action", "description": "Subscribe for the next case study"},
                ]
            }
        )

        # Seed Chat Messages for script 1 (matching page 12)
        AIChatMessage.objects.get_or_create(
            script=s1,
            user=user,
            role="user",
            content="Give me an alternative opening"
        )
        AIChatMessage.objects.get_or_create(
            script=s1,
            user=user,
            role="assistant",
            content='Here is a quieter option: "The biggest port in the region handled the least cargo per hour." Want me to build the next beat around that?',
            suggested_action="replace_hook",
            suggested_snippet="The biggest port in the region handled the least cargo per hour."
        )

        s2, _ = Script.objects.get_or_create(
            user=user,
            title="The Last Ferry",
            defaults={
                "project": p2,
                "platform": "short_film",
                "duration": "Scene 4 · 4 min",
                "tone": "Dramatic",
                "status": "draft",
                "sync_status": "synced",
                "version": 1,
                "word_count": 850,
                "char_count": 4820,
                "hook": "The engine choked twice before the pilot gave up trying to conceal the warning light.",
                "introduction": "Night settled over the crossing like wet wool.",
                "main_content": "[VISUAL: Low angle cabin shot. Rain streaks across the forward glass.]\nELENA\n'If we turn back now, we lose the tide.'\n\nMATEO\n'If we don't, we lose the hull.'",
                "conclusion": "The silence in the wheelhouse spoke louder than any gauge.",
            }
        )

        s3, _ = Script.objects.get_or_create(
            user=user,
            title="Launch Day Reel",
            defaults={
                "project": p3,
                "platform": "instagram_reels",
                "duration": "45 sec",
                "tone": "Energetic",
                "status": "draft",
                "sync_status": "synced",
                "version": 1,
                "word_count": 120,
                "char_count": 680,
                "hook": "Stop wasting 4 hours on your video scripts.",
                "introduction": "Here is how the top 1% of creators script their content in 90 seconds.",
                "main_content": "1. Feed your core thesis into ScriptForge AI.\n2. Pick your platform and pacing.\n3. Let Claude generate full scenes, visual cues, and killer hooks.",
                "call_to_action": "Link in bio to try it free today.",
            }
        )

        # 5. Templates (Matching screenshot page 2)
        templates_data = [
            ("YouTube Scripts", "video", "Hook to CTA", "Complete high-retention long-form YouTube structure with viral hook and retention beats.", "youtube", "8 min", "Informative"),
            ("YouTube Shorts", "video", "Fast vertical hooks", "Ultra-fast punchy vertical video format with 3-second hook and high-loop ending.", "youtube_shorts", "60 sec", "Bold"),
            ("Instagram Reels", "video", "Short visual beats", "Visual-first social video script with dynamic camera callouts and relatable problem solving.", "instagram_reels", "45 sec", "Friendly"),
            ("TikTok Scripts", "video", "Trend-ready", "Trend-aligned viral storytelling with fast cuts, conversational phrasing, and high-engagement comment hooks.", "tiktok", "30 sec", "Conversational"),
            ("Movie Screenplays", "film", "Scenes and dialogue", "Industry-standard cinematic screenplay layout with scene sluglines, character dialogue, and parentheticals.", "movie", "15 min", "Dramatic"),
            ("Short Films", "film", "Compact story arcs", "Tight narrative three-act structure ideal for indie cinema, film festival submissions, and proof-of-concepts.", "short_film", "10 min", "Cinematic"),
            ("Web Series", "film", "Episode beats", "Episodic narrative structure with cliffhangers, cold opens, and recurring character dynamics.", "web_series", "12 min", "Storytelling"),
            ("Podcast Scripts", "audio", "Host and guest", "Engaging interview and monologue format with host questions, guest tangents, and segment transitions.", "podcast", "15 min", "Conversational"),
            ("Product Commercial", "business", "Problem to Solution", "High-conversion direct-response commercial with customer pain-point agitation, product reveal, and clear CTA.", "advertisement", "30 sec", "Persuasive"),
            ("Brand Story", "business", "Hero story arc", "Inspiring corporate documentary style highlighting mission, culture, and visionary leadership.", "advertisement", "2 min", "Inspirational"),
        ]

        for name, cat, tagline, desc, plat, dur, tone in templates_data:
            ScriptTemplate.objects.get_or_create(
                name=name,
                defaults={
                    "category": cat,
                    "tagline": tagline,
                    "description": desc,
                    "default_platform": plat,
                    "default_duration": dur,
                    "default_tone": tone,
                    "is_builtin": True
                }
            )

        self.stdout.write(self.style.SUCCESS("Database successfully seeded!"))
