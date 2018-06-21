from orator.migrations import Migration


class CreateSignalsTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('signals') as table:
            table.increments('id')
            table.string('external_uuid', 128).unique()
            table.json('signal')
            table.integer('device_id').unsigned()
            table.foreign('device_id').references('id').on('devices').on_delete('cascade')
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('signals')
