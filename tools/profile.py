"""Everything the profile graphics say. Edit this, then run `python tools/build.py`."""

NAME = 'Aryan Jain'
KICKER = 'RESEARCH ENGINEER  ·  IMPERIAL COLLEGE LONDON'
TAGLINE = 'Building reliable AI systems across machine learning, systems and distributed infrastructure.'
CHIPS = ['M.ENG COMPUTING · AI & ML', 'FIRST-CLASS', 'LONDON']

NOW = (2026, 10)  # the "now" line on the timeline

# Link buttons under the hero: (file name, glyph, label, handle, url)
LINKS = [
    ('linkedin', 'linkedin', 'LinkedIn', 'aryanthejain', 'https://www.linkedin.com/in/aryanthejain/'),
    ('scholar', 'book', 'Google Scholar', '3 papers', 'https://scholar.google.com/citations?user=-r_1bb0AAAAJ'),
    ('orcid', 'orcid', 'ORCID', '0009-0005-7034-0371', 'https://orcid.org/0009-0005-7034-0371'),
    ('email', 'mail', 'Email', 'aryanthejain@gmail.com', 'mailto:aryanthejain@gmail.com'),
    ('phone', 'phone', 'Phone', '+44 7721 170621', 'tel:+447721170621'),
]

HIGHLIGHTS = [
    ('trophy', 'Amadeus Award', 'Best 2nd-year group project'),
    ('rocket', 'NASA Artemis', '"Moon to Mars" winner'),
    ('globe', 'COP29 dataset', 'Climate TRACE inventory'),
    ('medal', 'UN V-Award', 'Social impact, 2022'),
]

NOW_ITEMS = [
    ('agents', 'Research Engineer · stealth startup',
     'Building a learned governance layer for multi-agent systems: adaptive permissioning, escalation and auditability.', None),
    ('people', 'Co-Chair elect, Imperial College AI Society',
     'And Lead of Google Developer Groups at Imperial, running workshops, projects and the AI-in-Energy Hackathon.', None),
    ('cap', 'Year 3 · M.Eng Computing (AI & ML)', None,
     ['Generative AI', 'Mathematics for ML', 'NLP', 'Computer Vision', 'Concurrency', 'Advanced Computer Architecture',
      'Digital Systems Design', 'Systems Performance Engineering', 'Corporate Finance']),
]

# (logo file or glyph, organisation, role, start (y, m), end (y, m) or None for ongoing, kind)
EXPERIENCE = [
    ('bending-spoons', 'Bending Spoons · Harvest', 'Software Engineering Intern', (2026, 7), (2026, 9), 'work'),
    ('glyph:stealth', 'Stealth startup', 'Research Engineer, part-time', (2026, 1), None, 'work'),
    ('sarvam', 'Sarvam AI', 'Data Infrastructure Intern', (2025, 7), (2025, 9), 'work'),
    ('people-plus-ai', 'People+ai', 'Intern, AI at the Edge', (2024, 11), (2025, 3), 'work'),
    ('imperial', 'Imperial College London', 'M.Eng Computing (AI & ML)', (2024, 9), None, 'study'),
    ('climate-trace', 'Climate TRACE · WattTime', 'Researcher', (2022, 7), (2024, 8), 'work'),
    ('artpark', 'ARTPARK · IISc Bangalore', 'Computer Vision Intern', (2021, 10), (2022, 7), 'work'),
    ('glyph:watchbot', 'WatchBOT', 'Founder & Technical Lead', (2020, 12), (2021, 9), 'work'),
]

IMPACT = {
    'logo': 'bending-spoons',
    'title': 'BENDING SPOONS  ·  HARVEST',
    'subtitle': 'SOFTWARE ENGINEERING INTERN  ·  JUL–SEP 2026',
    'stats': [
        ('115', 'merged PRs', 'in 13 weeks'),
        ('#1', 'contributor', 'on the team this quarter'),
        ('6.7×', 'faster assignment page', '2.7s → 0.4s'),
        ('$5M', 'ARR product rebuilt', 'natively inside Harvest'),
    ],
    'bullets': [
        "Rebuilt Forecast, Harvest's decade-old sister product, natively inside Harvest: owned architecture, data models, APIs and delivery across capacity planning, scheduling, utilisation and plan-vs-actual.",
        "Built a self-serve import that brings Forecast customers' scheduling history across without loss.",
        'Kept the planning engine interactive across 1,000-day horizons, 20k assignments and 2,000+ projects. Also shipped milestone billing, project tags and permissions, and gave 48 code reviews.',
    ],
}

# Project cards. icon: logo file or 'glyph:<name>'.
PROJECTS = {
    'alongside': {
        'icon': 'glyph:alongside',
        'title': 'Alongside',
        'badge': 'AMADEUS AWARD  ·  93.3%',
        'text': "Facilitated peer-support groups for bereaved young adults: a group room, a private line to the facilitator, a quiet space and a facilitator dashboard. Imperial's best second-year group project.",
        'tags': ['Next.js', 'Scala Play', 'PostgreSQL'],
    },
    'p2p': {
        'icon': 'glyph:bolt',
        'title': 'P2P energy trading',
        'badge': 'INDIA ENERGY STACK  ·  BECKN',
        'text': 'Peer-to-peer solar trading with an AI agent on web, WhatsApp and voice. I built Ed25519 request signing, the trust engine and trade limits, and overselling protection with row locks and Redlock.',
        'tags': ['TypeScript', 'Beckn', 'Redis'],
    },
    'sarvam': {
        'icon': 'sarvam',
        'title': 'Sarvam AI',
        'badge': 'SOVEREIGN AI  ·  2025',
        'text': 'A WhatsApp multi-agent system that gets people through government schemes end to end, using RAG, type-safe orchestration and Playwright browser execution in a vLLM loop, with zero-shot onboarding for new schemes.',
        'tags': ['vLLM', 'Playwright', 'Agents'],
    },
    'eqip': {
        'icon': 'glyph:scales',
        'title': 'EQIP',
        'badge': 'LEGAL-TECH  ·  AGENTS',
        'text': 'AI agents for equitable IP collaboration: contribution attribution, ownership arrangements and contract drafting, grounded in a retrieval-augmented knowledge base.',
        'tags': ['FastAPI', 'Streamlit', 'RAG'],
    },
}

CLIMATE = {
    'icon': 'climate-trace',
    'title': 'Climate TRACE · WattTime',
    'badge': 'COP29 EMISSIONS INVENTORY  ·  AGU 2023 & 2024',
    'text': 'A global geospatial ML pipeline that finds wastewater treatment plants in satellite imagery and estimates their greenhouse gas emissions, built with researchers from Johns Hopkins APL and Stanford.',
    'tags': ['TensorFlow', 'Inception v3', 'Remote sensing'],
    'stats': [('2,637', 'plants found'), ('200', 'cities'), ('+300%', 'vs. official China data'), ('20×', 'throughput')],
}

SYSTEMS = [
    ('glyph:board', 'NNUE chess engine', 'Self-trained, with a custom C inference backend on bare-metal Raspberry Pi graphics.'),
    ('glyph:chip', 'ARMv8-A emulator', 'AArch64 decoding, execution and an assembler. Scored 100%.'),
    ('glyph:terminal', 'PintOS kernel', 'Scheduling, synchronisation, virtual memory, syscalls and file systems.'),
    ('glyph:braces', 'WACC compiler', 'Type checking, IRs, optimisations and native code generation.'),
]

RESEARCH = [
    ('Harnessing Satellite Images and Machine Learning to Detect Wastewater Treatment Plants Globally',
     'A. Jain, L. Sridhar, A. Davitt, G. Volpato, G. McCormick, H. Srinivas', 'AGU FALL MEETING 2023 · GC21F-0964'),
    ('ClimateTRACE Facility-Level Wastewater Emissions Dataset',
     'G. Collins, A. Jain, P. Sicurello, E. Kirwan, P. Tulloch, C. Piatko, L. Sridhar et al.', 'AGU FALL MEETING 2024 · H53O-1308'),
    ('Wastewater Sector: Emissions from Wastewater Treatment Plants',
     'A. Jain, L. Sridhar, A. Davitt', 'AGU24 · 2024'),
    ('AI at the Edge: Imagining the Mega Impact',
     'Co-lead and technical author', 'PEOPLE+AI · REPORT'),
]

LEADERSHIP = [
    ('bolt', 'AI-in-Energy Hackathon', 'Led it: 450+ participants, £25k in prizes, sponsors incl. Google, Anthropic and Beckn.'),
    ('people', 'Google Developer Groups', 'Lead at Imperial, after a year as Technical Director of the student club.'),
    ('medal', 'DhanDanaDan', 'Founded a financial literacy platform that certified 5,500+ learners. UN V-Award 2022.'),
    ('watchbot', 'WatchBOT', 'Founded a computer vision startup for classroom attention. US$20k raised, piloted in 3 schools.'),
    ('star', 'AP Scholar with Distinction', '5/5 in Calculus BC, Statistics and Physics C. Merit, Indian Olympiad Qualifier in Maths.'),
    ('note', 'Off the keyboard', 'Guitar, RSL Grade 8 Merit. Tennis for Imperial and for Haryana in AITA tournaments.'),
]

STACK = [
    ('LANGUAGES', 'py,c,ts,scala,haskell,java,kotlin,ruby,bash'),
    ('ML · SYSTEMS · WEB', 'pytorch,tensorflow,react,nextjs,nodejs,postgres,redis,docker,gcp,linux,git'),
]

SIDE = ('glyph:target', 'Focus-Mode', 'My own macOS focus timer and site blocker, with lock-in modes and a Chrome extension.',
        'https://github.com/aryan-the-jain/Focus-Mode')

# "Year in work" heatmap. Days with public GitHub contributions use the real
# counts from tools/cache/contributions.json (run tools/fetch_github.py). Private
# work that GitHub can't see (Sarvam, Imperial GitLab, Bending Spoons) is estimated
# from these periods: (start, end, weekday intensity 0-1, weekend intensity 0-1, label).
YEAR_START = (2025, 7, 1)
YEAR_END = (2026, 10, 9)
YEAR_PERIODS = [
    ((2025, 7, 7), (2025, 9, 26), 0.86, 0.3),      # Sarvam
    ((2025, 10, 6), (2025, 10, 12), 0.45, 0.2),    # term 1, week 1
    ((2025, 10, 13), (2025, 12, 12), 0.84, 0.22),  # PintOS, five days a week
    ((2025, 12, 13), (2026, 1, 9), 0.15, 0.1),     # winter break
    ((2026, 1, 10), (2026, 3, 20), 0.94, 0.25),    # WACC, five days a week
    ((2026, 3, 21), (2026, 4, 26), 0.28, 0.18),    # Easter
    ((2026, 4, 27), (2026, 6, 20), 0.5, 0.25),     # term 3
    ((2026, 6, 21), (2026, 7, 5), 0.25, 0.15),
    ((2026, 7, 6), (2026, 9, 30), 0.96, 0.3),      # Harvest
]

# Parallel tracks drawn under the commit grid, on the same time axis.
# (lane, [(start, end or None for ongoing, label)])
YEAR_LANES = [
    ('WORK', [((2025, 7, 7), (2025, 9, 26), 'Sarvam AI'), ((2026, 7, 6), (2026, 9, 30), 'Harvest @ Bending Spoons')]),
    ('UNI PROJECTS', [((2025, 10, 13), (2025, 12, 12), 'PintOS kernel'), ((2026, 1, 12), (2026, 3, 20), 'WACC compiler'),
                      ((2026, 5, 25), (2026, 6, 19), 'Alongside')]),
    ('COURSEWORK', [((2025, 10, 6), (2025, 12, 12), 'Term 1'), ((2026, 1, 10), (2026, 3, 20), 'Term 2'),
                    ((2026, 4, 27), (2026, 6, 20), 'Term 3')]),
    ('SIDE PROJECTS', [((2025, 11, 1), (2026, 1, 5), 'EQIP'), ((2026, 1, 12), (2026, 2, 28), 'P2P energy trading'),
                       ((2026, 10, 4), None, 'Focus-Mode')]),
    ('RESEARCH', [((2026, 1, 5), None, 'Stealth startup · multi-agent governance')]),
    ('LEADERSHIP', [((2025, 7, 1), None, 'Google Developer Groups lead · AI Society')]),
]
# Weekly coursework on GitLab during term, on top of the big projects.
YEAR_TERMS = [((2025, 10, 6), (2025, 12, 12)), ((2026, 1, 10), (2026, 3, 20)), ((2026, 4, 27), (2026, 6, 20))]
YEAR_COURSEWORK = 0.25
YEAR_BACKGROUND = 0.06  # side projects and part-time research outside the main blocks
