"""Smallest example: JSON in tags + stop sequence, then validate."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extract import extract_with_tags
from schemas import Ticket

EMAIL = "Hi, this is Ana Ruiz. I was charged twice for May and need it fixed today, please."


def main() -> None:
    """Extract one ticket via tags + stop sequence and print the validated object."""
    ticket = extract_with_tags(EMAIL, Ticket)
    print(ticket)
    print(type(ticket).__name__, "->", ticket.model_dump())


if __name__ == "__main__":
    main()
