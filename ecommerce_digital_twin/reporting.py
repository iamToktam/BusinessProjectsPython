"""Chart generation (matplotlib) and 1-page PDF reporting (fpdf2)."""

from pathlib import Path

import matplotlib
from fpdf import FPDF
from fpdf.enums import XPos, YPos

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from store_twin import StoreDigitalTwin  # noqa: E402

BASELINE_COLOR = "#2563EB"
PROMO_COLOR = "#10B981"
ALERT_COLOR = "#DC2626"
NAVY_RGB = (24, 49, 83)
LIGHT_BG_RGB = (241, 245, 249)
BORDER_RGB = (203, 213, 225)
TEXT_RGB = (30, 41, 59)
MUTED_RGB = (100, 116, 139)


def _add_bar_labels(ax: plt.Axes, bars, fmt: str) -> None:
    """Attach value labels neatly above each bar."""
    for bar in bars:
        height = bar.get_height()
        ax.annotate(
            fmt.format(height),
            xy=(bar.get_x() + bar.get_width() / 2, height),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color="#1E293B",
        )


def generate_charts(
    baseline_twin: StoreDigitalTwin,
    promo_twin: StoreDigitalTwin,
    output_path: Path,
) -> Path:
    """Create a 2-panel comparison chart image and save it as PNG."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    base_summary = baseline_twin.get_summary()
    promo_summary = promo_twin.get_summary()

    fig, (ax_fin, ax_stock) = plt.subplots(1, 2, figsize=(10.5, 4.2), dpi=180)
    fig.patch.set_facecolor("white")

    # Panel 1: Financial KPI comparison
    metrics = ["Revenue", "Cost", "Net Profit"]
    base_values = [
        base_summary["total_revenue"],
        base_summary["total_cost"],
        base_summary["net_profit"],
    ]
    promo_values = [
        promo_summary["total_revenue"],
        promo_summary["total_cost"],
        promo_summary["net_profit"],
    ]

    x_fin = list(range(len(metrics)))
    bar_width = 0.36
    bars_base = ax_fin.bar(
        [x - bar_width / 2 for x in x_fin],
        base_values,
        width=bar_width,
        label="Baseline (0% Off)",
        color=BASELINE_COLOR,
    )
    bars_promo = ax_fin.bar(
        [x + bar_width / 2 for x in x_fin],
        promo_values,
        width=bar_width,
        label="What-If (10% Off)",
        color=PROMO_COLOR,
    )

    _add_bar_labels(ax_fin, bars_base, "${:.2f}")
    _add_bar_labels(ax_fin, bars_promo, "${:.2f}")

    ax_fin.set_title("Financial Comparison", fontsize=11, fontweight="bold")
    ax_fin.set_ylabel("USD ($)", fontsize=9)
    ax_fin.set_xticks(x_fin)
    ax_fin.set_xticklabels(metrics, fontsize=9)
    ax_fin.set_ylim(0, max(base_values + promo_values) * 1.18)
    ax_fin.grid(axis="y", linestyle="--", alpha=0.4)
    ax_fin.spines["top"].set_visible(False)
    ax_fin.spines["right"].set_visible(False)
    ax_fin.legend(frameon=False, fontsize=8)

    # Panel 2: Remaining inventory vs. reorder levels
    skus = list(baseline_twin.inventory.keys())
    labels = [
        baseline_twin.inventory[sku].name.replace(" ", "\n")
        for sku in skus
    ]
    base_stock = [baseline_twin.inventory[sku].stock for sku in skus]
    promo_stock = [promo_twin.inventory[sku].stock for sku in skus]
    reorder_levels = [
        baseline_twin.inventory[sku].reorder_level for sku in skus
    ]

    x_stock = list(range(len(skus)))
    bars_s_base = ax_stock.bar(
        [x - bar_width / 2 for x in x_stock],
        base_stock,
        width=bar_width,
        label="Baseline Stock",
        color=BASELINE_COLOR,
    )
    bars_s_promo = ax_stock.bar(
        [x + bar_width / 2 for x in x_stock],
        promo_stock,
        width=bar_width,
        label="Promo Stock",
        color=PROMO_COLOR,
    )
    ax_stock.plot(
        x_stock,
        reorder_levels,
        color=ALERT_COLOR,
        marker="o",
        linestyle="--",
        linewidth=1.5,
        label="Reorder Level",
    )

    _add_bar_labels(ax_stock, bars_s_base, "{:.0f}")
    _add_bar_labels(ax_stock, bars_s_promo, "{:.0f}")

    ax_stock.set_title(
        "Remaining Inventory After Simulation",
        fontsize=11,
        fontweight="bold",
    )
    ax_stock.set_ylabel("Units", fontsize=9)
    ax_stock.set_xticks(x_stock)
    ax_stock.set_xticklabels(labels, fontsize=8)
    ax_stock.set_ylim(0, max(base_stock + promo_stock + reorder_levels) + 3)
    ax_stock.grid(axis="y", linestyle="--", alpha=0.4)
    ax_stock.spines["top"].set_visible(False)
    ax_stock.spines["right"].set_visible(False)
    ax_stock.legend(frameon=False, fontsize=8)

    plt.tight_layout(pad=1.6)
    fig.savefig(output_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    return output_path


def _draw_kpi_card(
    pdf: FPDF,
    x: float,
    y: float,
    width: float,
    height: float,
    label: str,
    value: str,
    accent_rgb: tuple[int, int, int],
) -> None:
    """Draw a compact KPI summary card at the given coordinates."""
    pdf.set_fill_color(*LIGHT_BG_RGB)
    pdf.set_draw_color(*BORDER_RGB)
    pdf.rect(x, y, width, height, style="DF")

    pdf.set_fill_color(*accent_rgb)
    pdf.rect(x, y, 2.2, height, style="F")

    pdf.set_xy(x + 5, y + 3)
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*MUTED_RGB)
    pdf.cell(width - 7, 5, label)

    pdf.set_xy(x + 5, y + 9)
    pdf.set_font("Helvetica", style="B", size=13)
    pdf.set_text_color(*accent_rgb)
    pdf.cell(width - 7, 7, value)


def generate_pdf_report(
    baseline_twin: StoreDigitalTwin,
    promo_twin: StoreDigitalTwin,
    chart_path: Path,
    pdf_path: Path,
) -> Path:
    """Build a clean, single-page A4 PDF executive report."""
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    base_summary = baseline_twin.get_summary()
    promo_summary = promo_twin.get_summary()
    profit_diff = round(
        promo_summary["net_profit"] - base_summary["net_profit"],
        2,
    )
    sign = "+" if profit_diff >= 0 else "-"
    diff_text = f"{sign}${abs(profit_diff):.2f}"
    diff_rgb = (16, 130, 90) if profit_diff >= 0 else (200, 38, 38)

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)
    pdf.set_margins(left=14, top=14, right=14)
    pdf.add_page()

    page_width = 210 - 28

    # Header banner
    pdf.set_fill_color(*NAVY_RGB)
    pdf.rect(0, 0, 210, 30, style="F")
    pdf.set_xy(14, 7)
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(
        page_width,
        8,
        f"{baseline_twin.store_name} - Digital Twin Report",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_x(14)
    pdf.set_font("Helvetica", size=9.5)
    pdf.set_text_color(210, 224, 240)
    pdf.cell(
        page_width,
        6,
        "Scenario Analysis: Baseline (0% Discount) vs. "
        "What-If Campaign (10% Discount)",
    )

    # KPI highlight cards
    card_y = 36
    card_gap = 5
    card_w = (page_width - 2 * card_gap) / 3
    card_h = 19

    _draw_kpi_card(
        pdf,
        14,
        card_y,
        card_w,
        card_h,
        "Baseline Net Profit",
        f"${base_summary['net_profit']:.2f}",
        (37, 99, 235),
    )
    _draw_kpi_card(
        pdf,
        14 + card_w + card_gap,
        card_y,
        card_w,
        card_h,
        "What-If Promo Net Profit",
        f"${promo_summary['net_profit']:.2f}",
        (16, 130, 90),
    )
    _draw_kpi_card(
        pdf,
        14 + 2 * (card_w + card_gap),
        card_y,
        card_w,
        card_h,
        "Net Profit Impact",
        diff_text,
        diff_rgb,
    )

    # Scenario comparison table
    pdf.set_xy(14, 61)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.set_text_color(*NAVY_RGB)
    pdf.cell(
        page_width,
        7,
        "1. Operational & Financial Summary",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    col_widths = [66, 58, 58]
    headers = ["Metric", "Baseline (0% Off)", "What-If (10% Off)"]
    pdf.set_fill_color(*NAVY_RGB)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", style="B", size=9)
    for col_w, heading in zip(col_widths, headers):
        pdf.cell(col_w, 7.5, heading, border=0, align="C", fill=True)
    pdf.ln()

    rows = [
        (
            "Total Orders",
            str(base_summary["total_orders"]),
            str(promo_summary["total_orders"]),
        ),
        (
            "Fulfilled / Failed Orders",
            f"{base_summary['fulfilled_orders']} / "
            f"{base_summary['failed_orders']}",
            f"{promo_summary['fulfilled_orders']} / "
            f"{promo_summary['failed_orders']}",
        ),
        (
            "Total Revenue",
            f"${base_summary['total_revenue']:.2f}",
            f"${promo_summary['total_revenue']:.2f}",
        ),
        (
            "Total Cost",
            f"${base_summary['total_cost']:.2f}",
            f"${promo_summary['total_cost']:.2f}",
        ),
        (
            "Net Profit",
            f"${base_summary['net_profit']:.2f}",
            f"${promo_summary['net_profit']:.2f}",
        ),
    ]

    pdf.set_draw_color(*BORDER_RGB)
    for idx, row in enumerate(rows):
        is_last = idx == len(rows) - 1
        fill_rgb = LIGHT_BG_RGB if idx % 2 == 1 else (255, 255, 255)
        pdf.set_fill_color(*fill_rgb)
        pdf.set_text_color(*TEXT_RGB)
        pdf.set_font("Helvetica", style="B" if is_last else "", size=9)
        pdf.cell(
            col_widths[0],
            6.8,
            f"  {row[0]}",
            border="B",
            align="L",
            fill=True,
        )
        pdf.cell(col_widths[1], 6.8, row[1], border="B", align="C", fill=True)
        pdf.cell(col_widths[2], 6.8, row[2], border="B", align="C", fill=True)
        pdf.ln()

    # Embedded charts
    pdf.set_xy(14, 114)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.set_text_color(*NAVY_RGB)
    pdf.cell(
        page_width,
        7,
        "2. Visual Analytics",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.image(str(chart_path), x=14, y=122, w=page_width)

    # Restock alerts section
    pdf.set_xy(14, 200)
    pdf.set_font("Helvetica", style="B", size=11)
    pdf.set_text_color(*NAVY_RGB)
    pdf.cell(
        page_width,
        7,
        "3. Inventory Restock Alerts",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )

    sections = [
        ("Baseline Scenario", baseline_twin.get_low_stock_products()),
        ("What-If Promo Scenario", promo_twin.get_low_stock_products()),
    ]
    col_x = [14, 14 + page_width / 2 + 3]
    box_w = page_width / 2 - 3
    box_y = 208
    box_h = 54

    for idx, (section_title, low_items) in enumerate(sections):
        x_pos = col_x[idx]
        pdf.set_fill_color(*LIGHT_BG_RGB)
        pdf.set_draw_color(*BORDER_RGB)
        pdf.rect(x_pos, box_y, box_w, box_h, style="DF")

        pdf.set_xy(x_pos + 4, box_y + 3)
        pdf.set_font("Helvetica", style="B", size=9.5)
        pdf.set_text_color(*NAVY_RGB)
        pdf.cell(box_w - 8, 6, section_title)

        pdf.set_font("Helvetica", size=8.5)
        pdf.set_text_color(*TEXT_RGB)
        cursor_y = box_y + 11
        if not low_items:
            pdf.set_xy(x_pos + 4, cursor_y)
            pdf.cell(box_w - 8, 6, "All products are sufficiently stocked.")
        else:
            for item in low_items:
                pdf.set_xy(x_pos + 4, cursor_y)
                pdf.cell(
                    box_w - 8,
                    6,
                    f"- {item.name} ({item.sku}): "
                    f"{item.stock} left (reorder <= {item.reorder_level})",
                )
                cursor_y += 6.5

    # Footer
    pdf.set_xy(14, 278)
    pdf.set_font("Helvetica", style="I", size=8)
    pdf.set_text_color(*MUTED_RGB)
    pdf.cell(
        page_width,
        5,
        "Generated automatically by ecommerce_digital_twin "
        "(Python, matplotlib, fpdf2).",
        align="C",
    )

    pdf.output(str(pdf_path))
    return pdf_path
