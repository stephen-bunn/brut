"""
This module contains a Caribou migration.

Migration Name: create_artifact_table
Migration Version: 20230127171944
"""


def upgrade(connection):
    # add your upgrade step here
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS artifact(
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            fingerprint TEXT NOT NULL UNIQUE,
            url TEXT NOT NULL,
            fetched_at TEXT,
            fetched_message TEXT,
            processed_at TEXT,
            processed_message TEXT
        )
        """
    )


def downgrade(connection):
    # add your downgrade step here
    connection.execute(
        """
        DROP TABLE IF EXISTS artifact
        """
    )
