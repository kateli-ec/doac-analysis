"""Page 11: Production & Visual Style Analysis."""

import os

import json
import re

import streamlit as st
import pandas as pd

from components.metrics import format_number
RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

st.set_page_config(page_title="Production Style", layout="wide")
st.title("Production & Visual Style Analysis")

st.markdown("""
How a podcast *looks* shapes how it *feels*. The set, lighting, camera angles, wardrobe, and
visible equipment all signal what kind of conversation the viewer is about to experience. This
analysis is based on actual video frames (not thumbnails) from 5 recent long-form episodes per channel.
""")

# Load manifest and competitor data
manifest_path = os.path.join(RAW_DIR, "full_manifest.json")
comp_path = os.path.join(RAW_DIR, "competitors_expanded.json")

if not os.path.exists(manifest_path):
    st.error("Frame data not found. Run production analysis collection first.")
    st.stop()

with open(manifest_path) as f:
    manifest = json.load(f)

comp_data = {}
if os.path.exists(comp_path):
    with open(comp_path) as f:
        comp_data = json.load(f)

# Production analysis data for each channel
PRODUCTION = {
    "The Diary Of A CEO": {
        "set": "Dark, moody living room. Bookshelves with warm lamp lighting behind host. Guest sits at a dark wooden desk/table. Minimal props. Dark walls with subtle texture.",
        "camera": "Multiple cameras. Host gets medium close-up facing camera. Guest gets tighter close-up, slightly angled. Switching between host, guest, and occasional two-shot.",
        "lighting": "Low-key, cinematic. Warm accent lights on bookshelves. Subject lit from front, background deliberately darker. Dramatic contrast.",
        "equipment": "No mics visible in frame. No headphones. Clean frame gives impression of intimate conversation, not a 'show'.",
        "wardrobe": "Steven Bartlett: consistently black t-shirt. Minimal jewelry. Clean, understated.",
        "vibe": "Intimate, premium, cinematic",
        "vibe_detail": "Feels like a Netflix documentary interview. The darkness creates a confessional atmosphere where guests open up.",
        "key_elements": "Dark background, bookshelf with warm lamps, no visible equipment, black wardrobe, high production value",
    },
    "Joe Rogan (PowerfulJRE)": {
        "set": "Custom studio in Austin, TX. Wooden walls, large neon 'Joe Rogan Experience' sign behind host. Heavy wooden table cluttered with drinks, supplements, random objects.",
        "camera": "Multiple cameras. Wide shot shows full studio. Individual medium shots for host and guest across the table.",
        "lighting": "Full, even lighting. Well-lit faces. Red/maroon velvet curtain behind guest. Warm wood tones throughout.",
        "equipment": "Prominently visible: large podcast mics on boom arms, over-ear headphones on both host and guest. Unapologetically a studio.",
        "wardrobe": "Joe Rogan: casual graphic t-shirts (brand tees), no blazers. Guests dress however they want.",
        "vibe": "Masculine, casual hangout",
        "vibe_detail": "Feels like a man cave. The cluttered table (coffee, whiskey, random objects) makes it lived-in. The neon sign is branded but not corporate.",
        "key_elements": "Neon branded sign, wooden walls, visible mics + headphones, cluttered table, red curtain for guests",
    },
    "Andrew Huberman": {
        "set": "Minimalist studio with dark gray acoustic panels. Small table with mic and coffee mug. Very clean, almost clinical.",
        "camera": "Single or dual camera. Medium close-up for solo episodes (host faces camera). For interviews: separate camera on guest with same minimal background.",
        "lighting": "Even, neutral. Not dramatic like DOAC, not warm like Rogan. Functional and clean.",
        "equipment": "Podcast mic on table visible. No headphones. Papers/pen often visible on Huberman (signals preparation). Coffee mug as only prop.",
        "wardrobe": "Always black. Black t-shirt or long sleeve. No branding, no color. Consistent across every episode.",
        "vibe": "Scientific, focused, serious",
        "vibe_detail": "The minimalism says 'this is about information, not aesthetics.' All-black wardrobe reinforces authority without flash.",
        "key_elements": "Gray acoustic panels, all-black wardrobe, papers/pen visible, minimal props, scientific authority",
    },
    "Lex Fridman": {
        "set": "Very dark, almost entirely black background. No set decoration. Just two people in darkness. Solo segments use text overlays.",
        "camera": "Tight close-ups with shallow depth of field. Solo segments: Lex faces camera with episode number overlay.",
        "lighting": "Extremely low-key. Single key light on face, everything else black. Most dramatic lighting of any channel.",
        "equipment": "Mic visible but understated. No headphones. Darkness hides everything except faces.",
        "wardrobe": "Often black, sometimes intellectual graphic t-shirts ('Forever Jung'). Casual but deliberately nerdy.",
        "vibe": "Intense, philosophical, intimate",
        "vibe_detail": "Feels like a late-night deep conversation. No distractions. Viewer forced to focus entirely on words and faces.",
        "key_elements": "Near-total darkness, dramatic single-source lighting, extreme close-ups, intellectual t-shirts",
    },
    "Chris Williamson": {
        "set": "Warm, upscale living room. Stained glass window behind seating. Plants, sculptures, decorative objects. Wooden furniture, warm tones. 'MW' watermark.",
        "camera": "Multiple cameras. Medium shots with background visible. Camera at slight angle, not straight-on. Close-ups during key moments.",
        "lighting": "Warm, ambient. Stained glass creates colorful light. Accent lights on decorative objects.",
        "equipment": "Mics visible on table but not prominent. No headphones. Drinks on table.",
        "wardrobe": "Semi-formal: blazer with no tie, button-down shirt. Clean-cut. Guests often match formality level.",
        "vibe": "Intellectual lounge",
        "vibe_detail": "Feels like a high-end club or library. Stained glass and plants give warmth. More curated than Rogan, less cinematic than DOAC.",
        "key_elements": "Stained glass window, plants, sculptures, warm lighting, blazer wardrobe, MW branding",
    },
    "Relentless": {
        "set": "Architectural, industrial-elegant. Ornate wooden paneling, decorative tile/glass partition. Looks like a converted historic building. No desk between host and guest.",
        "camera": "5 frames: wide two-shot, individual portraits, full-body shots. Slightly off-center angles. 'Relentless' watermark lower-right.",
        "lighting": "Natural and warm. Even lighting without dramatic shadows. Architectural details provide visual interest.",
        "equipment": "No visible mics or headphones in many shots. Lavalier mics likely. Very clean frames.",
        "wardrobe": "Ti Morse: casual, dark/black. Guests wear startup-casual (polos, bomber jackets, t-shirts).",
        "vibe": "Natural conversation between founders",
        "vibe_detail": "Historic/architectural set gives gravitas without corporate feel. Lack of visible equipment reinforces 'just two people talking.'",
        "key_elements": "Architectural paneling, tile/glass partition, no visible mics, 5 camera angles, startup-casual, historic building",
    },
    "Dwarkesh Patel": {
        "set": "Home library/study. Bookshelves filled with books behind guest. Wooden table with coffee mugs and papers. Plants visible. Warm, residential.",
        "camera": "Split-screen for remote guests. In-person: medium shots with bookshelf background. Text overlays during solo segments.",
        "lighting": "Natural/warm. Not studio-grade. Feels like someone's actual home office.",
        "equipment": "Minimal. Lavalier mics. Papers and coffee on table.",
        "wardrobe": "Casual: sweaters, henley shirts, neutral colors. Intellectual-casual.",
        "vibe": "Academic fireside chat",
        "vibe_detail": "Feels like visiting a professor's office. Bookshelves and residential setting signal intellectual depth over production polish.",
        "key_elements": "Bookshelves, wooden table, coffee mugs, residential, split-screen remote, academic vibe",
    },
    "Patrick Bet-David (Valuetainment)": {
        "set": "Corporate studio. Large 'PBD' branded backdrop. Monitors/screens visible. Desk with laptop. News desk aesthetic.",
        "camera": "Multiple cameras. Host straight-on with branded backdrop. Guests get own camera. News-style production.",
        "lighting": "Full, bright, even. No shadows. Everything lit for clarity, like a TV news set.",
        "equipment": "Mics, headphones, laptop, screens all visible. This is a production and wants you to know it.",
        "wardrobe": "Suit and tie or dress shirt. Always formal. Signals business authority.",
        "vibe": "Business news show",
        "vibe_detail": "Feels like Fox Business or CNBC more than a podcast. Branding prominent, formality deliberate.",
        "key_elements": "Giant PBD branding, suit wardrobe, news desk, full bright lighting, visible monitors, corporate",
    },
    "Tom Bilyeu (Impact Theory)": {
        "set": "Dark, modern studio. Teal/cyan LED accent lighting in geometric shapes. Chess piece sculpture visible. Dark walls, sleek aesthetic.",
        "camera": "Multiple cameras. Dynamic: dramatic zooms, graphics overlays, text callouts. More produced editing than most podcasts.",
        "lighting": "Dark with colored LED accents (teal/cyan). Face well-lit against dark background. High contrast.",
        "equipment": "Varies. The production uses more post-production overlays (graphics, statistics on screen) than competitors.",
        "wardrobe": "All black. Always black t-shirt or top. Glasses. Consistent personal brand.",
        "vibe": "High-energy, motivational, modern",
        "vibe_detail": "LED accents and chess piece signal ambition and strategy. Dark+neon feels like a tech startup or gaming channel.",
        "key_elements": "Teal LED accents, chess piece sculpture, dark studio, all-black wardrobe, on-screen graphics",
    },
    "Lewis Howes": {
        "set": "Warm, modern living room. Dark walls with red neon 'Greatness' sign (branded). Books and objects on shelves. Comfortable seating.",
        "camera": "Multiple cameras. Medium close-ups, slight angle. Host side branded with neon sign.",
        "lighting": "Warm, even. Well-lit faces. Background has warm accent lighting.",
        "equipment": "Mics visible but not dominant. No headphones.",
        "wardrobe": "Dark polo or button-down. Polished but not formal. Athletic build visible.",
        "vibe": "Aspirational living room",
        "vibe_detail": "Feels like coffee with a successful friend. Neon sign branded but warm. Comfortable, motivational.",
        "key_elements": "Red 'Greatness' neon sign, dark walls, warm lighting, polo wardrobe, motivational",
    },
    "Rich Roll": {
        "set": "Dark, minimal studio. Black background. Small table between host and guest. Very simple.",
        "camera": "Multiple cameras. Individual medium shots for host and guest against dark backgrounds.",
        "lighting": "Low-key. Faces lit, background dark. Similar to Lex but slightly warmer.",
        "equipment": "Podcast mics visible on table. No headphones. Water bottle visible.",
        "wardrobe": "Casual: black t-shirt, glasses. Simple, no-frills.",
        "vibe": "Serious, focused, no distractions",
        "vibe_detail": "Darkness removes all visual noise. Pure conversation. Less intense than Lex, less cinematic than DOAC.",
        "key_elements": "Black background, minimal setup, visible mics, casual all-black wardrobe",
    },
    "Jay Shetty Podcast": {
        "set": "Warm library/study. Dark wood bookshelves. Couch or comfortable chairs. 'On Purpose' branding on mic. Candles or subtle decor.",
        "camera": "Multiple cameras. Medium shots with background visible. Close-ups during emotional moments.",
        "lighting": "Warm, soft. Intimate, cozy feel. Background slightly darker than subjects.",
        "equipment": "Branded podcast mic visible ('On Purpose'). No headphones.",
        "wardrobe": "Minimalist, earth tones or black. Clean, spiritual-aesthetic.",
        "vibe": "Warm, spiritual, intimate",
        "vibe_detail": "Feels like a therapy session or deep conversation with a wise friend. Bookshelves and warm lighting create 'wisdom' atmosphere.",
        "key_elements": "Wood bookshelves, branded mic, warm candle-like lighting, earth-tone wardrobe, spiritual atmosphere",
    },
    "Dr Rangan Chatterjee": {
        "set": "Bright, natural. Converted garden room or conservatory feel. Light wood paneling, teal/green accent wall. Personal photos on shelves.",
        "camera": "Standard dual camera. Individual shots for host and guest. Natural framing.",
        "lighting": "Bright, natural daylight feel. High key. Opposite of DOAC/Lex dark approach.",
        "equipment": "Mic on boom arm visible. 'Feel Better Live More' branding. Casual, functional.",
        "wardrobe": "Smart casual. Scarf sometimes. Approachable, not clinical despite being a doctor.",
        "vibe": "Friendly consultation room",
        "vibe_detail": "Bright, natural setting feels health-positive and optimistic. Personal touches make it warm and human.",
        "key_elements": "Bright natural light, teal/green wall, wood paneling, personal photos, health-optimistic",
    },
    "Tim Ferriss": {
        "set": "Warm, decorated studio. Wood shelving with eclectic objects (globe, clapperboard, star, bust sculpture). Comfortable chair seating.",
        "camera": "Multiple cameras. Medium shots. Background objects provide visual interest.",
        "lighting": "Warm, even, well-produced. Golden tones. Background objects lit with accent lights.",
        "equipment": "Mic visible. Professional but personal, like a well-appointed office.",
        "wardrobe": "Glasses, clean casual. Sometimes button-down. Approachable nerd aesthetic.",
        "vibe": "Eclectic intellectual den",
        "vibe_detail": "Curated objects (globe, clapperboard, bust) signal worldliness and creativity. Renaissance man's study.",
        "key_elements": "Eclectic shelf objects, globe, warm golden lighting, comfortable chairs, intellectual-creative",
    },
    "Jordan Peterson": {
        "set": "Varies: lecture hall (white backdrop, podium), studio interviews, or remote. Lecture format uses all-white minimalist stage.",
        "camera": "Multiple cameras for lectures (wide + close-up). Interview format uses standard dual camera.",
        "lighting": "Lectures: dramatic, theatrical. Single spotlight against white. Interviews: warmer, conventional.",
        "equipment": "Lectures: podium/lectern visible. Interviews: varies by location.",
        "wardrobe": "Formal: suit jacket (often tweed or plaid), dress shirt. Most formally dressed host in the set.",
        "vibe": "Academic authority",
        "vibe_detail": "Suit + lecture format signals 'professor.' Even in interviews, formality positions Peterson as authority figure.",
        "key_elements": "Suit wardrobe (tweed/plaid), lecture format, white stage, academic authority, theatrical lighting",
    },
    "Farzad": {
        "set": "Home music studio/office. Guitars and instruments hanging on wall. Monitors/screens in background. Personal, lived-in creative space.",
        "camera": "Single camera facing host directly. Medium close-up. Mostly solo commentary format.",
        "lighting": "Cool-toned, even. Slightly blue/gray ambient. Not heavily produced.",
        "equipment": "Podcast mic visible on boom arm. Home studio equipment in background.",
        "wardrobe": "Casual: graphic t-shirts. Relaxed, authentic.",
        "vibe": "Tech-savvy creator's garage",
        "vibe_detail": "Guitars + monitors signal a creative, multi-talented person. Feels like hanging out in a friend's music studio talking about finance.",
        "key_elements": "Guitars on wall, monitors, home studio, graphic tees, cool blue tones, creator vibe",
    },
    "Newcomer Pod": {
        "set": "Polished podcast studio. Dark blue paneled walls, plants, shelving with objects. In-person interviews at a table.",
        "camera": "Multiple cameras. Medium shots with background visible. Professional framing.",
        "lighting": "Warm, well-lit. Professional quality similar to larger channels.",
        "equipment": "Podcast mics visible on boom arms. Professional setup.",
        "wardrobe": "Guests dress casually (tech casual). Host: casual.",
        "vibe": "Professional tech journalism",
        "vibe_detail": "Well-produced for its size. The dark blue panels and plants create a polished but relaxed feel.",
        "key_elements": "Dark blue panels, plants, professional mics, tech-casual wardrobe, journalism feel",
    },
    "Silicon Valley Girl": {
        "set": "Varies: outdoor locations, offices, coffee shops. Split-screen for remote interviews. Not studio-bound.",
        "camera": "Split-screen for remote guests (side-by-side). In-person: handheld or steady-cam feel. More documentary than studio.",
        "lighting": "Natural daylight in outdoor/office settings. Variable quality.",
        "equipment": "Lavalier mics. Minimal visible equipment.",
        "wardrobe": "Fashion-forward, stylish. Colorful, trendy. Very different from the all-black podcast norm.",
        "vibe": "Lifestyle meets tech",
        "vibe_detail": "Feels like a vlog-interview hybrid. Location shooting gives energy. Fashion-forward wardrobe stands out in the podcast space.",
        "key_elements": "Location shooting, split-screen, fashion-forward wardrobe, natural light, vlog-interview hybrid",
    },
    "Norges Bank Investment Mgmt": {
        "set": "Corporate/institutional. Clean, branded intros. Professional studio or office settings.",
        "camera": "Standard corporate video production. Clean framing.",
        "lighting": "Even, professional. Institutional quality.",
        "equipment": "Minimal visible. Lavalier mics.",
        "wardrobe": "Business professional. Suits and dress shirts.",
        "vibe": "Institutional, authoritative",
        "vibe_detail": "This is sovereign wealth fund content. It looks and feels like corporate communications, not casual podcasting.",
        "key_elements": "Corporate branding, professional lighting, business attire, institutional tone",
    },
    "Sammi Cohen Talks": {
        "set": "Warm, cozy room. Bookshelves with decorative objects. Green curtain accent. Plants. 'Social Currency' branding on mic.",
        "camera": "Standard dual camera setup. Medium shots with warm background.",
        "lighting": "Warm, inviting. Well-lit but not harsh.",
        "equipment": "Branded mic visible. Clean setup.",
        "wardrobe": "Casual, colorful (yellow cardigan in one episode). Friendly, approachable.",
        "vibe": "Warm, friendly, approachable",
        "vibe_detail": "Feels like a cozy catch-up with a friend. The colored wardrobe and green curtain give personality.",
        "key_elements": "Bookshelves, green curtain, branded mic, plants, colorful wardrobe, cozy feel",
    },
    "Jocko Willink": {
        "set": "Dark, minimal studio. Very low lighting. Mics and equipment visible. No decoration. Sparse, military-functional.",
        "camera": "Multiple cameras. Over-the-shoulder shots. @handles displayed on screen for host and co-host.",
        "lighting": "Very dark, dramatic. Single source illuminating faces. Shadows everywhere.",
        "equipment": "Large mics visible. Headphones on both host and guest. Equipment is part of the aesthetic.",
        "wardrobe": "Dark t-shirts (often branded: 'Jocko Fuel'). Military-casual. Muscular build visible.",
        "vibe": "Disciplined, military, intense",
        "vibe_detail": "Darkness and spartan setup mirror the discipline/military ethos. No comfort, no decoration. Pure function.",
        "key_elements": "Very dark, minimal, visible mics + headphones, military-casual, Jocko Fuel branding, intense",
    },
    "Alex Hormozi": {
        "set": "Modern studio with Acquisition.com branding. Split-screen format for interviews. White boards/screens behind guest with data/numbers visible.",
        "camera": "Split-screen showing both host and guest. Clean professional framing.",
        "lighting": "Even, well-lit. Professional quality.",
        "equipment": "Minimal visible. Clean production.",
        "wardrobe": "Casual: flannel shirts, caps. Rugged entrepreneur look.",
        "vibe": "Business operator, no-nonsense",
        "vibe_detail": "Data/numbers visible on screen reinforces the quantitative, ROI-focused content. Split-screen keeps both parties visible.",
        "key_elements": "Acquisition.com branding, split-screen, data on screen, casual-rugged wardrobe, business focus",
    },
    "Armchair Expert with Dax Shepard": {
        "set": "Eclectic, cluttered attic/garage feel. Shelves full of toys, memorabilia, funko pops, globe. Green walls. Lived-in and personal.",
        "camera": "Multiple cameras. Wide shots showing the cluttered environment. Medium close-ups for conversation.",
        "lighting": "Warm, slightly dim. Accent lights on shelves. Cozy, garage-hangout lighting.",
        "equipment": "Mics visible on boom arms. Casual setup visible.",
        "wardrobe": "Very casual: baseball cap, t-shirt, denim. Celebrity-casual.",
        "vibe": "Celebrity garage hangout",
        "vibe_detail": "The clutter and memorabilia create character. Feels like hanging out in a cool friend's attic. Intentionally not polished.",
        "key_elements": "Cluttered shelves, toys/memorabilia, green walls, globe, baseball cap, garage vibe",
    },
    "Bryce Crawford Podcast": {
        "set": "Warm, rustic home studio. Wooden shelf/beam visible. Books, colorful cans (branded?), couch seating. Cozy, cabin-like.",
        "camera": "Standard dual camera. Medium shots.",
        "lighting": "Warm, natural. Soft light, inviting.",
        "equipment": "Mics visible on boom arms.",
        "wardrobe": "Very casual: trucker cap, layered jacket, bright undershirt. Outdoorsy-casual.",
        "vibe": "Casual fireside chat",
        "vibe_detail": "Rustic, cozy setting with a young-creator energy. Feels approachable and unpretentious.",
        "key_elements": "Rustic wood, couch seating, trucker cap, cabin-like warmth, casual energy",
    },
    "The Jordan Harbinger Show": {
        "set": "Studio with purple/magenta accent wall or lighting. Branded mic cube visible. Modern, polished.",
        "camera": "Multiple cameras. Close-up shots with branded elements visible.",
        "lighting": "Colorful accent (purple/magenta). Well-lit face against colored background.",
        "equipment": "Branded mic visible (show name on mic flag). Pop filter visible.",
        "wardrobe": "Casual: t-shirt or polo. Clean-cut.",
        "vibe": "Polished, branded podcast studio",
        "vibe_detail": "Professional studio with distinctive purple branding. Signals established, serious podcast.",
        "key_elements": "Purple/magenta accent, branded mic, polished studio, clean wardrobe",
    },
    "Johnathan Bi": {
        "set": "Dark, academic. Boxes/shelving in background (looks like a storage area or unfinished space). Very raw, unpolished.",
        "camera": "Single camera. Close-up on host. Simple framing.",
        "lighting": "Dark, minimal. Functional lighting.",
        "equipment": "Minimal visible.",
        "wardrobe": "Formal: tweed blazer, dress shirt. Academic-formal despite the raw set. Deliberate contrast.",
        "vibe": "Underground academic lecture",
        "vibe_detail": "The raw space + formal wardrobe creates an interesting tension. Feels like an intellectual who doesn't care about aesthetics.",
        "key_elements": "Dark raw space, tweed blazer, academic-formal wardrobe, minimal production, intellectual",
    },
    "Kevin Rose": {
        "set": "Minimal, plain background. Simple setup. Clean but not decorated.",
        "camera": "Single or dual camera. Medium shots. Straightforward framing.",
        "lighting": "Even, functional.",
        "equipment": "Pen/notepad visible. Minimal mic setup.",
        "wardrobe": "Casual: black t-shirt, baseball cap. Tech-casual.",
        "vibe": "Low-key tech insider",
        "vibe_detail": "No frills. The simplicity says the content matters, not the set. Tech legend who doesn't need visual production.",
        "key_elements": "Plain background, baseball cap, minimal setup, tech-casual, content-focused",
    },
    "Robinson Erhardt": {
        "set": "Remote/Zoom setup. Living room visible with art, paintings, couch, bookshelves. Split-screen with guest in their own home.",
        "camera": "Webcam quality. Split-screen Zoom recording.",
        "lighting": "Natural daylight. Variable quality. Not studio-produced.",
        "equipment": "No professional equipment visible. Standard webcam/computer setup.",
        "wardrobe": "Very casual: yellow t-shirt, green beanie/cap. Unconventional, artistic.",
        "vibe": "Intellectual Zoom call",
        "vibe_detail": "Feels like overhearing two professors on a video call. Zero production value, 100% content value. Paintings on wall add personality.",
        "key_elements": "Zoom/remote setup, art on walls, very casual wardrobe, zero production, pure content",
    },
    "What Bitcoin Did": {
        "set": "Home office. Plain white walls. Office furniture visible in background. Headphones on. Very casual/amateur setup.",
        "camera": "Webcam. Single frame on host. Remote guests via Zoom.",
        "lighting": "Even, room lighting. Not studio-produced.",
        "equipment": "Large over-ear headphones visible. 'What Bitcoin Did' branded overlay on video.",
        "wardrobe": "Very casual: navy t-shirt. Relaxed.",
        "vibe": "Home office podcast",
        "vibe_detail": "Proudly low-production. The content (Bitcoin analysis) carries the show, not the visuals.",
        "key_elements": "Home office, headphones, branded overlay, webcam quality, content-first",
    },
    "Machine Learning Street Talk": {
        "set": "Home/office setting. Natural background with window visible. Clean but not decorated.",
        "camera": "Close-up on host/guest. In-person interviews in office-like settings.",
        "lighting": "Natural, variable. Not studio-controlled.",
        "equipment": "Minimal visible. Professional audio quality despite simple visual setup.",
        "wardrobe": "Casual: cap, glasses, dark shirt. Tech-casual.",
        "vibe": "Tech office conversation",
        "vibe_detail": "Feels like a conversation at an ML conference or tech office. Visual simplicity lets the technical content lead.",
        "key_elements": "Office setting, natural light, cap + glasses, tech-casual, content-focused",
    },
    "The Investors Podcast Network": {
        "set": "Remote/Zoom format. Split-screen showing host and guest in their home offices. Bookshelves common in backgrounds.",
        "camera": "Webcam. Split-screen.",
        "lighting": "Natural, variable per participant.",
        "equipment": "Mics visible for some hosts. Standard remote podcast setup.",
        "wardrobe": "Smart casual to casual.",
        "vibe": "Professional remote podcast",
        "vibe_detail": "Standard Zoom podcast format. Bookshelves in backgrounds signal finance/investing credibility.",
        "key_elements": "Remote/Zoom, split-screen, bookshelves, variable quality, investing credibility",
    },
    "Unsupervised Learning (Redpoint)": {
        "set": "Warm, cozy studio. Wooden table, shelving with decorative objects (plants, small figurines). Coffee mugs. Warm tones.",
        "camera": "Multiple cameras. Medium two-shot showing both host and guest at table. Individual close-ups.",
        "lighting": "Warm, inviting. Well-lit for its size. Above-average production for a sub-25K channel.",
        "equipment": "Mics visible. Text overlay captions on screen ('Coming up:' teasers).",
        "wardrobe": "Casual: dark shirts, graphic tees. VC-casual.",
        "vibe": "Venture capital fireside",
        "vibe_detail": "Surprisingly polished for its subscriber count. Feels like a VC firm's in-house content studio.",
        "key_elements": "Warm wood table, decorative shelves, coffee mugs, text overlays, above-average production for size",
    },
    "TechTechPotato": {
        "set": "Event/conference stage setting. Blue/purple LED backdrop with tech branding. Two chairs facing each other on stage.",
        "camera": "Multiple cameras. Wide stage shot + individual close-ups.",
        "lighting": "Professional stage lighting. Blue/purple LED wash.",
        "equipment": "Lavalier mics. Stage setup with professional audio.",
        "wardrobe": "Smart casual: blazer. Both host and guest in semi-formal tech conference attire.",
        "vibe": "Tech conference interview",
        "vibe_detail": "Looks like it's filmed at industry events. The stage setting adds scale and professionalism beyond what a 143K channel usually has.",
        "key_elements": "Conference stage, blue/purple LED backdrop, blazers, professional staging, event-feel",
    },
    "The Origins Podcast": {
        "set": "Home study/library with bookshelves. Multiple people visible at desks with mics. Cluttered, academic office feel.",
        "camera": "Multiple cameras showing panelists. Collage/montage-style intro.",
        "lighting": "Warm, functional. Standard room lighting.",
        "equipment": "Large mics on stands visible. Headphones on some participants.",
        "wardrobe": "Academic casual: sweaters, collared shirts.",
        "vibe": "Academic panel discussion",
        "vibe_detail": "Feels like a university seminar being recorded. Multiple speakers, bookshelves, visible mics create a scholarly atmosphere.",
        "key_elements": "Bookshelves, multiple panelists, visible mics/headphones, academic casual, scholarly",
    },
    "Around The Coin": {
        "set": "Branded intro graphics. Guest headshots with geometric branded frames. No studio visible in intros.",
        "camera": "Standard remote interview format.",
        "lighting": "Variable (remote guests).",
        "equipment": "Branded overlays and graphics.",
        "wardrobe": "Variable.",
        "vibe": "Branded remote podcast",
        "vibe_detail": "Heavy on graphic branding (intro cards, geometric frames). No studio identity beyond the brand graphics.",
        "key_elements": "Branded intro graphics, geometric frames, remote format, no studio",
    },
    "Prime Movers Lab": {
        "set": "Remote/Zoom. Split-screen with host and guest in home offices. Bookshelves behind host.",
        "camera": "Webcam. Split-screen Zoom.",
        "lighting": "Natural, variable.",
        "equipment": "Standard webcam setup.",
        "wardrobe": "Smart casual.",
        "vibe": "VC office call",
        "vibe_detail": "Standard remote podcast. Bookshelves signal credibility. No distinctive visual identity.",
        "key_elements": "Remote/Zoom, bookshelves, basic production, VC-standard",
    },
    "Rational VC Podcast": {
        "set": "Audio-only with static branded image. No video of hosts/guests visible.",
        "camera": "No video cameras. Static branded card shown throughout.",
        "lighting": "N/A (audio-only on YouTube).",
        "equipment": "Audio-only. Podcast logos and Spotify/Apple icons displayed.",
        "wardrobe": "N/A.",
        "vibe": "Audio podcast uploaded to YouTube",
        "vibe_detail": "No video production. This is an audio podcast repurposed for YouTube. Static image throughout.",
        "key_elements": "Audio-only, static branded image, no video production, podcast platform logos",
    },
    "TWIML AI Podcast": {
        "set": "Branded intro with digital/tech-themed graphics (blue wave patterns). Guest headshots with name/title overlay.",
        "camera": "Standard remote format after intro.",
        "lighting": "N/A (mostly remote/graphic-heavy).",
        "equipment": "Remote setup.",
        "wardrobe": "Academic/professional.",
        "vibe": "Professional AI conference podcast",
        "vibe_detail": "Polished branded intros with guest credentials. Signals professionalism despite small size.",
        "key_elements": "Blue tech-themed graphics, guest headshots, branded intros, conference podcast feel",
    },
}

# ---- Section 1: Production Breakdown by Channel ----
st.header("Production Breakdown by Channel")

for channel_name, prod in PRODUCTION.items():
    cd = comp_data.get(channel_name, {})
    subs = cd.get("subscriber_count", 0)
    vids_data = manifest.get(channel_name, [])

    with st.expander(f"**{channel_name}** ({format_number(subs)} subs) \u2014 {prod['vibe']}"):
        # Video stats table
        if vids_data:
            vid_rows = []
            for v in vids_data:
                vid_rows.append({
                    "Title": v["title"][:55],
                    "Views": f"{v['views']:,}",
                    "Likes": f"{v['likes']:,}",
                    "Duration": v["duration"],
                    "Published": v["published"],
                    "Link": v["url"],
                })
            vid_df = pd.DataFrame(vid_rows)
            st.dataframe(vid_df, use_container_width=True, hide_index=True,
                         column_config={"Link": st.column_config.LinkColumn("Link", display_text="Watch")})

        # Images available in the full mood board
        st.caption("[View full visual mood board with frames](https://kateli-ec.github.io/doac-analysis/mood_board.html)")

        # Production details
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Set:** {prod['set']}")
            st.markdown(f"**Camera:** {prod['camera']}")
            st.markdown(f"**Lighting:** {prod['lighting']}")
        with col2:
            st.markdown(f"**Equipment Visible:** {prod['equipment']}")
            st.markdown(f"**Host Wardrobe:** {prod['wardrobe']}")
            st.markdown(f"**Overall Vibe:** {prod['vibe_detail']}")
        st.caption(f"Key elements: {prod['key_elements']}")

st.markdown("---")

# ---- Section 2: Side-by-Side Comparison ----
st.header("Side-by-Side Comparison")

comp_rows = []
for channel_name, prod in PRODUCTION.items():
    cd = comp_data.get(channel_name, {})
    subs = cd.get("subscriber_count", 0)
    created = cd.get("created_at", "")
    age = round((pd.Timestamp("2026-04-10") - pd.Timestamp(created)).days / 365.25, 1) if created else 0

    lighting = "Dark/moody" if any(w in prod["lighting"].lower() for w in ["low-key", "dark", "dramatic", "cinematic", "extremely"]) else \
               "Bright/natural" if any(w in prod["lighting"].lower() for w in ["bright", "natural", "high key", "daylight"]) else "Warm/even"

    mics = "No" if any(w in prod["equipment"].lower() for w in ["no mic", "no visible", "lavalier", "minimal"]) else "Yes"
    headphones = "Yes" if "headphone" in prod["equipment"].lower() else "No"

    wardrobe_cat = "All black" if "black" in prod["wardrobe"].lower() and "blazer" not in prod["wardrobe"].lower() and "suit" not in prod["wardrobe"].lower() else \
                   "Formal" if any(w in prod["wardrobe"].lower() for w in ["suit", "blazer", "formal", "tweed", "dress shirt"]) else \
                   "Semi-formal" if any(w in prod["wardrobe"].lower() for w in ["polo", "button-down", "smart"]) else "Casual"

    branded = "Yes" if any(w in (prod["set"] + prod["key_elements"]).lower() for w in ["neon", "branded", "pbd", " mw ", "branding", "on purpose"]) else "No"

    format_type = "Remote/Zoom" if any(w in prod["camera"].lower() for w in ["zoom", "webcam", "remote", "split-screen"]) else \
                  "In-person studio" if any(w in prod["set"].lower() for w in ["studio", "room", "office", "library"]) else \
                  "Location/varies"

    comp_rows.append({
        "Channel": channel_name,
        "Subscribers": subs,
        "Age (yrs)": age,
        "Format": format_type,
        "Lighting": lighting,
        "Mics Visible": mics,
        "Headphones": headphones,
        "Wardrobe": wardrobe_cat,
        "Branded Set": branded,
        "Background": prod["set"].split(".")[0][:40],
        "Vibe": prod["vibe"],
    })

comp_df = pd.DataFrame(comp_rows).sort_values("Subscribers", ascending=False)
st.dataframe(comp_df, use_container_width=True, hide_index=True,
             column_config={"Subscribers": st.column_config.NumberColumn(format="%,d")})

st.markdown("---")

# ---- Section 3: Patterns ----
st.header("Production Patterns & Insights")

n_dark = sum(1 for r in comp_rows if r["Lighting"] == "Dark/moody")
n_bright = sum(1 for r in comp_rows if r["Lighting"] == "Bright/natural")
n_warm = sum(1 for r in comp_rows if r["Lighting"] == "Warm/even")
n_remote = sum(1 for r in comp_rows if r["Format"] == "Remote/Zoom")
n_studio = sum(1 for r in comp_rows if r["Format"] == "In-person studio")
n_mics_hidden = sum(1 for r in comp_rows if r["Mics Visible"] == "No")
n_branded = sum(1 for r in comp_rows if r["Branded Set"] == "Yes")
n_black = sum(1 for r in comp_rows if r["Wardrobe"] == "All black")

st.markdown(f"""
**Lighting:** {n_dark} channels use dark/moody, {n_warm} warm/even, {n_bright} bright/natural.
The top-tier channels split into dark (DOAC, Lex, Huberman, Jocko, Rich Roll, Impact Theory) and
warm (Rogan, Chris Williamson, Jay Shetty, Tim Ferriss, Dwarkesh). Both work at scale.

**Format:** {n_studio} channels film in-person in a studio. {n_remote} use remote/Zoom.
The largest channels are overwhelmingly in-person. Remote format caps out around 500K subs,
with Robinson Erhardt (532K) as the main exception.

**Equipment visibility:** {n_mics_hidden} channels hide mics (DOAC, Relentless, Silicon Valley Girl).
Hiding equipment creates a "natural conversation" feel. Showing equipment (Rogan, Jocko, PBD)
creates an "I'm on a show" feel. Both work.

**Wardrobe:** {n_black} channels have hosts who consistently wear all black (DOAC, Huberman,
Impact Theory, Rich Roll, Jocko). The most successful hosts pick one look and never deviate.
Wardrobe IS the personal brand at thumbnail scale.

**Branded sets:** {n_branded} channels use prominent on-set branding (neon signs, logos, mic flags).
Most top channels either brand heavily (Rogan, PBD, Lewis Howes) or not at all (DOAC, Huberman, Lex).

**Production quality vs channel size:** Smaller channels that invest in in-person, multi-camera
production (Relentless, Unsupervised Learning, Newcomer Pod) visually punch above their weight.
Channels stuck in Zoom format (What Bitcoin Did, Investors Podcast, Prime Movers Lab) have a
visible production ceiling.
""")

st.markdown("---")
st.caption("Analysis based on actual video frames from 5 recent long-form episodes per channel. April 2026.")
