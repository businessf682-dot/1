import os, re, math
from PIL import Image, ImageDraw
import studio as S
import rig as R

OX = R.OX
DISP = {"BULL": "RALLY", "CRASH": "SLUMP", "GOLDIE": "GAUGE", "CASH": "LEDGER"}
SW = {"BULL": ((52, 150, 86), (24, 80, 44)), "CRASH": ((176, 54, 58), (96, 22, 28)),
      "GOLDIE": ((218, 172, 50), (128, 96, 14)), "CASH": ((112, 142, 154), (58, 80, 92))}
SK, OL = (250, 250, 252), (22, 22, 26)


def _w(k, v):
    return max(1, int(v * k))


# ======================= CHARACTER ART (same head for all, only sweater colour changes) =======================
def c_torso(d, k, nm):
    fl, dk = SW[nm]
    R.poly(d, [(58, 302), (112, 270), (170, 262), (230, 262), (288, 270), (342, 302), (354, 540), (46, 540)], k, fl, OL, 3)
    R.poly(d, [(174, 200), (226, 200), (230, 268), (170, 268)], k, SK)
    d.line(R.P([(174, 200), (170, 268)], k), fill=OL, width=_w(k, 3))
    d.line(R.P([(226, 200), (230, 268)], k), fill=OL, width=_w(k, 3))
    for y in (228, 242):
        d.arc(((184 + OX) * k, y * k, (216 + OX) * k, (y + 12) * k), 20, 160, fill=OL, width=_w(k, 2))
    d.arc(((158 + OX) * k, 238 * k, (242 + OX) * k, 296 * k), 5, 175, fill=OL, width=_w(k, 11))
    d.arc(((158 + OX) * k, 238 * k, (242 + OX) * k, 296 * k), 5, 175, fill=dk, width=_w(k, 7))
    for pts in ([(118, 340), (130, 356), (142, 372)], [(262, 372), (276, 352), (288, 332)], [(168, 430), (200, 436), (232, 430)]):
        d.line(R.P(pts, k), fill=dk, width=_w(k, 3), joint="curve")


def c_arm(d, k, nm, s, th, ps, shy=0, *extra, **kw):
    fl, dk = SW[nm]
    sx, sy = R.SH[s]
    sy += shy
    t, p = math.radians(th), math.radians(ps)
    e = (sx + s * math.sin(t) * R.U, sy + math.cos(t) * R.U)
    w = (e[0] + s * math.sin(p) * R.F, e[1] + math.cos(p) * R.F)

    def seg(a, b, wd, col):
        d.line([((a[0] + OX) * k, a[1] * k), ((b[0] + OX) * k, b[1] * k)], fill=col, width=int(wd * k))
        r = wd / 2
        for q in (a, b):
            d.ellipse(((q[0] + OX - r) * k, (q[1] - r) * k, (q[0] + OX + r) * k, (q[1] + r) * k), fill=col)

    seg((sx, sy), e, 70, OL)
    seg(e, w, 58, OL)
    seg((sx, sy), e, 64, fl)
    seg(e, w, 52, fl)
    dx, dy = s * math.sin(p), math.cos(p)
    cw = (w[0] - dx * 12, w[1] - dy * 12)
    seg(cw, w, 54, OL)
    seg(cw, w, 48, dk)
    hx, hy = w[0] + dx * 18, w[1] + dy * 18
    R.ell(d, k, (hx - 22, hy - 26, hx + 22, hy + 26), SK, OL, 3)
    R.ell(d, k, (hx - s * 22 - 8, hy - 6 - 10, hx - s * 22 + 8, hy - 6 + 10), SK, OL, 2)
    for a in (-0.3, 0, 0.3):
        ca, sa = math.cos(a), math.sin(a)
        vx, vy = dx * ca - dy * sa, dx * sa + dy * ca
        d.line([((hx + OX + vx * 8) * k, (hy + vy * 8) * k), ((hx + OX + vx * 26) * k, (hy + vy * 26) * k)], fill=OL, width=_w(k, 2))


def c_head(d, k, nm, e, bl, look, T, speaking, *extra):
    P = lambda pts: R.P(pts, k)
    for ex in (140, 260):
        R.ell(d, k, (ex - 8, 100, ex + 8, 134), SK, OL, 3)
    shapes = [(142, 34, 258, 150), (152, 96, 248, 222)]
    for b in shapes:
        R.ell(d, k, (b[0] - 3, b[1] - 3, b[2] + 3, b[3] + 3), OL)
    for b in shapes:
        R.ell(d, k, b, SK)
    for y in (62, 72, 82):
        d.arc(((168 + OX) * k, y * k, (234 + OX) * k, (y + 14) * k), 200, 340, fill=OL, width=_w(k, 2))
    d.line(P([(156, 101), (176, 94), (196, 98)]), fill=OL, width=_w(k, 5), joint="curve")
    d.line(P([(206, 98), (226, 94), (246, 102)]), fill=OL, width=_w(k, 5), joint="curve")
    c = 0.42 + 0.58 * bl - (0.06 * (1 - bl) if speaking else 0)
    for ex in (176, 226):
        ey, rx, ry = 114, 17, 9
        R.ell(d, k, (ex - rx, ey - ry, ex + rx, ey + ry), (255, 255, 255), OL, 2)
        px = ex + max(-6, min(6, look * 0.8))
        R.ell(d, k, (px - 7, ey - 7, px + 7, ey + 7), (10, 10, 14))
        yl = ey - ry + 2 * ry * c
        pts = [(ex + rx * math.cos(math.radians(i)), min(ey + ry * math.sin(math.radians(i)), yl)) for i in range(0, 360, 10)]
        R.poly(d, pts, k, SK)
        d.line(P([(ex - rx - 1, yl), (ex + rx + 1, yl)]), fill=OL, width=_w(k, 3))
        d.arc(((ex - rx + OX) * k, (ey - ry) * k, (ex + rx + OX) * k, (ey + ry) * k), 0, 360, fill=OL, width=_w(k, 2))
        d.arc(((ex - 14 + OX) * k, (ey + 10) * k, (ex + 14 + OX) * k, (ey + 22) * k), 20, 160, fill=OL, width=_w(k, 2))
    d.line(P([(204, 118), (208, 140), (199, 148), (207, 150)]), fill=OL, width=_w(k, 3), joint="curve")
    cx = 203
    ho = e * 17 * (0.85 + 0.15 * math.sin(T * 23)) if speaking else 0
    if ho > 2:
        R.ell(d, k, (cx - 15, 168, cx + 15, 170 + ho), (40, 10, 14), OL, 2)
    else:
        d.line(P([(184, 177), (194, 173), (212, 173), (222, 178)]), fill=OL, width=_w(k, 3), joint="curve")
    d.arc(((190 + OX) * k, 190 * k, (216 + OX) * k, 204 * k), 200, 340, fill=OL, width=_w(k, 2))


def save_jpgs():
    os.makedirs("out", exist_ok=True)
    for nm in S.ORDER:
        r = R.portrait(nm, 900)
        bg = Image.new("RGB", r.size, (255, 255, 255))
        bg.paste(r, (0, 0), r)
        bg.save(f"out/friday_characters_{DISP[nm].lower()}.jpg", quality=92)


def pre():
    R.draw_torso, R.draw_arm, R.draw_head, R.save_jpgs = c_torso, c_arm, c_head, save_jpgs


# ======================= NAMES, TICKER (no LIVE), TABLE PLATES =======================
def name_card(nm, W, H):
    import fx as F
    from PIL import ImageFilter
    fs = int(H * 0.05) if W >= H else int(W * 0.075)
    f, f2 = S.font(fs), S.font(fs * 0.42)
    label = DISP[nm]
    w = int(max(f.getlength(label), f2.getlength(F.ROLE[nm]))) + 80
    h = int(fs * 2.0)
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text(((w - f.getlength(label)) / 2, 2), label, font=f, fill=S.COL[nm] + (255,))
    glow = lay.filter(ImageFilter.GaussianBlur(fs * 0.25))
    back = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(back).rounded_rectangle((0, 0, w - 1, h - 1), radius=14, fill=(0, 0, 0, 120))
    out = Image.alpha_composite(Image.alpha_composite(back, glow), glow)
    d = ImageDraw.Draw(out)
    d.text(((w - f.getlength(label)) / 2, 2), label, font=f, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255))
    d.text(((w - f2.getlength(F.ROLE[nm])) / 2, fs * 1.25), F.ROLE[nm], font=f2, fill=S.COL[nm] + (255,), stroke_width=1, stroke_fill=(0, 0, 0, 255))
    return out


def face(nm, h, emo="calm"):
    sp = emo == "shock"
    im = R.Rig(nm, int(h / 0.50)).frame(2.0 if sp else 1.0, sp, 0.9 if sp else 0.0, nm, 0, 0.0)
    im = im.crop((0, 0, im.width, int(im.height * 0.50)))
    bb = im.getchannel("A").getbbox()
    return im.crop(bb) if bb else im


def rebuild(cfg):
    import fx as F
    W, H = cfg["W"], cfg["H"]
    S.TABLE, S.PLATE = [], {}
    tx0 = int(W * 0.02)
    for by in sorted(set(s[1] for s in S.SEAT.values())):
        w = int(W * 0.96)
        strip = Image.new("RGBA", (w, S.TH), (0, 0, 0, 0))
        sd = ImageDraw.Draw(strip)
        sd.rounded_rectangle((0, 0, w - 1, S.TH - 1), radius=int(S.TH * .35), fill=(96, 62, 40, 255))
        sd.rectangle((10, 4, w - 11, 8), fill=(130, 90, 62, 255))
        ty = by - int(S.TH * 0.2)
        for n, (cx, b, _) in S.SEAT.items():
            if b != by:
                continue
            nf = S.font(S.TH * .42)
            tw = nf.getlength(DISP[n])
            cl = cx - tx0
            x0, y0, x1, y1 = cl - tw / 2 - 14, S.TH * .30, cl + tw / 2 + 14, S.TH * .88
            sd.rounded_rectangle((x0, y0, x1, y1), radius=8, fill=(20, 24, 38, 255), outline=S.COL[n], width=2)
            sd.text((cl - tw / 2, S.TH * .34), DISP[n], font=nf, fill=S.COL[n])
            S.PLATE[n] = (x0 + tx0, y0 + ty, x1 + tx0, y1 + ty)
        S.TABLE.append((strip, tx0, ty))
    hb = int(H * 0.045) if W >= H else int(H * 0.03)
    f = S.font(hb * 0.55)
    unit = "   •   " + cfg["topic"].upper()[:90] + "   •   MARKET DEBATE   •   RALLY vs SLUMP   "
    uw = int(f.getlength(unit)) + 1
    reps = int(W * 2 / uw) + 3
    S.TICK = Image.new("RGB", (uw * reps, hb), (14, 18, 32))
    ImageDraw.Draw(S.TICK).text((0, hb * 0.18), unit * reps, font=f, fill=(240, 240, 240))
    S.TICK_W = uw
    S.BADGE = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    hw = 0.13 * W if W >= H else 0.30 * W
    F.CLOSE = {n: R.Rig(n, int(540 * hw / 112)) for n in S.ORDER}


# ======================= SPOKEN TEXT / PROMPTS / SEO =======================
PHRASES = [("Bull and Crash", "Rally and Slump"), ("Bull vs Crash", "Rally vs Slump"),
           ("Bull (benefits), Crash (risks), Goldie (neutral), Cash (host)", "Rally (benefits), Slump (risks), Gauge (neutral), Ledger (host)"),
           ("Goldie keeps", "Gauge keeps"), ("the white host", "the host")]


def fwd(p):
    for a, b in PHRASES:
        p = p.replace(a, b)
    for k_, v in DISP.items():
        p = re.sub(r"\b%s\b" % k_, v, p)
    return p


CLOSING = [
    {"who": "GOLDIE", "text": "That's the full picture. Rally showed you the opportunity, Slump showed you the danger, and the smart move is to do your own research."},
    {"who": "GOLDIE", "text": "This show is for education only, not financial advice. If it helped you, subscribe, and tell us in the comments which side you were on."},
]


def texts():
    try:
        import brain as B
    except Exception:
        return
    ol, op = B.llm, B.parse
    B.llm = lambda p, *a, **kw: ol(fwd(p), *a, **kw)

    def parse(text, allowed):
        for k_, v in DISP.items():
            text = re.sub(r"(?im)^(\W*)%s(\W*[:：])" % v, r"\g<1>%s\g<2>" % k_, text)
        return op(text, allowed)
    B.parse = parse

    def intro_lines(topic, facts):
        t = B.llm("Write the opening monologue of CASH, the host who ONLY introduces the show. 6 to 8 lines, each starting with "
                  "'CASH:'. State today's topic, why it matters right now, 4 specific things viewers will learn, what the debate "
                  "will cover, and that this is education, not financial advice.\nTopic: %s\nFacts:\n%s" % (topic, facts), tokens=800)
        ls = B.parse(t, {"CASH"})
        if len(ls) < 3:
            ls = [{"who": "CASH", "text": "Welcome to the table. I'm Ledger, and I open the show. Today's topic: %s." % topic},
                  {"who": "CASH", "text": "In the next two hours you will learn what happened, why it matters, who benefits, who gets hurt, and how to think about it."},
                  {"who": "CASH", "text": "This is education, not financial advice."}]
        if "ledger" not in ls[0]["text"].lower():
            ls[0]["text"] = "Welcome to the table. I'm Ledger, the one in the blue-grey sweater, and my only job is to open the show. " + ls[0]["text"]
        return ls + [
            {"who": "CASH", "text": "Now let me introduce the rest of the table."},
            {"who": "GOLDIE", "text": "I'm Gauge, the one in the yellow sweater. I'm neutral. I ask the hard questions to both sides and I keep this debate honest."},
            {"who": "BULL", "text": "I'm Rally, the one in the green sweater. I bring the benefits, the opportunities and the upside of every story."},
            {"who": "CRASH", "text": "And I'm Slump, the one in the red sweater. I bring the harms, the risks and the warnings nobody wants to hear."},
            {"who": "CASH", "text": "That's the table. Gauge, it's all yours."},
            {"who": "GOLDIE", "text": "Thank you, Ledger. Rally, Slump, let's get started."}]
    B.intro_lines = intro_lines
    B.CLOSING = CLOSING
    if hasattr(B, "seo"):
        os_ = B.seo

        def seo(*a, **kw):
            t, d, g = os_(*a, **kw)
            return t.replace("Bull vs Crash", "Rally vs Slump"), d.replace("#bullvscrash", "#marketdebate"), g
        B.seo = seo


def post():
    import fx as F
    F.name_card, F.face = name_card, face
    sp = F.thumb_spec

    def spec(*a, **kw):
        r = sp(*a, **kw)
        if r["headline"] == "BULL VS CRASH":
            r["headline"] = "RALLY VS SLUMP"
            r["highlight"] = "SLUMP"
        return r
    F.thumb_spec = spec
    prev = S.init

    def init3(cfg):
        prev(cfg)
        rebuild(cfg)
    S.init = init3
    texts()
