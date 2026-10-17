import unittest
from database import init_db
from models import add_darbas, load_table_df, delete_darbas

class TestUkvedysApp(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_task_creation(self):
        task_data = {
            'title': 'Testavimo užduotis',
            'description': 'Test',
            'location': 'Testo patalpa',
            'source': 'Vadovo pavedimas',
            'priority': 'P3 - Įprasta',
            'status': 'Nauja',
            'due_date': '2026-12-31'
        }
        task_id = add_darbas(task_data)
        self.assertTrue(task_id.startswith('D-'))
        df = load_table_df('darbai')
        self.assertIn(task_id, df['id'].values)
        delete_darbas(task_id)

if __name__ == '__main__':
    unittest.main()
