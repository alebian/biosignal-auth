from orator.seeds import Seeder


class DatabaseSeeder(Seeder):

    def run(self):
        """
        Run the database seeds.
        """
        self.db.table('clients').insert({
            'name': 'test',
            'access_token': '6xvsTWmeLQ4wYeIyWizk5XfSIUCKlxbFESqgfLiU81c5r2rbarvoZohnoN3T3A4dqMCOo88JggRn52yMmZVq2g=='
        })
        self.db.table('devices').insert({
            'external_id': 'rpi-1',
            'client_id': 1
        })
        self.db.table('devices').insert({
            'external_id': 'mac-1',
            'client_id': 1
        })
        self.db.table('devices').insert({
            'external_id': 'mac-2',
            'client_id': 1
        })
