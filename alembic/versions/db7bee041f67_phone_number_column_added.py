"""phone number column added

Revision ID: db7bee041f67
Revises: 
Create Date: 2025-03-11 13:01:27.136403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'db7bee041f67'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

#ekleme vs. yaptığımızda buraya yazıyoruz
def upgrade() -> None:                                                                #Boş bırıkılırsa sıkıntı olmaz demek
    op.add_column('users', sa.Column('phone_number', sa.String(), nullable=True))



#silme vs. yaptığımızda buraya yazıyoruz
def downgrade() -> None:
    pass
