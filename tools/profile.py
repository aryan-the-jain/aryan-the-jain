"""Everything the profile graphics say. Edit this, then run `python tools/build.py`."""

NAME = 'Aryan Jain'
KICKER = 'RESEARCH ENGINEER  ·  IMPERIAL COLLEGE LONDON'
TAGLINE = 'Building reliable AI systems across machine learning, systems and distributed infrastructure.'
CHIPS = ['M.ENG COMPUTING · AI & ML', 'FIRST-CLASS', 'LONDON']

NOW = (2026, 10)  # the "now" line on the timeline

# (logo file or glyph, organisation, role, start (y, m), end (y, m) or None for ongoing, kind)
EXPERIENCE = [
    ('bending-spoons', 'Bending Spoons · Harvest', 'Software Engineering Intern', (2026, 7), (2026, 10), 'work'),
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
    'subtitle': 'SOFTWARE ENGINEERING INTERN  ·  JUL–OCT 2026',
    'stats': [
        ('115', 'merged PRs', 'in 13 weeks'),
        ('#1', 'contributor', 'on the team this quarter'),
        ('6.7×', 'faster assignment page', '2.7s → 0.4s'),
        ('$5M', 'ARR product rebuilt', 'natively inside Harvest'),
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
