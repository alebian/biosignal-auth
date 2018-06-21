from orator.migrations import Migration


class CreateDevicesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('devices') as table:
            table.increments('id')
            table.string('external_id', 32)
            table.string('ip_address', 16).nullable()
            table.integer('client_id').unsigned()
            table.foreign('client_id').references('id').on('clients').on_delete('cascade')
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('devices')
