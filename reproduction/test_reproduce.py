"""Checks for the original R table-slice translation and reported contrasts."""
import unittest
import reproduce


class Figure2DataChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.curves = reproduce.load_curves()
        cls.by_key = {(c['panel'], c['strain'], c['donor_vaccinated']): c for c in cls.curves}

    def test_selected_record_counts(self):
        # Counts from the original R's explicit nrows, independently enumerated.
        counts = {'A': {'595': (10, 7), 'Md5': (8, 7), '675A': (20, 9)},
                  'B': {'595': (10, 7), 'Md5': (8, 7), '675A': (9, 6)},
                  'C': {'595': (10, 7), 'Md5': (8, 7), '675A': (5, 7)}}
        self.assertEqual(len(self.curves), 18)
        for panel, strains in counts.items():
            for strain, ns in strains.items():
                for vaccinated, n in zip([False, True], ns):
                    self.assertEqual(self.by_key[panel, strain, vaccinated]['n'], n)

    def test_nine_day_595_detection_contrast(self):
        summary = reproduce.make_summary(self.curves)
        self.assertEqual(summary['vaccinated_donors'], 25)
        self.assertEqual(summary['unvaccinated_donors'], 34)
        self.assertEqual(summary['difference_days'], 9)

    def test_unresolved_595_survival_endpoint_is_preserved(self):
        c = self.by_key['C', '595', True]
        self.assertEqual(c['day'][-1], 53)
        self.assertEqual(sum(r['state'][-1] for r in c['records']), 1)
        self.assertAlmostEqual(c['percent'][-1], 100/7)
        self.assertEqual(self.by_key['C', '595', False]['percent'][-1], 0)

    def test_lethal_strain_transmission_contrast(self):
        for strain in ['Md5', '675A']:
            self.assertTrue(all(v == 0 for v in self.by_key['B', strain, False]['percent']))
            self.assertEqual(self.by_key['B', strain, True]['percent'][-1], 100)
            self.assertEqual(self.by_key['A', strain, False]['percent'][-1], 0)

    def test_display_offsets_do_not_change_biological_values(self):
        for key, expected in [(('A', 'Md5', True), 2), (('B', 'Md5', False), -2), (('C', 'Md5', False), 2)]:
            c = self.by_key[key]
            self.assertEqual(c['display_offset'], expected)
            self.assertAlmostEqual(c['drawn_percent'][0]-c['percent'][0], expected)
        for c in self.curves:
            self.assertTrue(all(0 <= v <= 100 for v in c['percent']))


if __name__ == '__main__':
    unittest.main()
