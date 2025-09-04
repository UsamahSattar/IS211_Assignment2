
import argparse
import csv
import logging
from datetime import datetime, date
from io import StringIO
from urllib.request import urlopen
import sys


def downloadData(url):
    """Download the CSV at URL and return its text (UTF-8)."""
    with urlopen(url) as resp:
        data = resp.read()
    return data.decode("utf-8", errors="replace")


def processData(file_content):
    """
    Parse CSV text and return {id: (name, birthday_date)}.

    Expected columns: id, name, birthday (dd/mm/YYYY).
    If a birthday is malformed, log:
      "Error processing line #<lineno> for ID #<id>"
    and skip that row.
    """
    logger = logging.getLogger("assignment2")
    people = {}

    reader = csv.reader(StringIO(file_content))
    for lineno, row in enumerate(reader, start=1):
        if not row:
            continue
        try:
            raw_id, name, bday_str = row[0].strip(), row[1].strip(), row[2].strip()
        except IndexError:
            
            continue

        
        if not raw_id.isdigit():
            continue

        pid = int(raw_id)
        try:
            bday = datetime.strptime(bday_str, "%d/%m/%Y").date()
        except Exception:
            logger.error(f"Error processing line #{lineno} for ID #{pid}")
            continue

        people[pid] = (name, bday)

    return people


def displayPerson(id, personData):
    """
    Print person info in required format, or 'not found' message.
    Format: "Person #<id> is <name> with a birthday of <YYYY-MM-DD>"
    """
    info = personData.get(id)
    if not info:
        print("No user found with that id")
        return
    name, bday = info
    print(f"Person #{id} is {name} with a birthday of {bday.isoformat()}")


def _configure_logger():
    """Set up a logger named 'assignment2' that writes ERRORs to error.log."""
    logger = logging.getLogger("assignment2")
    logger.setLevel(logging.ERROR)
    handler = logging.FileHandler("error.log", mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.handlers.clear()
    logger.addHandler(handler)


def main(url):
    _configure_logger()

    
    try:
        csv_text = downloadData(url)
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

    
    personData = processData(csv_text)

    
    while True:
        raw = input("Enter an ID to lookup (<= 0 to exit): ").strip()
        if not raw:
            continue
        try:
            pid = int(raw)
        except ValueError:
            print("Please enter a valid integer ID.")
            continue

        if pid <= 0:
            break

        displayPerson(pid, personData)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Week 2 assignment runner (Python 3)")
    parser.add_argument("--url", required=True, type=str, help="URL to the CSV file")
    args = parser.parse_args()
    main(args.url)
