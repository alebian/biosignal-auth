from orator.migrations import Migration


class CreateClientsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('clients') as table:
            table.increments('id')
            table.string('name', 128)
            table.string('access_token', 128)
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('clients')
