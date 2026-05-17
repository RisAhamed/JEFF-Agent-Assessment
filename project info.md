Task 01

## Custom Jeff AI Agent Interface

WordPress · OpenAI/groq Assistants API · Multi-Mode UI · Full-Screen Chat

Bottleneck

Jeff is JustStartUP's AI co-founder product. Currently needs even better custom and personalised feel as it already highly tailored for brands. We need a fully custom, owned agent interface embedded on WordPress with hard limit trackers.

Required Agent Modes

MODE 01

**Investor Mode**

Jeff simulates a seasoned seed investor — asks hard due diligence questions, challenges assumptions, pokes holes in the model. Founder gets battle-tested before real pitches.

MODE 02

**Refine My Business Model**

Jeff acts as a strategic co-founder — maps revenue streams, identifies leaky assumptions, suggests pivots, and helps tighten the core value proposition.

MODE 03

**Act as a Customer**

Jeff roleplays as the startup's target customer persona — responds to pitches, raises objections, simulates buying decisions, and gives honest product feedback.

MODE 04

**Build / Refine Pitch Deck**

Jeff interviews the founder across all 10 standard pitch deck sections, structures the content, and outputs a clean slide-by-slide brief ready for Canva integration (see Task 02).

MODE 05

**Financial Planning**

Jeff guides founders through revenue projections, burn rate, runway calculation, pricing strategy, and unit economics. Outputs structured financial summary.

Required Features

⛶

**Full-Screen Interface** Modal or dedicated page that takes full viewport. Not a corner widget. Closeable via ESC or X button.

⇄

**Mode Switcher** Top-of-interface mode selector. Switching mode resets the conversation and loads the corresponding system prompt.

🔒

**Premium Gate** Interface only renders for logged-in WordPress users with Premium role. Free users see an upgrade prompt.

💬

**Session Memory** Conversation history preserved within the session. Cleared on mode switch or page reload.

🔑

**Secure API Handling** OpenAI API key must be handled server-side via PHP endpoint. Never exposed in frontend JS.

📱

**Mobile Responsive** Full-screen experience must work correctly on mobile. Touch-friendly input and scroll behaviour.

🎨

**Brand Consistent** Dark cyberpunk aesthetic. Pitch black background, neon accents, Rosario font. Must match juststrtup.com visual identity.

⚡

**Streaming Responses** OpenAI streaming API for real-time token output. No waiting for full response to render.

Technical Requirements

Implementation

WordPress shortcode or custom page template. Must work inside Elementor HTML widget or as standalone WP page.

AI Backend

OpenAI Assistants API — one Assistant per mode (5 total) or single Assistant with dynamic instructions override per mode.

Server Layer

PHP REST endpoint registered via `register_rest_route()` to proxy OpenAI calls. API key stored in `wp-config.php` as constant.

Auth Check

Use `is_user_logged_in()` + `current_user_can()` or Ultimate Members role check to gate Premium content.

Code Delivery

Clean PHP + JS. Can use CodeSnippets plugin for PHP. No additional plugin dependencies unless pre-approved.

Compatibility

Must not conflict with WooCommerce, Ultimate Members, Paid Membership Pro, or Elementor.

Tech Stack

OpenAI Assistants API WordPress REST API PHP 8+ Vanilla JS / Fetch API Elementor HTML Widget Ultimate Members Paid Membership Pro CodeSnippets Plugin

Deliverables

Working full-screen Jeff agent interface with all 5 modes functional and switchable.

PHP REST endpoint file or CodeSnippets-ready snippet handling OpenAI proxying securely.

Mode 04 (Pitch Deck) outputs a structured JSON or formatted text object per slide — to be consumed by Task 02.

Brief setup documentation: how to add OpenAI API key, how to create/configure the 5 Assistants, how to embed on WordPress.

Tested on WordPress + Elementor environment. No console errors. No plugin conflicts.