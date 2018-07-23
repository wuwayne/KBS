"""empty message

Revision ID: c16da1a107fb
Revises: f86fb6923973
Create Date: 2018-07-13 16:30:17.763233

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c16da1a107fb'
down_revision = 'f86fb6923973'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stars',
    sa.Column('starers_id', sa.Integer(), nullable=True),
    sa.Column('stared_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['stared_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['starers_id'], ['user.id'], )
    )
    op.create_foreign_key(None, 'comment', 'post', ['post_id'], ['id'])
    op.create_foreign_key(None, 'comment', 'user', ['user_id'], ['id'])
    op.drop_column('comment', 'pos_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('pos_id', sa.INTEGER(), nullable=True))
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_table('stars')
    # ### end Alembic commands ###