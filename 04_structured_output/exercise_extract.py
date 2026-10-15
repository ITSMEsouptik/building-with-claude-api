"""Run extraction over a small set of emails and report the success rate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extract import ExtractionError, extract_with_schema, extract_with_tags, with_retry
from schemas import Ticket

EMAILS = [
    "Hi, this is Ana Ruiz. I was charged twice for May and need it fixed today, please.",
    "Dev here (Sam Lee). The export button crashes the app every time. Not blocking, but annoying.",
    "Would love dark mode someday. - Priya N.",
    "URGENT: our whole team (Acme Corp, contact Joe Park) cannot log in since 9am!!",
]


def main(extractor=extract_with_tags) -> None:
    """Extract every email, print each result or failure, and print the success rate."""
    ok = 0
    for email in EMAILS:
        try:
            print(with_retry(extractor, email, Ticket))
            ok += 1
        except ExtractionError as e:
            print("FAILED:", e)
    print(f"\n{ok}/{len(EMAILS)} extracted ({extractor.__name__})")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "tags"
    main(extract_with_schema if mode == "schema" else extract_with_tags)
