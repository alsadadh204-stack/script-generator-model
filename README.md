# SCRIPTLY AI · ScriptForge AI

> **"Your ideas. Perfectly scripted."**  
> *A modern AI scriptwriting SaaS web application built with Django, Anthropic Claude, and Document Grounding.*

---

## 🌟 Overview

**SCRIPTLY AI** (branded in-app as **ScriptForge AI**) is a production-grade scriptwriting and creative development platform designed specifically for video creators, YouTube creators, filmmakers, advertisers, marketing teams, podcasters, and storytellers. 

The application implements the design specifications from the 16 reference screens with high visual fidelity, featuring a dark aesthetic (`#0E0C0A` obsidian surface with warm coral `#FF7A3D` accents), pill-shaped components, multi-step creation wizards, contextual AI editing, document-grounded RAG retrieval, and multi-format exports.

---

## ✨ Key Features

### 1. 🎬 Multi-Step Script Generation Wizard (Screenshots 7 – 10)
- **Step 2 (Requirements):** Custom title, topic prompt, audience targeting, platform selector (YouTube, Shorts, Reels, TikTok, Podcasts, Screenplays), duration, tone selector pills (Informative, Friendly, Bold, Cinematic, Conversational), and expandable custom instructions.
- **Step 3 (AI Options):** Claude model selector cards (**Claude Sonnet**, **Claude Opus**, **Claude Haiku**), interactive Creativity slider, script length selector (Short, Medium, Long), and Knowledge Base toggle.
- **Step 5 (Review Outline):** Analysis summary banner and 6 chronological editable outline beats (Hook, Introduction, Main Content, Engagement, Conclusion, Call to Action) with inline editing and one-click regenerate.
- **Step 6 (Writing Script):** Real-time generation simulation with live typewriter text and animated cursor (`▍`), source passage attribution badge, and transition to the editor.

### 2. 📝 Section-Aware Script Editor (Screenshot 11)
- **Real-time Metrics:** Live word count, character count, and estimated speaking duration pill (e.g. `1,240 words · 6,980 chars · about 8 min`).
- **Section Tabs:** Quick jumping to `Hook`, `Intro`, `Main`, and `Outro`.
- **Floating AI Popup:** Highlight any sentence or paragraph to trigger instant contextual revisions: **Rewrite**, **Expand**, **Shorten**, or **Improve**.
- **Autosave & Version Control:** Debounced AJAX autosave with version snapshots and history inspection.

### 3. 💬 Contextual AI Assistant Drawer (Screenshot 12)
- Slide-over chat drawer that references the current script context.
- Provides interactive alternative beats and dialogue lines.
- One-click action buttons: **Replace hook** and **Insert below** to modify the script directly without copy-paste friction.

### 4. 📚 Grounded Knowledge Base (Screenshot 4)
- Upload Brand Voice guidelines, company PDFs, interview DOCX files, or web URLs.
- Document status tracking: `Indexed` (green), `Indexing...` (progress bar), and `Failed · Reprocess`.
- Grounding context is injected into Claude prompts to eliminate hallucinations.

### 5. 📁 Projects & Offline State Simulation (Screenshots 3 & 14)
- Organize scripts by project folders with knowledge base links.
- Star/favorite toggle and search filtering (`All`, `Recent`, `Favorites`).
- **Offline Mode Simulator:** Test how scripts remain editable offline and sync automatically upon reconnection.

### 6. 📤 Multi-Format Export Engine (Screenshot 13)
- Export directly to:
  - **PDF:** Screenplay layout styled with ReportLab.
  - **DOCX:** Microsoft Word formatted with visual directions and cues.
  - **TXT:** Standard plain-text teleprompter format.
  - **Markdown (.md):** Clean formatted markdown.

### 7. ⚡ Quick AI Tools Suite
- **Hook Generator:** 8 psychological hook styles (Curiosity, Shock, Contrarian, Problem-First, Bold Statement, Story, Mystery, Question).
- **Title Generator:** SEO, curiosity-driven, and high-CTR titles.
- **Idea Generator:** Turn creative angles directly into scripts.
- **Content Repurposer:** Transform YouTube scripts into TikTok/Reel beat sheets.
- **Scene Breakdown:** Generates sluglines, visual descriptions, audio cues, and dialogue.

---

## 🛠️ Technology Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python 3.14+, Django 6.1 (Modular Apps Architecture) |
| **Frontend** | HTML5, CSS3 Custom Design System, Vanilla JavaScript |
| **Typography & Icons** | Inter (Google Fonts), SVG Icon System |
| **AI Integration** | Anthropic Claude API (`anthropic` SDK) with realistic intelligent engine fallback |
| **Export Services** | ReportLab (PDF), python-docx (DOCX), Markdown |
| **Database** | SQLite (development) / PostgreSQL-compatible schema |

---

## 📂 Project Architecture

```
d:\APPLICATION SCRIPT\
├── manage.py
├── requirements.txt
├── .env.example
├── .env
├── README.md
│
├── config/
│   ├── settings.py          # Core settings, apps, templates, auth config
│   ├── urls.py              # Root URL routing
│   └── wsgi.py
│
├── apps/
│   ├── accounts/            # User authentication, profiles, themes, plan usage
│   ├── core/                # Landing page, home dashboard, search, seed command
│   ├── scripts/             # Script models, wizard, editor, exports, projects
│   ├── ai_engine/           # Claude API integration, chat assistant, standalone tools
│   ├── knowledge/           # Knowledge bases, document upload, status indexing
│   └── templates_manager/   # Pre-built script templates library
│
├── templates/
│   ├── base.html            # Top desktop nav, mobile bottom nav, toast, modals
│   └── pages/
│       ├── landing.html     # SaaS marketing landing page
│       ├── auth/            # Sign in and Sign up views
│       ├── home.html        # Dashboard matching Screenshot 1
│       ├── create_categories.html # Categories grid matching Screenshot 2
│       ├── create_wizard.html     # 8-step wizard matching Screenshots 7-10
│       ├── editor.html            # Script editor matching Screenshot 11-13
│       ├── projects.html          # Projects list matching Screenshots 3 & 14
│       ├── knowledge.html         # Knowledge base matching Screenshot 4
│       ├── profile.html           # Profile & theme matching Screenshot 5
│       ├── ai_tools.html          # Standalone quick AI creator tools
│       ├── templates.html         # Template showcase
│       └── search_results.html    # Global search
│
└── static/
    ├── css/styles.css       # Obsidian & warm coral dark design system
    └── js/
        ├── main.js          # Toast notifications & network listeners
        ├── wizard.js        # Multi-step state, Claude outline & streaming
        └── editor.js        # Autosave, stats counter, AI drawer, exports
```

---

## 🚀 Quickstart & Setup Guide

### 1. Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Git (optional)

### 2. Environment Configuration
Create your local environment file:
```bash
copy .env.example .env
```
Optionally configure your Anthropic Claude API key in `.env`:
```env
ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here
ANTHROPIC_DEFAULT_MODEL=claude-3-5-sonnet-20241022
DEBUG=True
```
*(Note: If no API key is provided, the application runs an intelligent simulated generator with contextual script completions and chat responses so you can test every workflow end-to-end).*

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup & Demo Data Seeding
Run database migrations:
```bash
python manage.py migrate
```
Seed initial demo data matching the screenshots:
```bash
python manage.py seed_data
```

### 5. Run Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open your browser and navigate to:
**http://127.0.0.1:8000/**

---

## 🔑 Demo Account Credentials

| Field | Value |
| :--- | :--- |
| **Email / Username** | `you@example.com` |
| **Password** | `password123` |
| **Initial Role** | Pro Plan Subscriber ("Your name", 24 Scripts, 38k Words) |

---

## 🧪 Automated Testing

Run the Django automated test suite:
```bash
python manage.py test apps/core
```
All integration tests cover:
- Authentication, landing page, and dashboard metrics
- Category picker & multi-step wizard outline generation
- Script persistence and real-time word/character statistics
- PDF, DOCX, TXT, and Markdown export rendering
- Contextual Ask AI Assistant chat drawer
- Knowledge base document indexing and project favorites
