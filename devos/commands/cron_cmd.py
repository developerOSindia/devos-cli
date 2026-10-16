"""
DeveloperOS CLI - Cron Parser & Next-Run Calculator
Zero-dependency 5-field cron expression parser, schedule explainer, and next-run calculator.
"""

import argparse
import calendar
import datetime
import json
import re
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

MONTH_NAMES = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

DAY_NAMES = {
    "SUN": 0, "MON": 1, "TUE": 2, "WED": 3, "THU": 4, "FRI": 5, "SAT": 6,
}

ALIASES = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


def parse_field(field_str: str, min_val: int, max_val: int, names: Optional[Dict[str, int]] = None) -> Set[int]:
    """
    Parses a single cron field into a set of permitted integer values.
    Supports *, ranges (1-5), steps (*/15 or 1-10/2), lists (1,2,5), and names.
    """
    field_str = field_str.strip().upper()
    if names:
        for name, num in names.items():
            field_str = re.sub(rf"\b{name}\b", str(num), field_str)

    values: Set[int] = set()
    parts = field_str.split(",")

    for part in parts:
        part = part.strip()
        if not part:
            continue

        step = 1
        if "/" in part:
            range_part, step_str = part.split("/", 1)
            try:
                step = int(step_str)
                if step <= 0:
                    raise ValueError(f"Step must be positive in '{part}'")
            except ValueError:
                raise ValueError(f"Invalid step value in '{part}'")
        else:
            range_part = part

        if range_part == "*":
            start, end = min_val, max_val
        elif "-" in range_part:
            start_str, end_str = range_part.split("-", 1)
            try:
                start = int(start_str)
                end = int(end_str)
            except ValueError:
                raise ValueError(f"Invalid range bounds in '{part}'")
            if start > end or start < min_val or end > max_val:
                raise ValueError(f"Range {start}-{end} out of bounds [{min_val}, {max_val}]")
        else:
            try:
                val = int(range_part)
            except ValueError:
                raise ValueError(f"Invalid cron token: '{part}'")
            if val < min_val or val > max_val:
                raise ValueError(f"Value {val} out of bounds [{min_val}, {max_val}]")
            start = val
            end = max_val if "/" in part else val

        for val in range(start, end + 1, step):
            if min_val <= val <= max_val:
                values.add(val)

    if not values:
        raise ValueError(f"No valid values resolved for field: '{field_str}'")

    return values


class CronSchedule:
    """Represents a validated 5-field cron schedule."""

    def __init__(self, expression: str):
        self.raw_expression = expression.strip()
        norm_expr = ALIASES.get(self.raw_expression.lower(), self.raw_expression)
        fields = norm_expr.split()
        if len(fields) != 5:
            raise ValueError(f"Expected 5 cron fields, received {len(fields)}: '{expression}'")

        self.min_field, self.hour_field, self.dom_field, self.month_field, self.dow_field = fields

        self.minutes = parse_field(self.min_field, 0, 59)
        self.hours = parse_field(self.hour_field, 0, 23)
        self.doms = parse_field(self.dom_field, 1, 31)
        self.months = parse_field(self.month_field, 1, 12, MONTH_NAMES)

        # Day of week: 0-7, 7 maps to 0 (Sunday)
        raw_dows = parse_field(self.dow_field, 0, 7, DAY_NAMES)
        self.dows = {0 if d == 7 else d for d in raw_dows}

        self.dom_any = self.dom_field == "*"
        self.dow_any = self.dow_field == "*"

    def matches_date(self, year: int, month: int, day: int) -> bool:
        """Checks if a calendar day matches the month, DOM, and DOW criteria."""
        if month not in self.months:
            return False

        max_day = calendar.monthrange(year, month)[1]
        if day > max_day:
            return False

        dt = datetime.date(year, month, day)
        # Python: 0=Mon..6=Sun. Cron: 0=Sun, 1=Mon..6=Sat
        cron_dow = (dt.weekday() + 1) % 7

        dom_match = day in self.doms
        dow_match = cron_dow in self.dows

        if self.dom_any and self.dow_any:
            return True
        elif not self.dom_any and self.dow_any:
            return dom_match
        elif self.dom_any and not self.dow_any:
            return dow_match
        else:
            # Vixie cron standard: if both are restricted, match if either matches
            return dom_match or dow_match

    def next_run(self, from_dt: datetime.datetime) -> datetime.datetime:
        """Finds the next upcoming execution datetime after from_dt."""
        # Truncate seconds and microseconds, step 1 minute forward
        current = from_dt.replace(second=0, microsecond=0) + datetime.timedelta(minutes=1)

        # Safety bound: 5 years limit
        limit_year = current.year + 5

        while current.year <= limit_year:
            # 1. Month check
            if current.month not in self.months:
                # Advance to first day of next month
                if current.month == 12:
                    current = datetime.datetime(current.year + 1, 1, 1, 0, 0, tzinfo=current.tzinfo)
                else:
                    current = datetime.datetime(current.year, current.month + 1, 1, 0, 0, tzinfo=current.tzinfo)
                continue

            # 2. Day check
            if not self.matches_date(current.year, current.month, current.day):
                # Advance to start of next calendar day
                current = (current + datetime.timedelta(days=1)).replace(hour=0, minute=0)
                continue

            # 3. Hour check
            if current.hour not in self.hours:
                # Advance to next hour, minute 0
                current = (current + datetime.timedelta(hours=1)).replace(minute=0)
                continue

            # 4. Minute check
            if current.minute not in self.minutes:
                current += datetime.timedelta(minutes=1)
                continue

            return current

        raise ValueError("No matching execution found within the next 5 years")

    def next_runs(self, count: int = 5, from_dt: Optional[datetime.datetime] = None) -> List[datetime.datetime]:
        """Calculates a sequence of future execution times."""
        if count < 1:
            raise ValueError("Run count must be at least 1")

        curr = from_dt or datetime.datetime.now()
        runs: List[datetime.datetime] = []
        for _ in range(count):
            nxt = self.next_run(curr)
            runs.append(nxt)
            curr = nxt
        return runs


def explain_cron(expression: str) -> str:
    """Provides a human-readable summary of a cron expression."""
    expr = expression.strip()
    lower = expr.lower()
    if lower in ALIASES:
        aliases_desc = {
            "@yearly": "Once a year on January 1 at 00:00",
            "@annually": "Once a year on January 1 at 00:00",
            "@monthly": "Once a month on the 1st at 00:00",
            "@weekly": "Once a week on Sunday at 00:00",
            "@daily": "Every day at 00:00 (midnight)",
            "@midnight": "Every day at 00:00 (midnight)",
            "@hourly": "Every hour at minute 0",
        }
        return aliases_desc[lower]

    fields = expr.split()
    if len(fields) != 5:
        return f"Custom 5-field expression: {expr}"

    m, h, dom, mon, dow = fields

    dow_names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # Common pattern checks
    if expr == "* * * * *":
        return "Every minute"
    if m.startswith("*/") and h == "*" and dom == "*" and mon == "*" and dow == "*":
        return f"Every {m[2:]} minutes"
    if m == "0" and h == "*" and dom == "*" and mon == "*" and dow == "*":
        return "Every hour at minute 0"
    if m.isdigit() and h == "*" and dom == "*" and mon == "*" and dow == "*":
        return f"Every hour at minute {m}"
    if m.isdigit() and h.isdigit() and dom == "*" and mon == "*" and dow == "*":
        return f"Every day at {int(h):02d}:{int(m):02d}"
    if m.isdigit() and h.isdigit() and dom == "*" and mon == "*" and dow == "1-5":
        return f"Every weekday (Monday through Friday) at {int(h):02d}:{int(m):02d}"

    # General descriptive format
    parts = []
    if m == "*":
        parts.append("every minute")
    elif m.startswith("*/"):
        parts.append(f"every {m[2:]} minutes")
    else:
        parts.append(f"at minute {m}")

    if h == "*":
        parts.append("past every hour")
    elif h.startswith("*/"):
        parts.append(f"every {h[2:]} hours")
    else:
        parts.append(f"past hour {h}")

    if dom != "*":
        parts.append(f"on day-of-month {dom}")

    if mon != "*":
        parts.append(f"in month {mon}")

    if dow != "*":
        parts.append(f"on day-of-week {dow}")

    return " ".join(parts).capitalize()


def register_subparser(subparsers: argparse._SubParsersAction) -> argparse.ArgumentParser:
    """Registers the 'cron' subcommand parser."""
    parser = subparsers.add_parser(
        "cron",
        help="Parse cron expressions and calculate next execution schedules",
        description="Zero-dependency cron parser, schedule humanizer, and multi-run timeline calculator.",
    )
    parser.add_argument(
        "expression",
        help="5-field cron expression (e.g. '*/15 * * * *') or alias (@daily, @hourly)",
    )
    parser.add_argument(
        "-n", "--runs",
        type=int,
        default=5,
        help="Number of upcoming execution times to calculate (default: 5)",
    )
    parser.add_argument(
        "--from",
        dest="from_time",
        default=None,
        help="Starting timestamp for calculation (ISO format: YYYY-MM-DDTHH:MM:SS)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output parsed schedule and next runs as JSON",
    )
    return parser


def execute(args: argparse.Namespace) -> int:
    """Executes the cron subcommand."""
    try:
        schedule = CronSchedule(args.expression)
    except Exception as err:
        sys.stderr.write(f"[ERROR] Invalid cron expression: {err}\n")
        return 1

    from_dt = None
    if args.from_time:
        try:
            from_dt = datetime.datetime.fromisoformat(args.from_time)
        except ValueError:
            sys.stderr.write(f"[ERROR] Invalid --from datetime format. Use ISO format (e.g. 2026-10-16T12:00:00)\n")
            return 1

    try:
        next_times = schedule.next_runs(count=args.runs, from_dt=from_dt)
        explanation = explain_cron(args.expression)
    except Exception as err:
        sys.stderr.write(f"[ERROR] Calculation failed: {err}\n")
        return 1

    if args.json:
        data = {
            "expression": args.expression,
            "explanation": explanation,
            "next_runs": [dt.strftime("%Y-%m-%d %H:%M:%S") for dt in next_times],
        }
        sys.stdout.write(json.dumps(data, indent=2) + "\n")
        return 0

    sys.stdout.write("============================================================\n")
    sys.stdout.write(f" DeveloperOS Cron Schedule: {args.expression}\n")
    sys.stdout.write(f" Meaning: {explanation}\n")
    sys.stdout.write("============================================================\n")
    sys.stdout.write(f"Upcoming {len(next_times)} execution times:\n")
    for i, run in enumerate(next_times, start=1):
        day_str = run.strftime("%A")
        date_str = run.strftime("%Y-%m-%d %H:%M:%S")
        sys.stdout.write(f"  {i}. {date_str} ({day_str})\n")

    return 0
