"""create queries table

Revision ID: 3e7e2f78bb8f
Revises: 8412e1fed6d
Create Date: 2014-06-20 06:58:25.508129

"""

# revision identifiers, used by Alembic.
revision = '3e7e2f78bb8f'
down_revision = '8412e1fed6d'

from alembic import op
from sqlalchemy import *


def upgrade():
    op.create_table(
        'queries',
        Column('string', String),
        Column('timestamp',
               Integer,
               primary_key=True,
               server_default=text("date_part('epoch'::text, now())"))
    )


def downgrade():
    op.drop_table('queries')
