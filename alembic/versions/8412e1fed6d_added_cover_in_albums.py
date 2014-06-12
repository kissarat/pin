"""added cover in albums

Revision ID: 8412e1fed6d
Revises: 4c683c8911ce
Create Date: 2014-06-12 14:05:26.065078

"""

# revision identifiers, used by Alembic.
revision = '8412e1fed6d'
down_revision = '4c683c8911ce'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('albums', sa.Column('cover_id', sa.Integer))
    op.create_foreign_key(
        "fk_cover", "albums",
        "pictures", ["cover_id"], ["id"])


def downgrade():
    pass
