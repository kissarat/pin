"""Changed users table

Revision ID: 4c683c8911ce
Revises: None
Create Date: 2014-06-03 16:46:26.095242

"""

# revision identifiers, used by Alembic.
revision = '4c683c8911ce'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('users', 'pic')
    op.drop_column('users', 'bg')
    op.add_column('users', sa.Column('pic_id', sa.Integer))
    op.add_column('users', sa.Column('bg_id', sa.Integer))

    op.create_foreign_key(
        "fk_pic", "users",
        "pictures", ["pic_id"], ["id"])
    op.create_foreign_key(
        "fk_bg", "users",
        "pictures", ["bg_id"], ["id"])

def downgrade():
    op.drop_column('users', 'pic_id')
    op.drop_column('users', 'bg_id')
    op.add_column('users', sa.Column('pic', sa.Integer))
    op.add_column('users', sa.Column('bg', sa.Boolean, server_default="False"))