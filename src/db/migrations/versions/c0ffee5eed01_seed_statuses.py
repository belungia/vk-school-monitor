"""Seed status lookup tables so status_id FKs resolve on a fresh DB

Revision ID: c0ffee5eed01
Revises: 8e45ddf21547
Create Date: 2026-06-16

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c0ffee5eed01'
down_revision: Union[str, Sequence[str], None] = '8e45ddf21547'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# (table, [(id, status), ...]) — 0 = off/new, 1 = on/analyzed. Idempotent.
SEED = {
    "user_statuses": [(0, "not_monitored"), (1, "monitored")],
    "group_statuses": [(0, "not_monitored"), (1, "monitored")],
    "post_statuses": [(0, "new"), (1, "analyzed")],
}


def upgrade() -> None:
    for table, rows in SEED.items():
        values = ", ".join(f"({i}, '{s}')" for i, s in rows)
        op.execute(
            f"INSERT INTO {table} (id, status) VALUES {values} "
            f"ON CONFLICT (id) DO NOTHING"
        )


def downgrade() -> None:
    for table, rows in SEED.items():
        ids = ", ".join(str(i) for i, _ in rows)
        op.execute(f"DELETE FROM {table} WHERE id IN ({ids})")
