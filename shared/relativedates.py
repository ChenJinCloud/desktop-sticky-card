"""Turn Chinese relative date words into absolute dates when tasks are added.

A task written as "今天 18:00 吃饭" means something different the next morning.
Rewriting it to "11月11日 18:00 吃饭" at insert time keeps the intent readable
weeks later, without asking the user to type dates by hand.
"""

from __future__ import annotations

import datetime
import os
import re


# Longer words must win: 大后天 before 后天, 大前天 before 前天.
RELATIVE_DAYS = {
    "大前天": -3,
    "前天": -2,
    "昨天": -1,
    "今天": 0,
    "明天": 1,
    "后天": 2,
    "大后天": 3,
}

_PATTERN = re.compile(
    "|".join(re.escape(word) for word in sorted(RELATIVE_DAYS, key=len, reverse=True))
)

RAW_DATES_ENV = "DESKTOP_STICKY_CARD_RAW_DATES"


def raw_dates_enabled() -> bool:
    """Let users keep the original wording via an environment variable."""
    value = os.environ.get(RAW_DATES_ENV, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def format_absolute(date: datetime.date, today: datetime.date | None = None) -> str:
    """Render a date as M月D日, adding the year when it leaves the current year."""
    if today is not None and date.year != today.year:
        return f"{date.year}年{date.month}月{date.day}日"
    return f"{date.month}月{date.day}日"


def normalize_relative_dates(text: str, today: datetime.date | None = None) -> str:
    """Replace every relative date word in ``text`` with its absolute date.

    Time-of-day words such as 早上/晚上 are kept as written, so
    "明天晚上开会" becomes "11月12日晚上开会".
    """
    today = today or datetime.date.today()

    def replace(match: re.Match[str]) -> str:
        days = RELATIVE_DAYS[match.group(0)]
        return format_absolute(today + datetime.timedelta(days=days), today)

    return _PATTERN.sub(replace, text)
