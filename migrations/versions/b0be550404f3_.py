"""empty message

Revision ID: b0be550404f3
Revises: 80820dd70bae
Create Date: 2020-02-03 20:16:54.214703

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0be550404f3'
down_revision = '80820dd70bae'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'Venue', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'Venue', type_='unique')
    # ### end Alembic commands ###
