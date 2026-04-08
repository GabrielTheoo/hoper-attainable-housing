import json, uuid, os

def gid(): return uuid.uuid4().hex[:8]

OR = "#EB7F1E"
BK = "#1A1A1A"
WH = "#FFFFFF"
GM = "#666666"
OL = "#FDF2E9"
BA = "#F9F9F7"

def section(settings, cols):
    return {"id": gid(), "elType": "section", "isInner": False, "settings": settings, "elements": cols}

def col(size, widgets, extra=None):
    s = {"_column_size": size, "_inline_size": None}
    if extra:
        s.update(extra)
    return {"id": gid(), "elType": "column", "settings": s, "elements": widgets}

def w(wtype, settings):
    return {"id": gid(), "elType": "widget", "widgetType": wtype, "settings": settings, "elements": []}

def pad(t, r, b, l):
    return {"unit": "px", "top": str(t), "right": str(r), "bottom": str(b), "left": str(l), "isLinked": False}

def heading(text, tag="h2", color=BK, align="left", weight="700", size=44, anim=None):
    s = {
        "title": text, "header_size": tag, "title_color": color, "align": align,
        "typography_typography": "custom", "typography_font_family": "Montserrat",
        "typography_font_weight": weight,
        "typography_font_size": {"unit": "px", "size": size},
        "_padding": pad(0, 0, 16, 0)
    }
    if anim:
        s["_animation"] = anim
    return w("heading", s)

def text_block(html, color=GM, size=17, align="left", anim=None):
    s = {
        "editor": html, "text_color": color,
        "typography_typography": "custom", "typography_font_family": "Montserrat",
        "typography_font_size": {"unit": "px", "size": size}, "align": align
    }
    if anim:
        s["_animation"] = anim
    return w("text-editor", s)

def spacer(h):
    return w("spacer", {"space": {"unit": "px", "size": h}})

def html_w(html):
    return w("html", {"html": html})

def label_html(txt):
    return (
        f'<p style="font-size:12px;font-weight:700;letter-spacing:2.5px;'
        f'text-transform:uppercase;color:{OR};margin-bottom:8px;'
        f'display:flex;align-items:center;gap:8px;font-family:Montserrat,sans-serif;">'
        f'<span style="display:block;width:24px;height:2px;background:{OR};flex-shrink:0;"></span>'
        f'{txt}</p>'
    )

def feature_card(emoji, title, desc, link_text, link_url):
    return (
        f'<div style="background:#fff;border:1px solid #E8E8E8;border-radius:16px;padding:32px;'
        f'display:flex;flex-direction:column;gap:14px;height:100%;">'
        f'<div style="width:52px;height:52px;background:{OL};border-radius:12px;'
        f'display:flex;align-items:center;justify-content:center;font-size:22px;">{emoji}</div>'
        f'<h3 style="font-size:18px;font-weight:700;color:{BK};margin:0;line-height:1.3;font-family:Montserrat,sans-serif;">{title}</h3>'
        f'<p style="font-size:15px;line-height:1.7;color:{GM};margin:0;flex:1;font-family:Montserrat,sans-serif;">{desc}</p>'
        f'<a href="{link_url}" style="color:{OR};font-weight:600;font-size:14px;text-decoration:none;font-family:Montserrat,sans-serif;">{link_text} \u2192</a>'
        f'</div>'
    )

def audience_card(emoji, title, desc, link_text, link_url):
    return (
        f'<div style="background:#fff;border:1px solid #E8E8E8;border-radius:16px;padding:32px;'
        f'display:flex;flex-direction:column;gap:14px;height:100%;">'
        f'<div style="width:48px;height:48px;background:{OL};border-radius:12px;'
        f'display:flex;align-items:center;justify-content:center;font-size:20px;">{emoji}</div>'
        f'<h4 style="font-size:19px;font-weight:700;color:{BK};margin:0;font-family:Montserrat,sans-serif;">{title}</h4>'
        f'<p style="font-size:15px;line-height:1.7;color:{GM};margin:0;flex:1;font-family:Montserrat,sans-serif;">{desc}</p>'
        f'<a href="{link_url}" style="color:{OR};font-weight:600;font-size:14px;text-decoration:none;font-family:Montserrat,sans-serif;">{link_text} \u2192</a>'
        f'</div>'
    )

def benefit_item(emoji, title, desc):
    return (
        f'<div style="display:flex;align-items:flex-start;gap:16px;">'
        f'<div style="width:44px;height:44px;background:{OL};border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0;">{emoji}</div>'
        f'<div><strong style="font-size:16px;font-weight:700;color:{BK};display:block;'
        f'margin-bottom:6px;font-family:Montserrat,sans-serif;">{title}</strong>'
        f'<p style="font-size:14px;line-height:1.7;color:{GM};margin:0;font-family:Montserrat,sans-serif;">{desc}</p></div>'
        f'</div>'
    )

def check_item(text, dark=False):
    bg = OR
    fg = "rgba(255,255,255,0.9)" if dark else BK
    return (
        f'<div style="display:flex;align-items:flex-start;gap:12px;font-size:15px;'
        f'color:{fg};font-family:Montserrat,sans-serif;">'
        f'<span style="width:24px;height:24px;background:{bg};border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;color:#fff;'
        f'font-size:11px;flex-shrink:0;margin-top:1px;">\u2713</span>{text}</div>'
    )

def x_item(text):
    return (
        f'<div style="display:flex;align-items:center;gap:12px;font-size:15px;color:{BK};font-family:Montserrat,sans-serif;">'
        f'<span style="width:24px;height:24px;background:#FFE5E5;border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;color:#E53935;font-size:11px;flex-shrink:0;">\u2717</span>{text}</div>'
    )

content = []

# ────────────────────────────────────────────────────────
# 1. HERO
# ────────────────────────────────────────────────────────
badge = (
    f'<span style="display:inline-flex;align-items:center;gap:8px;'
    f'background:rgba(235,127,30,0.15);border:1px solid rgba(235,127,30,0.4);'
    f'color:{OR};font-size:13px;font-weight:600;font-family:Montserrat,sans-serif;'
    f'padding:8px 16px;border-radius:999px;">'
    f'\u2736 Earn up to $13,000 toward your closing costs</span>'
)

hero_btns = (
    f'<div style="display:flex;gap:16px;flex-wrap:wrap;">'
    f'<a href="/check-eligibility" style="display:inline-flex;align-items:center;gap:8px;'
    f'padding:14px 28px;background:{OR};color:#fff;border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:16px;font-weight:600;text-decoration:none;'
    f'box-shadow:0 8px 32px rgba(235,127,30,0.35);">Check Your Eligibility \u2192</a>'
    f'<a href="/programs" style="display:inline-flex;align-items:center;gap:8px;'
    f'padding:14px 28px;background:transparent;color:#fff;'
    f'border:2px solid rgba(255,255,255,0.45);border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:16px;font-weight:600;text-decoration:none;">Learn About Hoper</a>'
    f'</div>'
)

trust_pills = (
    f'<div style="display:flex;flex-wrap:wrap;gap:28px;padding-top:32px;'
    f'border-top:1px solid rgba(255,255,255,0.12);">'
    + "".join([
        f'<div style="display:flex;align-items:center;gap:10px;color:rgba(255,255,255,0.85);'
        f'font-size:14px;font-weight:500;font-family:Montserrat,sans-serif;">'
        f'<span style="color:{OR};font-size:16px;">\u2713</span>{t}</div>'
        for t in [
            "No additional credit score requirement",
            "Your mortgage rate stays the same",
            "Available in most states",
            "New &amp; fully owned solar system"
        ]
    ])
    + f'</div>'
)

content.append(section({
    "background_background": "classic",
    "background_image": {"url": "https://gabrieltheoo.github.io/hoper-attainable-housing/Frame%20427319444.webp"},
    "background_size": "cover",
    "background_position": "center center",
    "background_overlay_background": "classic",
    "background_overlay_color": "rgba(10,10,10,0.65)",
    "height": "100vh",
    "padding": pad(160, 40, 120, 40),
    "custom_css": (
        ".elementor-background-overlay{"
        "background:linear-gradient(to right,rgba(10,10,10,0.88) 0%,"
        "rgba(10,10,10,0.6) 55%,rgba(10,10,10,0.25) 100%) !important;}"
    )
}, [col(100, [
    html_w(badge),
    spacer(16),
    heading("Homeownership Is Closer Than You Think", "h1", WH, "left", "800", 60),
    text_block(
        "<p>Eligible homebuyers can earn up to <strong>$13,000 toward closing costs</strong>, "
        "receive financial mentorship, and lower long-term energy costs with a fully owned "
        "solar system \u2014 all without changing their mortgage rate.</p>",
        "rgba(255,255,255,0.85)", 18
    ),
    spacer(24),
    html_w(hero_btns),
    spacer(48),
    html_w(trust_pills),
])]))

# ────────────────────────────────────────────────────────
# 2. FEATURES
# ────────────────────────────────────────────────────────
fc = [
    feature_card("\U0001f393", "Prepare for Your Home Purchase",
        "Get online, self-paced, pre-closing financial education. In less than 6 hours, "
        "you'll understand what it takes to buy a house and how to get there.", "Enroll Now", "/programs"),
    feature_card("\U0001f9e0", "Benefit from Financial Advice",
        "Receive post-closing financial mentorship designed to help you master proven "
        "wealth-building strategies and move forward with confidence and clarity.", "Ensure your success", "/programs"),
    feature_card("\U0001f52c", "Participate in Valuable Research",
        "Participate in a structured initiative studying how education, mentorship, and stronger "
        "financial positioning improve long-term homeowner success.", "Start Earning", "/programs"),
]
fc2 = [
    feature_card("\U0001f4b0", "Earn 3.5% \u2014 Up to $13,000",
        "Earn income by participating in a homeownership research program and use it toward "
        "closing costs, strengthening financial reserves, or reducing debt.", "Start Earning", "/programs"),
    feature_card("\u2600\ufe0f", "Lower Long-Term Housing Costs",
        "Lower utility expenses through a fully owned solar energy system, helping you create "
        "more predictable monthly housing costs.", "How it works", "/programs"),
]

cards_row1 = (
    f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">'
    + "".join(fc) + f'</div>'
)
cards_row2 = (
    f'<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:24px;'
    f'max-width:66.6%;margin:24px auto 0;">'
    + "".join(fc2) + f'</div>'
)

content.append(section({
    "background_background": "classic", "background_color": WH,
    "padding": pad(96, 40, 96, 40)
}, [col(100, [
    html_w(f'<div style="text-align:center;">{label_html("The Hoper Program")}</div>'),
    heading("Start Earning Toward Your Home Purchase", "h2", BK, "center", "700", 44, "fadeInUp"),
    text_block("<p>We remove doubt and friction from the homebuying process through the Hoper Research Program.</p>", GM, 18, "center"),
    spacer(48),
    html_w(cards_row1 + cards_row2),
])]))

# ────────────────────────────────────────────────────────
# 3. COMPARISON
# ────────────────────────────────────────────────────────
without_items = "".join([
    x_item(t) for t in [
        "Stretching to cover closing costs",
        "Draining savings just to make the numbers work",
        "Entering ownership without a long-term financial strategy"
    ]
])
with_items = "".join([
    check_item(t, dark=True) for t in [
        "Earn up to $13,000 toward closing",
        "Follow a proven financial education framework",
        "Lower and stabilize long-term housing costs"
    ]
])

comparison_html = (
    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;max-width:960px;margin:0 auto;">'

    f'<div style="background:rgba(26,26,26,0.03);border:1px solid #E8E8E8;border-radius:20px;padding:40px;">'
    f'<div style="font-size:13px;font-weight:700;color:{GM};text-transform:uppercase;'
    f'letter-spacing:1.5px;margin-bottom:24px;font-family:Montserrat,sans-serif;">Without a structured plan</div>'
    f'<div style="display:flex;flex-direction:column;gap:16px;margin-bottom:28px;">{without_items}</div>'
    f'<div style="background:{BA};border-radius:12px;padding:20px;font-size:14px;color:{GM};'
    f'line-height:1.65;font-family:Montserrat,sans-serif;">'
    f'Higher monthly payments + Lower cash reserves = More stress, less joy, and more financial risks.</div>'
    f'</div>'

    f'<div style="background:{BK};border-radius:20px;padding:40px;">'
    f'<div style="display:inline-flex;align-items:center;gap:6px;background:{OR};color:#fff;'
    f'font-size:12px;font-weight:700;font-family:Montserrat,sans-serif;padding:6px 14px;'
    f'border-radius:999px;margin-bottom:20px;">\u2605 The Hoper Way</div>'
    f'<div style="font-size:22px;font-weight:800;color:#fff;margin-bottom:24px;font-family:Montserrat,sans-serif;">With Hoper</div>'
    f'<div style="display:flex;flex-direction:column;gap:16px;margin-bottom:28px;">{with_items}</div>'
    f'<div style="background:rgba(255,255,255,0.08);border-radius:12px;padding:20px;'
    f'font-size:14px;color:rgba(255,255,255,0.8);line-height:1.65;font-family:Montserrat,sans-serif;">'
    f'Lower monthly payments + Higher cash reserves = <strong style="color:#fff;">'
    f'Less stress, more joy, and the peace that comes with financial confidence.</strong></div>'
    f'</div>'
    f'</div>'
)

enroll_btn = (
    f'<div style="text-align:center;">'
    f'<a href="/check-eligibility" style="display:inline-flex;align-items:center;gap:8px;'
    f'padding:16px 40px;background:{OR};color:#fff;border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:17px;font-weight:600;text-decoration:none;'
    f'box-shadow:0 8px 32px rgba(235,127,30,0.35);">Enroll Now \u2192</a>'
    f'</div>'
)

content.append(section({
    "background_background": "classic", "background_color": BA,
    "padding": pad(96, 40, 96, 40)
}, [col(100, [
    heading("Don't Let Go of the Dream of Homeownership", "h2", BK, "center", "700", 44, "fadeInUp"),
    text_block("<p>Buying a home is one thing. Doing so prepared for the future is another.</p>", GM, 18, "center"),
    spacer(48),
    html_w(comparison_html),
    spacer(40),
    html_w(enroll_btn),
])]))

# ────────────────────────────────────────────────────────
# 4. GUIDANCE (2-col)
# ────────────────────────────────────────────────────────
guidance_checklist = (
    f'<div style="display:flex;flex-direction:column;gap:14px;">'
    + "".join([check_item(t) for t in [
        "Understand exactly what lenders evaluate and how to strengthen your profile",
        "Get clear on your numbers, reserves, and financial position",
        "Follow a defined path from pre-approval to closing",
        "Enter ownership with a plan for long-term stability"
    ]])
    + f'</div>'
)

guidance_cta_btn = (
    f'<a href="/company" style="display:inline-flex;align-items:center;gap:8px;'
    f'padding:14px 28px;background:{OR};color:#fff;border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:16px;font-weight:600;text-decoration:none;'
    f'box-shadow:0 8px 32px rgba(235,127,30,0.35);">Learn More About Hoper \u2192</a>'
)

guidance_image = (
    f'<div style="position:relative;">'
    f'<img src="https://s3-alpha-sig.figma.com/img/3904/9dbf/cd300cd37add57c8e5d643bc7a79c454" '
    f'alt="Couple reviewing homebuying documents" '
    f'style="width:100%;height:520px;object-fit:cover;border-radius:24px;display:block;">'
    f'<div style="position:absolute;top:24px;right:24px;background:#fff;border-radius:14px;'
    f'padding:16px 20px;box-shadow:0 8px 40px rgba(0,0,0,0.12);text-align:center;">'
    f'<div style="font-size:28px;font-weight:800;color:{OR};font-family:Montserrat,sans-serif;">$13K</div>'
    f'<div style="font-size:12px;color:{GM};font-weight:500;font-family:Montserrat,sans-serif;">Max earnings</div>'
    f'</div>'
    f'<div style="position:absolute;bottom:24px;left:24px;background:rgba(26,26,26,0.85);'
    f'backdrop-filter:blur(12px);border-radius:14px;padding:14px 20px;'
    f'display:flex;align-items:center;gap:12px;color:#fff;">'
    f'<span style="font-size:22px;">\u2600\ufe0f</span>'
    f'<div><div style="font-size:14px;font-weight:700;font-family:Montserrat,sans-serif;">Solar included</div>'
    f'<div style="font-size:11px;opacity:.7;font-family:Montserrat,sans-serif;">Fully owned system</div></div>'
    f'</div>'
    f'</div>'
)

content.append(section({
    "background_background": "classic", "background_color": WH,
    "padding": pad(96, 40, 96, 40)
}, [
    col(50, [
        html_w(label_html("Homebuying is complicated")),
        heading("Guidance Before and After You Close", "h2", BK, "left", "700", 40, "fadeInLeft"),
        text_block(
            "<p>Hoper supports you with structured education before closing and financial mentorship "
            "after you move in \u2014 helping you navigate both the purchase and the long-term realities of ownership.</p>",
            GM, 17
        ),
        spacer(24),
        html_w(guidance_checklist),
        spacer(32),
        html_w(guidance_cta_btn),
    ], {"_column_size": 50}),
    col(50, [html_w(guidance_image)], {"_column_size": 50}),
]))

# ────────────────────────────────────────────────────────
# 5. WHY HOPER (2-col reversed)
# ────────────────────────────────────────────────────────
why_image = (
    f'<div style="position:relative;">'
    f'<img src="https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=700&q=80" '
    f'alt="Happy family in front of their new home" '
    f'style="width:100%;height:520px;object-fit:cover;border-radius:24px;display:block;">'
    f'<div style="position:absolute;bottom:24px;right:24px;background:#fff;border-radius:14px;'
    f'padding:14px 20px;box-shadow:0 8px 40px rgba(0,0,0,0.12);display:flex;align-items:center;gap:12px;">'
    f'<div style="width:40px;height:40px;background:{OL};border-radius:50%;'
    f'display:flex;align-items:center;justify-content:center;font-size:18px;">\U0001f4b2</div>'
    f'<div><div style="font-size:18px;font-weight:800;color:{BK};font-family:Montserrat,sans-serif;">3.5%</div>'
    f'<div style="font-size:12px;color:{GM};font-family:Montserrat,sans-serif;">Earned at closing</div></div>'
    f'</div>'
    f'</div>'
)

why_benefits = (
    f'<div style="display:flex;flex-direction:column;gap:24px;">'
    + benefit_item("\U0001f4b2", "Earn income when you buy or refinance",
        "Receive up to 3.5% of your home's purchase price (up to $13,000) as earned income to "
        "reduce closing costs, strengthen reserves, or improve your overall financial position.")
    + benefit_item("\U0001f3e0", "Build equity instead of paying rent",
        "Homeownership helps families build a future of equity and long-term financial stability.")
    + benefit_item("\u26a1", "Lower and more predictable housing costs",
        "Fully owned solar helps lower utility costs and stabilize monthly housing expenses.")
    + benefit_item("\U0001f465", "Continued support after closing",
        "Getting you into a home is step one \u2014 the real goal is long-term stability and financial progress.")
    + f'</div>'
)

why_cta = (
    f'<a href="/check-eligibility" style="display:inline-flex;align-items:center;gap:8px;'
    f'padding:14px 28px;background:{OR};color:#fff;border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:16px;font-weight:600;text-decoration:none;'
    f'box-shadow:0 8px 32px rgba(235,127,30,0.35);">Check Your Eligibility \u2192</a>'
)

content.append(section({
    "background_background": "classic", "background_color": BA,
    "padding": pad(96, 40, 96, 40)
}, [
    col(50, [html_w(why_image)], {"_column_size": 50}),
    col(50, [
        html_w(label_html("Why Homebuyers Choose Hoper")),
        heading("Build a Sustainable Future and Prosper Financially", "h2", BK, "left", "700", 40, "fadeInRight"),
        spacer(24),
        html_w(why_benefits),
        spacer(32),
        html_w(why_cta),
    ], {"_column_size": 50}),
]))

# ────────────────────────────────────────────────────────
# 6. AUDIENCE (4 cards)
# ────────────────────────────────────────────────────────
audience_cards = "".join([
    audience_card(e, t, d, l, u) for e, t, d, l, u in [
        ("\U0001f3e0", "For Homebuyers",
         "Earn income at closing. Reduce out-of-pocket costs. Build long-term stability through financial education and solar ownership.",
         "See How It Works", "/use-cases/homebuyers"),
        ("\U0001f4bc", "For Loan Officers",
         "Differentiate your FHA offering. Strengthen borrower qualification. Provide measurable financial value without layering additional debt.",
         "See Loan Officer Details", "/use-cases/loan-officers"),
        ("\U0001f511", "For Real Estate Agents",
         "Help clients compete with stronger financial positioning. Increase closing confidence. Offer something other buyers don't have.",
         "Explore Agent Benefits", "/use-cases/real-estate-agents"),
        ("\U0001f3d7\ufe0f", "For Builders",
         "Help buyers qualify more confidently. Reduce transaction friction. Offer new construction with built-in long-term energy savings.",
         "Explore Builder Benefits", "/use-cases/home-builders"),
    ]
])

content.append(section({
    "background_background": "classic", "background_color": WH,
    "padding": pad(96, 40, 96, 40)
}, [col(100, [
    html_w(f'<div style="text-align:center;">{label_html("Built For Everyone")}</div>'),
    heading("Built for You \u2014 No Matter What Role You Play in the Transaction",
            "h2", BK, "center", "700", 44, "fadeInUp"),
    text_block(
        "<p>Hoper strengthens the financial position of everyone involved in the homebuying process \u2014 "
        "aligning buyers and industry partners around stronger outcomes.</p>",
        GM, 18, "center"
    ),
    spacer(48),
    html_w(f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:24px;">{audience_cards}</div>'),
])]))

# ────────────────────────────────────────────────────────
# 7. TESTIMONIALS
# ────────────────────────────────────────────────────────
def testimonial_card(stars, quote, name, role):
    return (
        f'<div style="background:#fff;border-radius:16px;padding:28px;border:1px solid #E8E8E8;">'
        f'<div style="color:#FBBC04;font-size:16px;margin-bottom:12px;">{"★" * stars}</div>'
        f'<p style="font-size:15px;line-height:1.7;color:{BK};margin:0 0 20px;'
        f'font-family:Montserrat,sans-serif;">"{quote}"</p>'
        f'<div style="display:flex;align-items:center;gap:12px;">'
        f'<div style="width:40px;height:40px;background:{OL};border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;font-size:18px;">\U0001f464</div>'
        f'<div><strong style="font-size:14px;color:{BK};display:block;font-family:Montserrat,sans-serif;">{name}</strong>'
        f'<span style="font-size:12px;color:{GM};font-family:Montserrat,sans-serif;">{role}</span></div>'
        f'</div>'
        f'</div>'
    )

testimonials_grid = (
    f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:24px;">'
    + testimonial_card(5,
        "Hoper made our dream of homeownership real. We earned $11,200 toward closing and the solar system has already cut our electricity bill in half.",
        "Maria T.", "First-Time Homebuyer, Arizona")
    + testimonial_card(5,
        "The financial education program was eye-opening. I understood the home buying process so much better and felt truly prepared when we closed.",
        "James R.", "Homebuyer, Texas")
    + testimonial_card(5,
        "As a loan officer, I've referred dozens of clients to Hoper. It strengthens their financial profile and makes my job easier. Win-win.",
        "Sarah K.", "Loan Officer, Florida")
    + testimonial_card(5,
        "We weren't sure we could afford to buy. Hoper changed that. The education, the earned income, and the solar savings made everything click.",
        "David & Priya M.", "First-Time Homebuyers, Georgia")
    + testimonial_card(5,
        "My clients who go through Hoper come to closing more financially prepared and less stressed. It's become a standard recommendation for me.",
        "Carlos R.", "Real Estate Agent, Nevada")
    + testimonial_card(5,
        "The post-closing mentorship was something I didn't expect to value so much. Now two years in, we're building wealth we never thought possible.",
        "Aisha L.", "Homeowner, North Carolina")
    + f'</div>'
)

content.append(section({
    "background_background": "classic", "background_color": BA,
    "padding": pad(96, 40, 96, 40)
}, [col(100, [
    html_w(f'<div style="text-align:center;">{label_html("Social Proof")}</div>'),
    heading("Real People. Real Progress", "h2", BK, "center", "700", 44, "fadeInUp"),
    text_block(
        "<p>Whether you're buying your first home or exploring your options, Hoper helps you move forward "
        "with earned income, long-term energy savings, and a structure designed for stability.</p>",
        GM, 18, "center"
    ),
    spacer(20),
    html_w(
        f'<div style="text-align:center;display:flex;align-items:center;justify-content:center;gap:12px;">'
        f'<span style="color:#FBBC04;font-size:24px;">\u2605\u2605\u2605\u2605\u2605</span>'
        f'<span style="font-size:22px;font-weight:800;color:{BK};font-family:Montserrat,sans-serif;">4.9</span>'
        f'<span style="font-size:15px;color:{GM};font-family:Montserrat,sans-serif;">214 Google reviews</span>'
        f'</div>'
    ),
    spacer(48),
    html_w(testimonials_grid),
])]))

# ────────────────────────────────────────────────────────
# 8. FAQ BANNER
# ────────────────────────────────────────────────────────
faq_banner = (
    f'<div style="background:{BA};border-radius:20px;padding:48px;'
    f'display:flex;align-items:center;justify-content:space-between;gap:40px;flex-wrap:wrap;">'
    f'<div style="display:flex;align-items:flex-start;gap:24px;">'
    f'<div style="width:64px;height:64px;background:{OL};border-radius:16px;'
    f'display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;">\u2753</div>'
    f'<div>'
    f'<h2 style="font-size:26px;font-weight:800;color:{BK};margin:0 0 8px;font-family:Montserrat,sans-serif;">Any Questions?</h2>'
    f'<p style="font-size:16px;color:{GM};margin:0;line-height:1.65;max-width:480px;font-family:Montserrat,sans-serif;">'
    f'Find answers to common questions about eligibility, the program, and how Hoper works. '
    f"Can't find what you're looking for? We're here to help.</p>"
    f'</div>'
    f'</div>'
    f'<div style="display:flex;gap:16px;flex-shrink:0;">'
    f'<a href="/faqs" style="display:inline-flex;align-items:center;gap:8px;padding:14px 28px;'
    f'background:{OR};color:#fff;border-radius:999px;font-family:Montserrat,sans-serif;'
    f'font-size:15px;font-weight:600;text-decoration:none;">Read the FAQs \u2192</a>'
    f'<a href="/company" style="display:inline-flex;align-items:center;gap:8px;padding:14px 28px;'
    f'background:transparent;color:{BK};border:2px solid {BK};border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:15px;font-weight:600;text-decoration:none;">Contact Us</a>'
    f'</div>'
    f'</div>'
)

content.append(section({
    "background_background": "classic", "background_color": WH,
    "padding": pad(64, 40, 64, 40),
    "border_border": "solid",
    "border_width": pad(1, 0, 1, 0),
    "border_color": "#E8E8E8",
}, [col(100, [html_w(faq_banner)])]))

# ────────────────────────────────────────────────────────
# 9. CTA SECTION
# ────────────────────────────────────────────────────────
cta_btns = (
    f'<div style="text-align:center;display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">'
    f'<a href="/check-eligibility" style="display:inline-flex;align-items:center;gap:8px;'
    f'padding:16px 32px;background:#fff;color:{OR};border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:16px;font-weight:700;text-decoration:none;">'
    f'Check Your Eligibility \u2192</a>'
    f'<a href="/programs" style="display:inline-flex;align-items:center;gap:8px;'
    f'padding:16px 32px;background:transparent;color:#fff;'
    f'border:2px solid rgba(255,255,255,0.5);border-radius:999px;'
    f'font-family:Montserrat,sans-serif;font-size:16px;font-weight:600;text-decoration:none;">'
    f'Learn About Hoper</a>'
    f'</div>'
)

content.append(section({
    "background_background": "classic", "background_color": OR,
    "padding": pad(96, 40, 96, 40),
}, [col(100, [
    heading("Homeownership Shouldn't Feel Out of Reach", "h2", WH, "center", "800", 44, "fadeInUp"),
    spacer(16),
    text_block(
        "<p>Whether you're buying your first home or exploring your options, Hoper helps you move forward "
        "with earned income, long-term energy savings, and a structure designed for stability.</p>",
        "rgba(255,255,255,0.85)", 18, "center"
    ),
    spacer(36),
    html_w(cta_btns),
])]))

# ────────────────────────────────────────────────────────
# EXPORT
# ────────────────────────────────────────────────────────
template = {
    "version": "0.4",
    "title": "Hoper - Homepage",
    "type": "section",
    "content": content,
    "page_settings": {}
}

out = os.path.join(os.path.dirname(__file__), "hoper-homepage-elementor.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(template, f, ensure_ascii=False, indent=2)

size = os.path.getsize(out)
print(f"OK: {out}")
print(f"Size: {size // 1024} KB | Sections: {len(content)}")
