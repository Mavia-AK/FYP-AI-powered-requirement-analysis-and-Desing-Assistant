# app/ml/uml/diagram_renderer.py
"""
Clean UML Use Case diagram renderer.

Matches the target style:
  • Single column of ellipses on the RIGHT inside a titled system box
  • Stick-figure actors on the LEFT, stacked vertically
  • Plain lines from actor to each of their use-cases
  • Black & white, clean fonts — no colour fills
  • Title at top of system boundary box
"""

from __future__ import annotations
import io
import math
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle

# ── Style ─────────────────────────────────────────────────────────────────────
BLACK  = "#000000"
WHITE  = "#FFFFFF"
BOX_ED = "#222222"
UC_ED  = "#333333"

DPI        = 150
LABEL_WRAP = 22

# ── Layout constants ──────────────────────────────────────────────────────────
FIG_W        = 7.0
ACTOR_CX     = 1.05
SYS_LEFT     = 1.85
SYS_RIGHT    = FIG_W - 0.2
UC_CX        = (SYS_LEFT + SYS_RIGHT) / 2
UC_W         = 2.8
UC_H         = 0.42
UC_ROW_H     = 0.80
HEAD_R       = 0.13
ACTOR_BODY_H = 0.38
ACTOR_ARM_H  = 0.13
ACTOR_LEG    = 0.18
ACTOR_LABEL_OFF = 0.08


def _wrap(text: str, width: int = LABEL_WRAP) -> str:
    return "\n".join(textwrap.wrap(str(text), width))


def _draw_stick(ax, cx: float, cy: float, label: str, fs: float = 8.5) -> None:
    head_cy  = cy + ACTOR_BODY_H / 2 + ACTOR_LEG / 2 + HEAD_R
    body_top = head_cy - HEAD_R
    body_bot = body_top - ACTOR_BODY_H
    arm_y    = body_top - ACTOR_ARM_H
    leg_top  = body_bot

    head = Circle(
        (cx, head_cy), HEAD_R,
        fill=False, edgecolor=BLACK, linewidth=1.4, zorder=6
    )
    ax.add_patch(head)

    ax.plot([cx, cx], [body_top, body_bot],
            color=BLACK, lw=1.4, zorder=6, solid_capstyle="round")
    ax.plot([cx - 0.18, cx + 0.18], [arm_y, arm_y],
            color=BLACK, lw=1.4, zorder=6, solid_capstyle="round")
    ax.plot([cx, cx - 0.15], [leg_top, leg_top - ACTOR_LEG],
            color=BLACK, lw=1.4, zorder=6, solid_capstyle="round")
    ax.plot([cx, cx + 0.15], [leg_top, leg_top - ACTOR_LEG],
            color=BLACK, lw=1.4, zorder=6, solid_capstyle="round")

    label_y = leg_top - ACTOR_LEG - ACTOR_LABEL_OFF
    ax.text(cx, label_y, label,
            ha="center", va="top",
            fontsize=fs, color=BLACK,
            multialignment="center", zorder=7)


def draw_uml_diagram_png(uml_data: dict) -> bytes | None:
    actors       = uml_data.get("actors",        [])
    rels         = uml_data.get("relationships", [])
    actor_groups = uml_data.get("actor_groups",  {})
    use_cases    = uml_data.get("use_cases",     [])
    title        = uml_data.get("title",         "System")

    if not actors and not use_cases:
        return None

    # Build ordered actor → [use_cases] mapping
    ag: dict[str, list[str]] = {}
    for actor in actors:
        ucs = actor_groups.get(actor, [])
        if ucs:
            ag[actor] = list(ucs)

    if not ag:
        for rel in rels:
            ag.setdefault(rel["actor"], [])
            if rel["use_case"] not in ag[rel["actor"]]:
                ag[rel["actor"]].append(rel["use_case"])

    total_ucs = sum(len(v) for v in ag.values())
    if total_ucs == 0:
        return None

    # Figure height
    TITLE_H = 0.55
    TOP_PAD = 0.30
    BOT_PAD = 0.35
    fig_h   = TITLE_H + TOP_PAD + total_ucs * UC_ROW_H + BOT_PAD
    fig_h   = max(fig_h, 5.0)

    fig, ax = plt.subplots(figsize=(FIG_W, fig_h), dpi=DPI)
    ax.set_xlim(0, FIG_W)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.set_facecolor(WHITE)

    # System boundary box
    box_top = fig_h - 0.15
    box_bot = 0.15

    ax.add_patch(mpatches.FancyBboxPatch(
        (SYS_LEFT, box_bot),
        SYS_RIGHT - SYS_LEFT,
        box_top - box_bot,
        boxstyle="square,pad=0",
        linewidth=1.6,
        edgecolor=BOX_ED, facecolor=WHITE,
        zorder=1,
    ))

    # System title
    ax.text(
        (SYS_LEFT + SYS_RIGHT) / 2,
        box_top - 0.12,
        title,
        ha="center", va="top",
        fontsize=10, fontweight="bold", color=BLACK,
        zorder=10,
    )

    # Place use-cases top-to-bottom
    uc_y_start = box_top - TITLE_H
    uc_positions: dict[str, float] = {}
    actor_band:   dict[str, tuple[float, float]] = {}

    row = 0
    for actor in ag:
        ucs   = ag[actor]
        y_top = uc_y_start - row * UC_ROW_H
        for uc in ucs:
            yc = uc_y_start - row * UC_ROW_H - UC_ROW_H / 2
            uc_positions[uc] = yc
            row += 1
        y_bot = uc_y_start - row * UC_ROW_H
        actor_band[actor] = (y_top, y_bot)

    # Draw ellipses
    for uc, yc in uc_positions.items():
        ax.add_patch(mpatches.Ellipse(
            (UC_CX, yc), UC_W, UC_H,
            linewidth=1.2,
            edgecolor=UC_ED, facecolor=WHITE,
            zorder=5,
        ))
        ax.text(UC_CX, yc, _wrap(uc),
                ha="center", va="center",
                fontsize=8, color=BLACK,
                multialignment="center", zorder=6)

    # Draw actors and lines
    for actor, ucs in ag.items():
        y_top, y_bot = actor_band[actor]
        actor_cy = (y_top + y_bot) / 2

        _draw_stick(ax, ACTOR_CX, actor_cy, actor)

        conn_x = ACTOR_CX + 0.18
        conn_y = (
            actor_cy
            + ACTOR_BODY_H / 2
            + ACTOR_LEG / 2
            - ACTOR_ARM_H
        )

        for uc in ucs:
            if uc not in uc_positions:
                continue
            uc_yc = uc_positions[uc]
            uc_lx = UC_CX - UC_W / 2

            ax.plot(
                [conn_x, uc_lx],
                [conn_y, uc_yc],
                color=BLACK, lw=0.9, zorder=3,
                solid_capstyle="round",
            )

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI,
                bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()


# ── Mermaid HTML ──────────────────────────────────────────────────────────────

def build_mermaid_html(uml_data: dict) -> str:
    from app.ml.uml.plantuml_generator import generate_mermaid
    mermaid_code = generate_mermaid(uml_data)

    if not mermaid_code.strip():
        return (
            "<html><body>"
            "<p style='padding:20px;color:#555;'>No diagram data.</p>"
            "</body></html>"
        )

    # Build HTML using string concatenation to avoid f-string brace conflicts
    html = (
        "<!DOCTYPE html>\n"
        "<html>\n"
        "<head>\n"
        "  <meta charset=\"UTF-8\"/>\n"
        "  <script src=\"https://cdn.jsdelivr.net/npm/mermaid@10"
        "/dist/mermaid.min.js\"></script>\n"
        "  <style>\n"
        "    body {\n"
        "      margin: 0;\n"
        "      padding: 12px;\n"
        "      background: #ffffff;\n"
        "      font-family: 'Segoe UI', sans-serif;\n"
        "    }\n"
        "    .mermaid {\n"
        "      display: flex;\n"
        "      justify-content: center;\n"
        "      min-height: 300px;\n"
        "    }\n"
        "    svg { max-width: 100%; height: auto; }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <div class=\"mermaid\">" + mermaid_code + "</div>\n"
        "  <script>\n"
        "    mermaid.initialize({\n"
        "      startOnLoad: true,\n"
        "      theme: 'base',\n"
        "      themeVariables: {\n"
        "        primaryColor:       '#FFFFFF',\n"
        "        primaryTextColor:   '#000000',\n"
        "        primaryBorderColor: '#333333',\n"
        "        lineColor:          '#000000',\n"
        "        fontSize:           '13px',\n"
        "        fontFamily:         'Segoe UI, sans-serif'\n"
        "      },\n"
        "      flowchart: {\n"
        "        curve:       'linear',\n"
        "        nodeSpacing: 50,\n"
        "        rankSpacing: 100,\n"
        "        padding:     20\n"
        "      }\n"
        "    });\n"
        "  </script>\n"
        "</body>\n"
        "</html>"
    )
    return html