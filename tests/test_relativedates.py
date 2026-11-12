import datetime
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from shared.cardstore import CardStore
from shared.relativedates import (
    RAW_DATES_ENV,
    format_absolute,
    normalize_relative_dates,
)


TODAY = datetime.date(2026, 11, 12)


class NormalizeTests(unittest.TestCase):
    def test_today_and_tomorrow_become_dates(self):
        self.assertEqual(normalize_relative_dates("今天 18:00 吃饭", TODAY), "11月12日 18:00 吃饭")
        self.assertEqual(
            normalize_relative_dates("明天晚上参加开源大会", TODAY),
            "11月13日晚上参加开源大会",
        )
        self.assertEqual(
            normalize_relative_dates("记得订后天早上回杭州的机票", TODAY),
            "记得订11月14日早上回杭州的机票",
        )

    def test_longer_words_win(self):
        self.assertEqual(normalize_relative_dates("大后天交周报", TODAY), "11月15日交周报")
        self.assertEqual(normalize_relative_dates("大前天说的", TODAY), "11月9日说的")
        self.assertEqual(normalize_relative_dates("昨天的事", TODAY), "11月11日的事")

    def test_all_occurrences_are_replaced(self):
        self.assertEqual(
            normalize_relative_dates("今天起草，明天评审，后天上线", TODAY),
            "11月12日起草，11月13日评审，11月14日上线",
        )

    def test_year_changes_are_spelled_out(self):
        self.assertEqual(
            normalize_relative_dates("明天截止", datetime.date(2026, 12, 31)),
            "2027年1月1日截止",
        )
        self.assertEqual(format_absolute(datetime.date(2026, 11, 12), TODAY), "11月12日")

    def test_text_without_relative_words_is_unchanged(self):
        self.assertEqual(normalize_relative_dates("买牛奶 2026-11-12", TODAY), "买牛奶 2026-11-12")


class AddTaskNormalizeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temporary.name)
        self.store = CardStore(self.data_dir)

    def tearDown(self):
        self.temporary.cleanup()
        os.environ.pop(RAW_DATES_ENV, None)

    def added_text(self):
        return self.store.get_tasks(self.store.read_lines())[-1][2]

    def test_add_stores_absolute_date(self):
        expected_day = (datetime.date.today() + datetime.timedelta(days=1)).day
        self.store.add_tasks(["明天晚上参加开源大会"])
        self.assertIn("晚上参加开源大会", self.added_text())
        self.assertNotIn("明天", self.added_text())
        self.assertTrue(self.added_text().startswith(f"{datetime.date.today().month}月{expected_day}日"))

    def test_env_variable_keeps_original_wording(self):
        with patch.dict(os.environ, {RAW_DATES_ENV: "1"}):
            self.store.add_tasks(["明天晚上参加开源大会"])
        self.assertIn("明天晚上参加开源大会", self.added_text())


if __name__ == "__main__":
    unittest.main()
