"""Render docs/architecture.png from scratch with matplotlib.

The DevOps mini-project rubric requires an *image* for the architecture
diagram. The README references a mermaid block which does not satisfy
that, so this script produces a polished PNG with the same content.
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).with_name("architecture.png")

NAVY = "#0B2545"
TEAL = "#13315C"
ACCENT = "#8DA9C4"
LIGHT = "#EEF4ED"
GREEN = "#1B998B"
AMBER = "#E0A458"
RED = "#C03221"
TEXT = "#1A1A1A"


def box(ax, xy, w, h, label, fc, fg="white", fs=11, bold=True, radius=0.18):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        linewidth=1.4,
        edgecolor="#1a1a1a",
        facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(
        x + w / 2,
        y + h / 2,
        label,
        ha="center",
        va="center",
        color=fg,
        fontsize=fs,
        fontweight="bold" if bold else "normal",
    )
    return (x + w / 2, y + h / 2), (x, y, w, h)


def arrow(ax, p1, p2, label=None, color="#1a1a1a", style="-|>", ls="-", lw=1.6, rad=0.0):
    ar = FancyArrowPatch(
        p1,
        p2,
        arrowstyle=style,
        color=color,
        linewidth=lw,
        linestyle=ls,
        mutation_scale=18,
        connectionstyle=f"arc3,rad={rad}",
    )
    ax.add_patch(ar)
    if label:
        mx, my = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
        ax.text(
            mx,
            my + 0.18,
            label,
            ha="center",
            va="bottom",
            fontsize=8.5,
            color=color,
            fontstyle="italic",
        )


def main():
    fig, ax = plt.subplots(figsize=(13, 8.2), dpi=180)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 9)
    ax.set_aspect("equal")
    ax.axis("off")

    # Title
    ax.text(
        7,
        8.55,
        "SecureMLOps — CI/CD + Deployment Architecture",
        ha="center",
        va="center",
        fontsize=16,
        fontweight="bold",
        color=NAVY,
    )
    ax.text(
        7,
        8.18,
        "GitHub Actions · Docker · Trivy · Bandit · Gitleaks · pytest",
        ha="center",
        va="center",
        fontsize=10,
        color=TEAL,
        fontstyle="italic",
    )

    # Top row: Developer -> GitHub Repo -> GitHub Actions
    dev_c, _ = box(ax, (0.4, 6.6), 2.2, 1.0, "Developer", NAVY)
    repo_c, _ = box(ax, (3.4, 6.6), 2.6, 1.0, "GitHub Repo", TEAL)
    ga_c, _ = box(ax, (6.8, 6.6), 2.6, 1.0, "GitHub Actions", TEAL)
    secrets_c, _ = box(ax, (10.4, 6.6), 3.2, 1.0, "GitHub Secrets\nAPI_TOKEN", AMBER, fg="#1a1a1a")

    arrow(ax, (2.6, 7.1), (3.4, 7.1), label="git push")
    arrow(ax, (6.0, 7.1), (6.8, 7.1), label="webhook")

    # Pipeline frame
    frame = FancyBboxPatch(
        (0.6, 1.6),
        12.8,
        4.4,
        boxstyle="round,pad=0.05,rounding_size=0.3",
        linewidth=1.6,
        edgecolor=NAVY,
        facecolor=LIGHT,
    )
    ax.add_patch(frame)
    ax.text(
        7,
        5.7,
        "CI/CD Pipeline   (.github/workflows/ci.yml)",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color=NAVY,
    )

    # Four pipeline jobs
    job_y, job_h = 3.0, 1.9
    job_w = 2.7
    gap = 0.35
    start_x = 0.85

    def job(i, title, body, color):
        x = start_x + i * (job_w + gap)
        # White body first (drawn underneath)
        body_box = FancyBboxPatch(
            (x, job_y),
            job_w,
            job_h,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            linewidth=1.2,
            edgecolor="#1a1a1a",
            facecolor="white",
            zorder=1,
        )
        ax.add_patch(body_box)
        # Colored header bar on top
        hdr = FancyBboxPatch(
            (x, job_y + job_h - 0.55),
            job_w,
            0.55,
            boxstyle="round,pad=0.0,rounding_size=0.12",
            linewidth=1.2,
            edgecolor="#1a1a1a",
            facecolor=color,
            zorder=2,
        )
        ax.add_patch(hdr)
        ax.text(
            x + job_w / 2,
            job_y + job_h - 0.28,
            title,
            ha="center",
            va="center",
            fontsize=10.5,
            fontweight="bold",
            color="white",
            zorder=3,
        )
        ax.text(
            x + job_w / 2,
            job_y + (job_h - 0.55) / 2 + 0.05,
            body,
            ha="center",
            va="center",
            fontsize=9,
            color=TEXT,
            zorder=3,
        )
        return (x + job_w / 2, job_y + job_h / 2), (x, x + job_w)

    j1, span1 = job(0, "1. Build & Lint", "flake8\nblack --check\ntrain model\nupload model.joblib", NAVY)
    j2, span2 = job(1, "2. Test & Security", "pytest --cov\nBandit (SAST)\nGitleaks", TEAL)
    j3, span3 = job(2, "3. Docker + Trivy", "buildx + GHA cache\nTrivy CVE scan\nfail HIGH/CRITICAL", GREEN)
    j4, span4 = job(3, "4. Deploy", "if ref==main\ndocker run\nsmoke /health /predict", RED)

    # Arrows between jobs
    for src, dst in [(span1[1], span2[0]), (span2[1], span3[0]), (span3[1], span4[0])]:
        arrow(ax, (src, job_y + job_h / 2), (dst, job_y + job_h / 2), color=NAVY, lw=2.0)

    # GA -> pipeline frame
    arrow(ax, (8.1, 6.6), (8.1, 5.7), color=NAVY, lw=2.0)

    # Secrets -> Deploy job (dashed)
    arrow(ax, (12.0, 6.6), (12.0, 4.9), color=AMBER, ls="--", lw=1.8)

    # Bottom: deployed container
    cont_c, _ = box(ax, (4.6, 0.25), 4.8, 1.05, "Running Container :8000\n/health  ·  /predict", GREEN)

    # Pipeline -> container
    arrow(ax, (7.0, 1.6), (7.0, 1.3), color=NAVY, lw=2.0)

    # Legend
    legend_items = [
        mpatches.Patch(color=NAVY, label="Source / orchestration"),
        mpatches.Patch(color=TEAL, label="Test & static analysis"),
        mpatches.Patch(color=GREEN, label="Build/scan & deploy"),
        mpatches.Patch(color=AMBER, label="Secret material"),
        mpatches.Patch(color=RED, label="Gated stage (main only)"),
    ]
    ax.legend(
        handles=legend_items,
        loc="lower left",
        bbox_to_anchor=(0.0, -0.02),
        ncol=5,
        frameon=False,
        fontsize=8.5,
    )

    plt.tight_layout()
    fig.savefig(OUT, dpi=180, bbox_inches="tight", facecolor="white")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
