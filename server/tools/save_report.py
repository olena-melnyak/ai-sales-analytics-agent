from pathlib import Path

from server.tools.audit import log_tool_call

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports"


def save_report(report_name: str, html: str) -> str:
    """Save an HTML analytics report to the reports directory."""

    try:
        report_name = report_name.strip()

        if not report_name:
            raise ValueError("Report name cannot be empty.")

        if not html.strip():
            raise ValueError("Report HTML cannot be empty.")

        if Path(report_name).name != report_name:
            raise ValueError("Report name must not contain directory paths.")

        if not report_name.lower().endswith(".html"):
            report_name += ".html"

        REPORTS_DIR.mkdir(parents=True, exist_ok=True)

        report_path = REPORTS_DIR / report_name
        report_path.write_text(html, encoding="utf-8")

        result = str(report_path.relative_to(PROJECT_ROOT))

        log_tool_call(
            tool_name="create_report",
            status="success",
        )

        return result

    except Exception as exc:
        log_tool_call(
            tool_name="create_report",
            status="error",
            error_message=str(exc),
        )
        raise
