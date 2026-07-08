#!/usr/bin/env python3
"""
Generate missing minimal flat Git deck icons (PIL).
Style: bold black outlines, limited palette, white background — matches existing git-deck assets.
"""

from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path("assets/images/git-deck")
SIZE = 512

# Limited flat palette (24-color style)
BLACK = (20, 20, 20)
WHITE = (255, 255, 255)
PURPLE = (130, 90, 200)
BLUE = (55, 120, 215)
LIGHT_BLUE = (100, 185, 255)
TEAL = (55, 175, 165)
GREEN = (95, 195, 75)
LIME = (125, 210, 35)
ORANGE = (255, 135, 55)
RED = (235, 85, 85)
YELLOW = (255, 215, 75)
BROWN = (155, 95, 55)
GRAY = (175, 175, 175)
PINK = (255, 150, 180)


def canvas():
    img = Image.new("RGB", (SIZE, SIZE), WHITE)
    return img, ImageDraw.Draw(img)


def stroke(draw, width=5):
    return {"outline": BLACK, "width": width}


def folder(draw, xy, color=TEAL, open_flap=True):
    x, y, w, h = xy
    draw.rounded_rectangle([x, y + 20, x + w, y + h], 12, fill=color, **stroke(draw))
    if open_flap:
        draw.polygon(
            [(x, y + 20), (x + 40, y + 20), (x + 55, y), (x + w - 20, y), (x + w, y + 20)],
            fill=color,
            **stroke(draw),
        )


def cloud(draw, cx, cy, scale=1.0, color=LIGHT_BLUE):
    r = int(28 * scale)
    blobs = [
        (cx - r, cy, r),
        (cx, cy - int(12 * scale), int(r * 1.1)),
        (cx + r, cy, r),
        (cx + int(15 * scale), cy + int(10 * scale), int(r * 0.85)),
    ]
    for bx, by, br in blobs:
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=color, **stroke(draw, 4))


def arrow(draw, start, end, color=ORANGE, width=14):
    draw.line([start, end], fill=color, width=width)
    ex, ey = end
    sx, sy = start
    import math

    ang = math.atan2(ey - sy, ex - sx)
    a1, a2 = ang + 2.6, ang - 2.6
    L = 22
    p1 = (ex + L * math.cos(a1), ey + L * math.sin(a1))
    p2 = (ex + L * math.cos(a2), ey + L * math.sin(a2))
    draw.polygon([end, p1, p2], fill=color, outline=BLACK)


def person(draw, cx, cy, shirt=PURPLE):
    draw.ellipse([cx - 35, cy - 80, cx + 35, cy - 10], fill=YELLOW, **stroke(draw))
    draw.ellipse([cx - 28, cy - 72, cx - 8, cy - 52], fill=BLACK)
    draw.ellipse([cx + 8, cy - 72, cx + 28, cy - 52], fill=BLACK)
    draw.arc([cx - 15, cy - 45, cx + 15, cy - 25], 20, 160, fill=BLACK, width=4)
    draw.rounded_rectangle([cx - 45, cy - 5, cx + 45, cy + 90], 18, fill=shirt, **stroke(draw))


# ── Icon builders ──────────────────────────────────────────────

def icon_config_name():
    img, d = canvas()
    person(d, 200, 280)
    d.rounded_rectangle([300, 140, 430, 220], 10, fill=YELLOW, **stroke(d))
    d.line([(320, 175), (410, 175)], fill=BLACK, width=4)
    d.line([(320, 195), (390, 195)], fill=BLACK, width=4)
    return img


def icon_config_email():
    img, d = canvas()
    d.polygon([(120, 160), (392, 160), (392, 340), (120, 340)], fill=LIGHT_BLUE, **stroke(d))
    d.polygon([(120, 160), (256, 260), (392, 160)], fill=BLUE, **stroke(d, 4))
    d.ellipse([300, 200, 370, 270], fill=WHITE, **stroke(d, 4))
    d.line([(315, 250), (340, 225), (355, 250)], fill=RED, width=5)
    return img


def icon_gitconfig():
    img, d = canvas()
    d.rounded_rectangle([140, 120, 380, 380], 16, fill=WHITE, **stroke(d))
    for i, txt in enumerate(["user.name=...", "user.email=...", "[core]"]):
        d.line([(170, 170 + i * 55), (350, 170 + i * 55)], fill=GRAY, width=6)
    cx, cy = 330, 330
    d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], fill=ORANGE, **stroke(d))
    for i in range(8):
        import math
        a = i * math.pi / 4
        d.rectangle(
            [cx + 34 * math.cos(a) - 8, cy + 34 * math.sin(a) - 8,
             cx + 34 * math.cos(a) + 8, cy + 34 * math.sin(a) + 8],
            fill=ORANGE, outline=BLACK,
        )
    return img


def icon_worktree_add():
    img, d = canvas()
    folder(d, (80, 200, 150, 130), TEAL)
    folder(d, (280, 200, 150, 130), BLUE)
    d.ellipse([215, 215, 265, 265], fill=GREEN, **stroke(d))
    d.line([(240, 228), (240, 252)], fill=WHITE, width=6)
    d.line([(228, 240), (252, 240)], fill=WHITE, width=6)
    arrow(d, (230, 265), (280, 265), ORANGE)
    return img


def icon_worktree_safe():
    img, d = canvas()
    d.rounded_rectangle([60, 180, 220, 380], 10, fill=WHITE, **stroke(d, 3))
    d.setdash = None
    for i in range(0, 520, 18):
        d.line([(60, i), (60, min(i + 9, 520))], fill=GRAY, width=3)
    folder(d, (300, 200, 150, 130), TEAL)
    d.polygon([(350, 120), (400, 170), (380, 170), (380, 230), (320, 230), (320, 170), (300, 170)], fill=GREEN, **stroke(d))
    return img


def icon_worktree_list():
    img, d = canvas()
    for i, c in enumerate([TEAL, BLUE, PURPLE]):
        folder(d, (100, 120 + i * 110, 120, 90), c)
        d.line([(250, 155 + i * 110), (400, 155 + i * 110)], fill=BLACK, width=5)
        d.line([(250, 175 + i * 110), (370, 175 + i * 110)], fill=GRAY, width=4)
    return img


def icon_gitignore_worktree():
    img, d = canvas()
    folder(d, (120, 160, 200, 150), TEAL)
    d.rounded_rectangle([280, 200, 400, 280], 10, fill=BROWN, **stroke(d))
    d.line([(295, 215), (385, 265)], fill=RED, width=8)
    d.line([(385, 215), (295, 265)], fill=RED, width=8)
    d.text((285, 295), "node", fill=BLACK) if False else None
    d.ellipse([290, 300, 390, 340], fill=GRAY, **stroke(d, 3))
    return img


def icon_worktree_remove():
    img, d = canvas()
    folder(d, (160, 180, 180, 150), TEAL)
    d.ellipse([300, 220, 380, 300], fill=RED, **stroke(d))
    d.line([(320, 260), (360, 260)], fill=WHITE, width=8)
    return img


def icon_worktree_blocked():
    img, d = canvas()
    folder(d, (140, 200, 160, 130), TEAL)
    d.rounded_rectangle([300, 180, 400, 300], 14, fill=YELLOW, **stroke(d))
    d.arc([330, 220, 370, 290], 0, 360, fill=BLACK, width=6)
    d.rectangle([345, 250, 355, 310], fill=BLACK)
    return img


def icon_worktree_force():
    img, d = canvas()
    folder(d, (140, 220, 150, 120), TEAL)
    d.polygon([(330, 120), (370, 220), (350, 220), (380, 320), (340, 250), (360, 250), (310, 120)], fill=ORANGE, **stroke(d))
    return img


def icon_worktree_prune():
    img, d = canvas()
    d.line([(200, 340), (200, 140)], fill=BROWN, width=10)
    d.ellipse([150, 100, 250, 180], fill=GREEN, **stroke(d))
    d.line([(160, 380), (240, 380)], fill=GRAY, width=8)
    d.line([(280, 360), (400, 240)], fill=RED, width=6)
    d.line([(280, 240), (400, 360)], fill=RED, width=6)
    return img


def icon_worktree_branch_block():
    img, d = canvas()
    d.line([(120, 360), (280, 200)], fill=BROWN, width=8)
    d.line([(280, 200), (400, 260)], fill=GREEN, width=8)
    d.ellipse([270, 190, 290, 210], fill=GREEN, **stroke(d, 3))
    d.line([(350, 150), (430, 230)], fill=RED, width=10)
    d.line([(430, 150), (350, 230)], fill=RED, width=10)
    return img


def icon_worktree_one_branch():
    img, d = canvas()
    folder(d, (80, 220, 120, 100), TEAL)
    folder(d, (300, 220, 120, 100), BLUE)
    d.line([(200, 270), (300, 270)], fill=GREEN, width=8)
    d.line([(250, 120), (330, 200)], fill=RED, width=12)
    d.line([(330, 120), (250, 200)], fill=RED, width=12)
    return img


def icon_diff_staged():
    img, d = canvas()
    d.rounded_rectangle([80, 140, 220, 380], 12, fill=YELLOW, **stroke(d))
    d.rounded_rectangle([290, 140, 430, 380], 12, fill=LIGHT_BLUE, **stroke(d))
    for i in range(4):
        c = RED if i % 2 else GREEN
        d.line([(100, 180 + i * 45), (200, 180 + i * 45)], fill=c, width=6)
        d.line([(310, 180 + i * 45), (410, 180 + i * 45)], fill=c, width=6)
    arrow(d, (230, 260), (280, 260), ORANGE, 10)
    return img


def icon_log_oneline():
    img, d = canvas()
    d.line([(120, 400), (120, 120)], fill=BROWN, width=8)
    for i, c in enumerate([BLUE, TEAL, PURPLE, ORANGE]):
        y = 150 + i * 60
        d.ellipse([100, y, 140, y + 40], fill=c, **stroke(d, 3))
        d.line([(150, y + 20), (400, y + 20)], fill=BLACK, width=4)
    return img


def icon_show():
    img, d = canvas()
    d.rounded_rectangle([140, 200, 380, 360], 14, fill=LIGHT_BLUE, **stroke(d))
    d.line([(170, 240), (350, 240)], fill=BLACK, width=5)
    d.line([(170, 280), (320, 280)], fill=GRAY, width=4)
    d.ellipse([300, 120, 400, 220], fill=WHITE, **stroke(d, 6))
    d.ellipse([330, 150, 370, 190], fill=LIGHT_BLUE, **stroke(d, 4))
    d.line([(370, 200), (420, 250)], fill=BROWN, width=8)
    return img


def icon_branch_create():
    img, d = canvas()
    d.line([(120, 380), (260, 200)], fill=BROWN, width=10)
    d.line([(260, 200), (400, 280)], fill=GREEN, width=8)
    d.ellipse([250, 190, 270, 210], fill=GREEN, **stroke(d, 3))
    d.ellipse([330, 240, 370, 280], fill=GREEN, **stroke(d))
    d.line([(350, 260), (350, 300)], fill=WHITE, width=6)
    d.line([(330, 280), (370, 280)], fill=WHITE, width=6)
    return img


def icon_checkout():
    img, d = canvas()
    d.line([(100, 350), (250, 180)], fill=BROWN, width=10)
    d.line([(250, 180), (400, 250)], fill=GREEN, width=8)
    d.line([(250, 180), (400, 120)], fill=BLUE, width=8)
    d.ellipse([240, 170, 260, 190], fill=GREEN, **stroke(d, 3))
    arrow(d, (300, 300), (380, 200), ORANGE)
    return img


def icon_checkout_b():
    img, d = canvas()
    d.line([(100, 360), (240, 200)], fill=BROWN, width=10)
    d.line([(240, 200), (380, 280)], fill=GREEN, width=8)
    d.line([(240, 200), (380, 140)], fill=BLUE, width=8)
    d.ellipse([370, 130, 400, 160], fill=BLUE, **stroke(d))
    d.line([(383, 140), (383, 155)], fill=WHITE, width=4)
    d.line([(375, 147), (391, 147)], fill=WHITE, width=4)
    arrow(d, (260, 320), (360, 160), ORANGE)
    return img


def icon_merge():
    img, d = canvas()
    d.line([(100, 300), (256, 180)], fill=GREEN, width=8)
    d.line([(400, 300), (256, 180)], fill=BLUE, width=8)
    d.line([(256, 180), (256, 380)], fill=BROWN, width=10)
    d.ellipse([246, 370, 266, 390], fill=BROWN, **stroke(d, 3))
    return img


def icon_branch_d():
    img, d = canvas()
    d.line([(120, 380), (280, 200)], fill=BROWN, width=10)
    d.line([(280, 200), (400, 260)], fill=GREEN, width=8)
    d.ellipse([270, 190, 290, 210], fill=GREEN, **stroke(d, 3))
    d.rounded_rectangle([320, 300, 400, 360], 10, fill=ORANGE, **stroke(d))
    d.text((340, 310), "d") if False else d.line([(345, 315), (345, 345)], fill=BLACK, width=5)
    return img


def icon_branch_D():
    img, d = canvas()
    d.line([(120, 380), (280, 200)], fill=BROWN, width=10)
    d.line([(280, 200), (400, 260)], fill=RED, width=8)
    d.ellipse([270, 190, 290, 210], fill=RED, **stroke(d, 3))
    d.rounded_rectangle([310, 290, 410, 370], 10, fill=RED, **stroke(d))
    d.line([(330, 310), (330, 350)], fill=WHITE, width=8)
    d.line([(350, 310), (350, 350)], fill=WHITE, width=8)
    return img


def icon_restore():
    img, d = canvas()
    d.rounded_rectangle([180, 180, 340, 300], 10, fill=LIGHT_BLUE, **stroke(d))
    d.arc([220, 100, 360, 240], 30, 200, fill=ORANGE, width=12)
    d.polygon([(220, 130), (200, 100), (250, 110)], fill=ORANGE, outline=BLACK)
    return img


def icon_restore_staged():
    img, d = canvas()
    d.rounded_rectangle([100, 120, 400, 200], 12, fill=YELLOW, **stroke(d))
    d.rounded_rectangle([180, 280, 320, 380], 12, fill=TEAL, **stroke(d))
    arrow(d, (250, 260), (250, 220), RED)
    return img


def icon_commit_amend():
    img, d = canvas()
    d.rounded_rectangle([120, 200, 400, 340], 16, fill=PURPLE, **stroke(d))
    d.line([(150, 250), (370, 250)], fill=WHITE, width=5)
    d.polygon([(300, 120), (380, 160), (340, 160), (360, 220), (300, 180), (320, 180)], fill=YELLOW, **stroke(d))
    return img


def icon_reset_soft():
    img, d = canvas()
    d.rounded_rectangle([280, 160, 400, 240], 14, fill=PURPLE, **stroke(d))
    d.rounded_rectangle([120, 280, 260, 360], 14, fill=YELLOW, **stroke(d))
    arrow(d, (280, 200), (200, 200), ORANGE)
    d.line([(150, 310), (230, 310)], fill=TEAL, width=6)
    return img


def icon_revert():
    img, d = canvas()
    d.rounded_rectangle([140, 220, 300, 300], 12, fill=RED, **stroke(d))
    d.rounded_rectangle([220, 140, 380, 220], 12, fill=GREEN, **stroke(d))
    arrow(d, (220, 260), (300, 200), BLUE)
    d.line([(300, 200), (340, 200)], fill=BLUE, width=6)
    return img


def icon_remote_add():
    img, d = canvas()
    cloud(d, 300, 180, 1.2, LIGHT_BLUE)
    d.ellipse([150, 280, 230, 360], fill=GREEN, **stroke(d))
    d.line([(190, 305), (190, 335)], fill=WHITE, width=6)
    d.line([(175, 320), (205, 320)], fill=WHITE, width=6)
    arrow(d, (230, 320), (250, 250), ORANGE)
    return img


def icon_fetch():
    img, d = canvas()
    cloud(d, 280, 160, 1.1)
    folder(d, (140, 260, 160, 120), TEAL)
    arrow(d, (280, 200), (220, 280), BLUE)
    d.line([(220, 280), (220, 310)], fill=BLACK, width=4)
    d.line([(200, 310), (240, 310)], fill=BLACK, width=4)
    return img


def icon_push_u():
    img, d = canvas()
    folder(d, (100, 260, 140, 110), TEAL)
    cloud(d, 340, 180)
    arrow(d, (250, 300), (300, 220), ORANGE)
    d.ellipse([230, 320, 270, 360], fill=YELLOW, **stroke(d))
    d.arc([235, 325, 265, 355], 30, 330, fill=BLACK, width=4)
    return img


def icon_stash_list():
    img, d = canvas()
    for i, c in enumerate([TEAL, BLUE, PURPLE]):
        d.rounded_rectangle([140, 280 - i * 50, 380, 330 - i * 50], 10, fill=c, **stroke(d))
    for i in range(3):
        d.line([(400, 150 + i * 40), (450, 150 + i * 40)], fill=BLACK, width=4)
    return img


def icon_stash_pop():
    img, d = canvas()
    d.rounded_rectangle([120, 160, 360, 240], 12, fill=BLUE, **stroke(d))
    d.rounded_rectangle([140, 240, 340, 300], 12, fill=TEAL, **stroke(d))
    d.rounded_rectangle([180, 300, 300, 380], 14, fill=ORANGE, **stroke(d))
    arrow(d, (240, 300), (240, 220), GREEN)
    return img


def icon_filter_repo():
    img, d = canvas()
    d.polygon([(200, 100), (320, 100), (360, 200), (160, 200)], fill=GRAY, **stroke(d))
    d.rectangle([170, 200, 350, 220], fill=GRAY, **stroke(d, 3))
    d.ellipse([220, 260, 300, 340], fill=RED, **stroke(d))
    d.line([(180, 380), (340, 260)], fill=BLACK, width=5)
    return img


def icon_non_fast_forward():
    img, d = canvas()
    cloud(d, 320, 160)
    folder(d, (100, 260, 130, 100), TEAL)
    arrow(d, (240, 300), (290, 220), ORANGE)
    d.line([(300, 200), (380, 280)], fill=RED, width=14)
    d.line([(380, 200), (300, 280)], fill=RED, width=14)
    return img


def icon_non_fast_forward_alt():
    """Card 50 — same concept, distinct composition from 049."""
    img, d = canvas()
    d.line([(100, 300), (400, 300)], fill=BROWN, width=8)
    d.ellipse([180, 280, 220, 320], fill=BLUE, **stroke(d))
    d.ellipse([300, 280, 340, 320], fill=GREEN, **stroke(d))
    arrow(d, (220, 260), (300, 260), ORANGE)
    d.line([(310, 220), (390, 300)], fill=RED, width=12)
    d.line([(390, 220), (310, 300)], fill=RED, width=12)
    return img


ICON_MAP = {
    "git-009-config-name.png": icon_config_name,
    "git-010-config-email.png": icon_config_email,
    "git-011-gitconfig.png": icon_gitconfig,
    "git-014-worktree-add.png": icon_worktree_add,
    "git-015-worktree-safe.png": icon_worktree_safe,
    "git-016-worktree-list.png": icon_worktree_list,
    "git-017-gitignore-worktree.png": icon_gitignore_worktree,
    "git-018-worktree-remove.png": icon_worktree_remove,
    "git-019-worktree-blocked.png": icon_worktree_blocked,
    "git-020-worktree-force.png": icon_worktree_force,
    "git-021-worktree-prune.png": icon_worktree_prune,
    "git-022-worktree-branch-block.png": icon_worktree_branch_block,
    "git-023-worktree-one-branch.png": icon_worktree_one_branch,
    "git-024-diff-staged.png": icon_diff_staged,
    "git-026-log-oneline.png": icon_log_oneline,
    "git-027-show.png": icon_show,
    "git-029-branch-create.png": icon_branch_create,
    "git-030-checkout.png": icon_checkout,
    "git-031-checkout-b.png": icon_checkout_b,
    "git-032-merge.png": icon_merge,
    "git-033-branch-d.png": icon_branch_d,
    "git-034-branch-D.png": icon_branch_D,
    "git-035-restore.png": icon_restore,
    "git-036-restore-staged.png": icon_restore_staged,
    "git-037-commit-amend.png": icon_commit_amend,
    "git-038-reset-soft.png": icon_reset_soft,
    "git-040-revert.png": icon_revert,
    "git-042-remote-add.png": icon_remote_add,
    "git-043-fetch.png": icon_fetch,
    "git-044-push-u.png": icon_push_u,
    "git-046-stash-list.png": icon_stash_list,
    "git-047-stash-pop.png": icon_stash_pop,
    "git-048-filter-repo.png": icon_filter_repo,
    "git-049-non-fast-forward.png": icon_non_fast_forward,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    created = 0
    for name, builder in ICON_MAP.items():
        path = OUT / name
        if path.exists():
            print(f"  skip (exists): {name}")
            continue
        builder().save(path, "PNG")
        print(f"  ✓ {name}")
        created += 1
    print(f"\nGenerated {created} new icons in {OUT}")


if __name__ == "__main__":
    main()