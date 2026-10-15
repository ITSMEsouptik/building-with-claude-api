"""Same extraction, via output_config.format (JSON schema)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extract import extract_with_schema
from schemas import Ticket

EMAIL = "Hi, this is Ana Ruiz. I was charged twice for May and need it fixed today, please."


def main() -> None:
    """Extract one ticket via a JSON schema and print the validated object."""
    print(extract_with_schema(EMAIL, Ticket))


if __name__ == "__main__":
    main()
