import unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import requests
from core import aggregate, monthly, map_window, parse_data


class DataChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.df = parse_data((Path(__file__).parent / "data/poultry_detections.csv").read_bytes())

    def test_snapshot_reconciles(self):
        self.assertEqual(len(self.df), 2300)
        self.assertEqual(self.df["Birds Impacted"].sum(), 211675446)
        self.assertEqual(str(self.df.Date.min().date()), "2022-02-08")
        self.assertEqual(str(self.df.Date.max().date()), "2026-11-04")
        self.assertEqual(self.df.duplicated().sum(), 10)
        months = pd.date_range("2022-02-01", "2026-11-01", freq="MS")
        timeline = monthly(self.df, months)
        self.assertEqual(timeline.Detections.sum(), len(self.df))
        self.assertEqual(timeline.Birds.sum(), self.df["Birds Impacted"].sum())
        self.assertEqual(aggregate(self.df, "State").Detections.sum(), len(self.df))
        self.assertEqual(timeline.loc[timeline.Detections.idxmax(), "Month"], pd.Timestamp("2022-04-01"))

    def test_monthly_cumulative_and_partial_range(self):
        selected = self.df.loc[self.df.Date.between("2022-03-15", "2022-04-20")]
        march = map_window(selected, pd.Timestamp("2022-03-01"), False)
        april = map_window(selected, pd.Timestamp("2022-04-01"), False)
        cumulative = map_window(selected, pd.Timestamp("2022-04-01"), True)
        self.assertEqual(len(march) + len(april), len(cumulative))
        self.assertEqual(len(cumulative), len(selected))
        self.assertTrue((cumulative.Date >= "2022-03-15").all())

    def test_missing_birds_not_filled_and_empty_months_are_zero(self):
        sample = b'Date,State,County,Operation Type,Birds Impacted\n01/01/2022,Iowa,A,WOAH Poultry,\n01/02/2022,Iowa,A,WOAH Poultry,\n'
        df = parse_data(sample)
        series = monthly(df, pd.date_range("2022-01-01", "2022-02-01", freq="MS"))
        self.assertTrue(pd.isna(series.iloc[0].Birds))
        self.assertEqual(series.iloc[0].Missing_birds, 2)
        self.assertEqual(series.iloc[1].Birds, 0)
        self.assertEqual(series.iloc[1].Detections, 0)
        self.assertTrue(df.Category.str.startswith("Other source").all())

    def test_verified_offline_fallback(self):
        from data_source import load_data
        load_data.clear()
        with patch("data_source.requests.get", side_effect=requests.ConnectionError("offline")), patch("data_source.datetime") as clock:
            from datetime import datetime, timezone
            clock.now.return_value = datetime(2030, 1, 1, tzinfo=timezone.utc)
            clock.fromisoformat = datetime.fromisoformat
            df, meta, status, error = load_data()
        self.assertEqual(status, "Offline snapshot")
        self.assertIn("offline", error)
        self.assertFalse(df.empty)
        self.assertEqual(len(meta["sha256"]), 64)
        load_data.clear()


class InterfaceChecks(unittest.TestCase):
    def test_widgets_and_empty_filter(self):
        from streamlit.testing.v1 import AppTest
        at = AppTest.from_file(str(Path(__file__).parent / "app.py"), default_timeout=45).run()
        self.assertEqual(len(at.exception), 0)
        at.radio[0].set_value("Cumulative").run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.metric[-1].value, "2,300")
        at.radio[1].set_value("Birds in affected flocks").run()
        at.multiselect[0].set_value(["Puerto Rico"]).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(at.metric[0].value, "3")
        at.multiselect[2].set_value(["Commercial Turkey Poult Supplier"]).run()
        self.assertEqual(at.metric[0].value, "0")
        self.assertEqual(len(at.exception), 0)
        at.multiselect[0].set_value([]).run()
        at.date_input[0].set_value((pd.Timestamp("2022-02-08").date(), pd.Timestamp("2022-02-20").date())).run()
        self.assertEqual(len(at.exception), 0)
        self.assertEqual(len(at.select_slider), 0)  # Single-month range works without a slider.


if __name__ == "__main__":
    unittest.main()
