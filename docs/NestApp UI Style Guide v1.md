## 0) Goal

Build a calm, premium, hospitality-grade UI similar to nestliving.id: airy whitespace, warm neutrals, deep teal headlines, and gold capsule CTA. Avoid “tech SaaS clutter”.

**Language:** English only  
**UI Mode:** Simple UX (journey-first)  
**Visual keywords:** calm, premium, airy, warm, clean, hospitality

---

## 1) Design Tokens (JSON)

Use these tokens as the single source of truth in code (Tailwind config or CSS variables). Do not invent new colors unless absolutely necessary.

`{   "brand": {     "name": "NestApp",     "tone": ["calm", "premium", "airy", "warm", "hospitality"]   },   "colors": {     "teal": {       "900": "#133437",       "800": "#1C4143",       "700": "#2A5556"     },     "neutral": {       "white": "#FFFFFF",       "softWhite": "#F1F1EE",       "warmBeige": "#DFDBD1",       "sand": "#D8DAD3",       "line": "rgba(33,41,41,0.10)",       "lineSoft": "rgba(33,41,41,0.08)"     },     "text": {       "primary": "#212929",       "secondary": "#565656",       "muted": "rgba(33,41,41,0.62)"     },     "accent": {       "goldTop": "#B4A78B",       "goldBottom": "#96856C",       "olive": "#3D4D47"     },     "feedback": {       "success": "#2E7D32",       "warning": "#B26A00",       "danger": "#B00020",       "info": "#2B6CB0"     }   },   "radius": {     "card": 20,     "input": 14,     "button": 999,     "modal": 24   },   "shadow": {     "soft": "0 10px 30px rgba(0,0,0,0.06)",     "xs": "0 6px 18px rgba(0,0,0,0.05)"   },   "border": {     "subtle": "1px solid rgba(33,41,41,0.08)",     "strong": "1px solid rgba(33,41,41,0.12)"   },   "layout": {     "maxWidth": 1200,     "pagePaddingX": 24,     "sectionPaddingYDesktop": 80,     "sectionPaddingYMobile": 48,     "gridGap": 24   },   "typography": {     "headingFont": "DM Sans",     "bodyFont": "Lora",     "uiFont": "DM Sans",     "scale": {       "h1": 56,       "h2": 40,       "h3": 28,       "h4": 22,       "body": 18,       "small": 14,       "caption": 12     },     "lineHeight": {       "tight": 1.1,       "normal": 1.5,       "relaxed": 1.7     },     "weight": {       "regular": 400,       "medium": 500,       "semibold": 600,       "bold": 700     }   },   "buttons": {     "primary": {       "radius": 999,       "padding": "12px 28px",       "border": "1px solid rgba(19,52,55,0.35)",       "background": "linear-gradient(180deg, #B4A78B 0%, #96856C 100%)",       "textColor": "#FFFFFF"     },     "secondary": {       "radius": 999,       "padding": "12px 28px",       "border": "1px solid rgba(33,41,41,0.12)",       "background": "#FFFFFF",       "textColor": "#133437"     }   } }`

---

## 2) Typography Rules (Strict)

- Headings use **DM Sans**, color **teal-900**.
    
- Body text uses **Lora**, color **text.primary** or **text.secondary**.
    
- Avoid mixing too many font weights. Use only: 400, 500, 600.
    
- Use generous line-height for body: 1.7.
    

### Heading usage

- H1: 56px, semibold, teal-900, tight line-height
    
- H2: 40px, semibold, teal-900
    
- H3: 28px, semibold, teal-900
    
- H4: 22px, semibold, teal-900
    

---

## 3) Layout & Spacing (This is what makes it feel premium)

- Use **large whitespace**.
    
- Max content width: **1200px**.
    
- Page padding: **24px**.
    
- Card padding: **24px–28px**.
    
- Avoid dense tables. Prefer roomy rows.
    

### Spacing scale (use consistent increments)

- 8 / 12 / 16 / 24 / 32 / 48 / 64 / 80
    

---

## 4) Core Components (Minimal Set)

### 4.1 App Shell

- Background: **neutral.softWhite**
    
- Sidebar: white surface, subtle border, no heavy shadows
    
- Top bar: minimal, no sticky heavy elements
    

### 4.2 Cards

- Background: white
    
- Border: subtle
    
- Radius: card radius
    
- Shadow: soft (optional, use sparingly)
    

### 4.3 Buttons

- Primary: gold gradient capsule
    
- Secondary: white capsule with border
    
- No extra button styles.
    

### 4.4 Inputs

- White background
    
- Rounded (14px)
    
- Border subtle
    
- Focus ring: subtle teal (avoid neon)
    

### 4.5 Badges / Status Pills

- Small rounded pill
    
- Background: neutral.warmBeige or softWhite
    
- Text: teal-900 or text.secondary
    
- Avoid bright chip colors unless error/warning.
    

### 4.6 Modal

- Radius 24
    
- Soft shadow
    
- Minimal header
    

---

## 5) Dashboard Visual Rules (with Donut Charts)

Dashboard must look calm and informative.

### Layout

1. Top: 4 summary cards (Deals in progress, Blocked, Awaiting action, Completed)
    
2. Middle: 2 donut charts (Unit occupancy, Deal status)
    
3. Bottom: small list of in-progress deals
    

### Donut chart style

- Use brand palette: teal + neutrals + gold
    
- No rainbow.
    
- Labels minimal.
    
- Chart is read-only (not clickable).
    

---

## 6) Deal Journey Page Rules (Most Important Screen)

This page must be the simplest.

### Must show

- Tenant summary + Unit summary (small)
    
- Journey checklist (vertical)
    
- Current step highlighted
    
- Exactly **one primary action button** for the current step
    

### Must not show

- Complex system statuses
    
- Technical logs
    
- Multiple competing CTAs
    

### Blocking message tone

Plain hospitality tone:

- “Action required: Upload Invoice to continue.”
    
- “Please complete the previous step.”
    

---

## 7) Copy Tone & Microcopy (English)

Tone: calm, polite, practical.

Use phrases like:

- “Action required”
    
- “Ready to proceed”
    
- “This step is not available yet”
    
- “Please complete the previous step”
    

Avoid:

- “Error 500”
    
- “Validation failed”
    
- “Exception stack trace”
    

---

## 8) Do & Don’t

### DO

- Use whitespace generously
    
- Keep navigation minimal
    
- Use soft borders, subtle shadows
    
- Use teal headings + warm neutrals
    
- Keep actions inside Deal Journey
    

### DON’T

- Create “busy SaaS dashboards”
    
- Add many icons everywhere
    
- Add too many color accents
    
- Add nested menus
    
- Show technical data to Admin
    

---

## 9) Implementation Notes for Claude Code

When generating frontend code:

- Create a single `theme.ts` or CSS variables file from the tokens.
    
- Use consistent component primitives: `Card`, `Button`, `Input`, `Badge`, `Modal`.
    
- Avoid extra UI libraries unless needed.
    
- Ensure everything looks premium with spacing and typography.
    

---

## 10) Acceptance Criteria (Visual)

The app should visually feel:

- airy, premium, warm, calm
    
- similar look-and-feel to nestliving.id
    
- not like a generic admin dashboard