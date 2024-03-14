"""create trigger on create message

Revision ID: 69f70f6f4bb4
Revises: b9ef5bba2b03
Create Date: 2024-03-03 15:53:51.680123

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "69f70f6f4bb4"
down_revision: Union[str, None] = "b9ef5bba2b03"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(sa.DDL(
        """
        CREATE OR REPLACE FUNCTION function_set_created_at() 
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.created_at IS NULL THEN
                    NEW.created_at = NOW();
                END IF;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;    
        """
    ))

    op.execute(sa.DDL(
        """
        CREATE TRIGGER trigger_set_created_at
            BEFORE INSERT or UPDATE ON messages
            FOR EACH ROW 
            EXECUTE PROCEDURE function_set_created_at();
        """
    ))
    # op.add_column('messages', sa.Column('created_at', sa.DateTime, nullable=True, server_default=sa.func.now()))
    # This part will update the existing rows to set the created_at column
    op.execute("UPDATE messages SET created_at = NOW() WHERE created_at IS NULL")


def downgrade() -> None:
    op.drop_column('messages', 'created_at')
    op.execute(sa.DDL("DROP TRIGGER trigger_set_created_at ON messages;"))
    op.execute(sa.DDL("DROP FUNCTION function_set_created_at()"))
