import argparse
from datetime import date, datetime
from itertools import islice
from pathlib import Path
from pprint import pprint
from typing import List, Optional

import pydantic
import yaml
from pydantic import BaseModel, Field, root_validator
from rich import print


def none_to_default(v, default):
    return v if v is not None else default


class Location(BaseModel):
    address: Optional[str]
    city: str = "MISSING"
    state: str = "MISSING"


class Minister(BaseModel):
    @root_validator(pre=True)
    def replace_none_with_default(cls, values):
        if "start" in values and values["start"] is None:
            values["start"] = datetime(1, 1, 1)
        return values

    end: Optional[date]
    name: str = "MISSING"
    start: date = datetime(1, 1, 1)
    type: str = "MISSING"


class Name(BaseModel):
    end: Optional[date]
    name: str = "MISSING"
    start: Optional[date]


class Status(BaseModel):
    active: bool = False
    reason: Optional[str] = None
    withdrawal_to: Optional[str] = None
    end_date: Optional[date] = None
    received_from: Optional[str] = None


class ChurchRecord(BaseModel):
    @root_validator(pre=True)
    def validate(cls, values):
        if (
            "received_from" in values
            and isinstance(values["received_from"], str) is False
        ):
            values["received_from"] = "MISSING"
        return values

    location: Location
    minister: Optional[List[Minister]]
    names: Optional[List[Name]]
    origination_date: date = datetime(1, 1, 1)
    raw_data: str = "MISSING"
    received_from: Optional[str] = None
    status: Status = Field(default_factory=Status)
    name: str
    end_date: Optional[date] = None


parser = argparse.ArgumentParser(description="Extract OPC Church Registry")
parser.add_argument(
    "--file",
    type=str,
    help="CSV file to extract",
    default="opc.yaml",
)
parser.add_argument(
    "--count", type=int, help="Number of records to extract", default=10
)
args = parser.parse_args()


def slugify(s):
    return (
        s.lower()
        .replace(" ", "-")
        .replace("'", "")
        .replace("’", "")
        .replace("(", "")
        .replace("/", "-")
    )


p = Path("site/content/churches")
errors_path = Path("errors")
errors = 0
success = 0
with open(args.file, newline="") as f:
    opc = yaml.safe_load(f)
    print(f"Extracting {args.count} records from {args.file}")
    for rec in islice(opc, args.count):
        print(".", end="", flush=True)
        try:
            status = {}
            rec["status"] = rec.get("status", {})
            for s in rec["status"]:
                status.update(s)
            rec["status"] = status
        except Exception as e:
            errors = errors + 1
            file = errors_path / (slugify(f"ERROR - {row[0]} {row[1]}") + ".md")
            file.write_text(str(e) + "\n\n" + row[3])
            continue
        try:
            parsed_red = ChurchRecord(**rec)
        except pydantic.error_wrappers.ValidationError as e:
            print(e)
            pprint(rec)
            errors = errors + 1
            raise
        file = p / (
            slugify(
                f"{parsed_red.name} {parsed_red.location.city} {parsed_red.location.state}"
            )
            + ".md"
        )
        d = parsed_red.dict()
        d["ministers"] = [m.name for m in parsed_red.minister or {}]
        d["states"] = [parsed_red.location.state]
        d["year_established"] = [d["origination_date"].year]
        if d["received_from"] == "MISSING":
            del d["received_from"]
        if d.get("received_from"):
            d["received_from"] = [d["received_from"]]
        if parsed_red.status.withdrawal_to:
            d["withdrawal_to"] = [parsed_red.status.withdrawal_to]
        d["date"] = d["origination_date"]
        d["title"] = f"{d['name']} ({d['location']['city']} {d['location']['state']})"
        file.write_text(
            f"""---
{yaml.dump(d)}
---"""
        )
        success = success + 1
print(f"\n{success} records extracted successfully")
print(f"{errors} records failed to extract")
