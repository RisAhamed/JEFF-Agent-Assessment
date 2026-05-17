# Jeff AI Agent — Deployment Plan
## Candidate: Riswan Ahamed M | Platform: Render.com

---

## A. Render.com Deployment Steps (Step-by-Step)

### Prerequisites
- GitHub account with the `jeff-agent` repo pushed (`.env` must be in `.gitignore`)
- Render.com account (free tier — no credit card required for web services)
- Groq API key from https://console.groq.com

### Steps

1. **Ensure `requirements.txt` exists** in project root with all 4 dependencies:
   `fastapi`, `uvicorn[standard]`, `groq`, `python-dotenv`

2. **Ensure `render.yaml` exists** in project root — Render auto-detects this Blueprint file
   and uses it to configure the service (build command, start command, health check path)

3. **Push to GitHub** — confirm `.env` is NOT committed (check `.gitignore`):
   ```bash
   git add . && git commit -m "feat: jeff agent initial build" && git push origin main
   ```

4. **Create a new Render service**:
   - Go to https://dashboard.render.com → **New +** → **Blueprint**
   - Connect your GitHub repo
   - Render reads `render.yaml` automatically and pre-fills all configuration

5. **Set the secret environment variable**:
   - In the Render dashboard → your service → **Environment** tab
   - Click **Add Environment Variable**
   - Key: `GROQ_API_KEY` | Value: `gsk_your_actual_key`
   - Render encrypts this at rest — it is never exposed in logs or config files

6. **Trigger deploy** — Render builds the image, installs dependencies, and starts the service

7. **Verify** — hit the live URL:

   ```
   GET https://jeff-ai-agent.onrender.com/health
   ```

   Expected: `{"status":"ok","service":"Jeff AI Agent","model":"openai/gpt-oss-20b"}`

**API Key Security**: The key lives only in Render's encrypted environment variable store.
In code it is loaded with `os.getenv("GROQ_API_KEY")` — never hardcoded, never committed.

---

## B. CORS Configuration for WordPress Cross-Domain Calls

When a browser on a WordPress site (e.g., `https://juststrtup.com`) calls the FastAPI
service on a different domain (e.g., `https://jeff-ai-agent.onrender.com`), the browser
performs a **CORS preflight** before the actual request:

1. Browser sends an **OPTIONS request** to the FastAPI endpoint
2. FastAPI (via `CORSMiddleware`) returns `Access-Control-Allow-Origin: *` in the response headers
3. Browser checks this header — if the origin is allowed, it proceeds with the real POST request
4. Without this header, the browser blocks the request entirely — the error appears in DevTools console, not server logs

**FastAPI CORS configuration used:**

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Or: ["https://juststrtup.com"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**The header the browser checks**: `Access-Control-Allow-Origin`

For production: replace `["*"]` with `["https://juststrtup.com"]` to restrict access to the specific WordPress domain only.

---

## C. Cold Start Mitigation (Free Tier, No Upgrade)

**Problem**: Render's free tier spins down services after 15 minutes of inactivity.
The first request after sleep incurs a ~30–60 second cold start delay.

**Strategy**: Use a free uptime monitoring service to send a lightweight HTTP GET ping
to the `/health` endpoint every **10 minutes**, keeping the service warm.

**Implementation with UptimeRobot (free)**:

1. Create a free account at https://uptimerobot.com
2. New Monitor → **HTTP(s)** type
3. URL: `https://jeff-ai-agent.onrender.com/health`
4. Check interval: **5 minutes**
5. UptimeRobot pings the endpoint, Render's service stays awake

The `/health` endpoint is a simple JSON return — negligible compute cost.
This adds zero latency overhead to real users and uses no Groq API quota.

**Alternative**: Render's paid Starter plan ($7/month) eliminates cold starts entirely.
For the assessment, UptimeRobot is the correct no-cost solution.

---

## D. WordPress Integration — Embedding Jeff on juststrtup.com

The Jeff interface is a standalone HTML/CSS/JS file (`jeff-ui.html`) that connects to the
FastAPI backend via fetch API. It can be embedded into WordPress in two ways:

### Option 1: Elementor HTML Widget (Recommended)

1. In WordPress Admin → **Pages** → edit the Jeff agent page
2. In Elementor, add an **HTML Widget** to the page
3. Copy the entire contents of `jeff-ui.html` into the HTML widget
4. **Update the API_BASE_URL** in the `<script>` section to point to the live Render URL:

   ```javascript
   const API_BASE_URL = 'https://jeff-ai-agent.onrender.com';
   ```

5. Save and publish — Jeff loads inside the WordPress page with full-screen styling

**Why this works**: The HTML widget renders raw HTML/CSS/JS directly into the page.
The inline `<style>` uses `position: fixed` + `inset: 0` for full-viewport takeover.
All external resources (Google Fonts, marked.js) load via CDN — no WordPress dependencies.

### Option 2: WordPress Shortcode via CodeSnippets Plugin

Add this PHP snippet via the **CodeSnippets** plugin (no file editing required):

```php
<?php
/**
 * Jeff AI Agent — WordPress Shortcode
 * Usage: Place [jeff_agent] on any WordPress page
 */
function jeff_agent_shortcode() {
    // Premium gate — only logged-in Premium users can access Jeff
    if ( ! is_user_logged_in() ) {
        return '<div style="text-align:center;padding:40px;color:#fff;background:#0a0a0a;">
            <h2>Please log in to access Jeff AI Agent</h2>
            <a href="' . wp_login_url( get_permalink() ) . '" style="color:#7c3aed;">Log In</a>
        </div>';
    }

    // Check for Premium role (Ultimate Members or Paid Membership Pro)
    $user = wp_get_current_user();
    $has_premium = in_array( 'premium', (array) $user->roles )
                || in_array( 'subscriber', (array) $user->roles )
                || function_exists( 'pmpro_hasMembershipLevel' ) && pmpro_hasMembershipLevel( null, $user->ID );

    if ( ! $has_premium ) {
        return '<div style="text-align:center;padding:40px;color:#fff;background:#0a0a0a;">
            <h2>Jeff AI Agent is a Premium Feature</h2>
            <p style="color:#a1a1aa;">Upgrade your membership to access Jeff, your AI co-founder.</p>
            <a href="/pricing" style="display:inline-block;margin-top:16px;padding:12px 24px;
               background:#7c3aed;color:#fff;border-radius:8px;text-decoration:none;">Upgrade Now</a>
        </div>';
    }

    // Load Jeff UI — reads the HTML file and injects it
    $jeff_html = file_get_contents( get_template_directory() . '/jeff-ui.html' );
    return $jeff_html;
}
add_shortcode( 'jeff_agent', 'jeff_agent_shortcode' );
```

**Usage**: Place `[jeff_agent]` on any WordPress page. The shortcode:
- Checks if the user is logged in (redirects to login if not)
- Verifies Premium role via Ultimate Members or Paid Membership Pro
- Renders Jeff's full interface for Premium users
- Shows an upgrade prompt for Free users

### Premium Gate Logic

The project requires that only Premium WordPress users can access Jeff. The shortcode above
handles this via role checking. The logic supports both:

- **Ultimate Members**: Checks `$user->roles` for `premium` role
- **Paid Membership Pro**: Checks `pmpro_hasMembershipLevel()` function

Free users see a styled upgrade prompt instead of the Jeff interface.

### File Placement

- Copy `jeff-ui.html` to your WordPress theme directory (e.g., `/wp-content/themes/your-theme/jeff-ui.html`)
- Or paste the full HTML directly into the Elementor HTML widget (Option 1)

---

## E. Production Security — CORS Lockdown

For production deployment, restrict CORS to only allow requests from your WordPress domain:

```python
# In main.py — replace allow_origins=["*"] with:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://juststrtup.com", "https://www.juststrtup.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Session-Id"],  # Allow frontend to read session ID header
)
```

This ensures only the WordPress site can call the FastAPI backend — all other origins are blocked.

---

## F. API Key Security

The project requires that API keys are **never exposed in frontend JavaScript**.

**Current implementation**:
- `GROQ_API_KEY` is stored in Render's encrypted environment variables (production)
- Loaded via `os.getenv("GROQ_API_KEY")` in `main.py` — server-side only
- The frontend (`jeff-ui.html`) calls the FastAPI `/chat` endpoint — it never touches the API key
- The `.env` file is in `.gitignore` — never committed to version control

**WordPress equivalent**: The PHP shortcode approach mirrors `wp-config.php` constant storage:
```php
// In wp-config.php (if using PHP proxy instead of FastAPI):
define('GROQ_API_KEY', 'gsk_your_key_here');
```

In our architecture, the FastAPI service IS the secure server layer — it replaces the PHP
`register_rest_route()` endpoint described in the project spec. The API key lives on Render,
not in WordPress.
