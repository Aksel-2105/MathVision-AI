"""Store source image feature snapshots for recommendation training."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0003_source_features"
down_revision: Union[str, Sequence[str], None] = "0002_experiments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("experiments", sa.Column("source_features", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("experiments", "source_features")
