"""Add indexes to price_history table

This migration adds indexes to the price_history table to improve query performance.
The following indexes are added:
- idx_price_history_ticker: Index on ticker column
- idx_price_history_date: Index on date column
- idx_price_history_last_updated: Index on last_updated column

These indexes will improve the performance of queries that filter by ticker, date, or last_updated,
which are common in the dashboard loading process.
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic
revision = 'add_price_history_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add indexes to price_history table
    op.create_index('idx_price_history_ticker', 'price_history', ['ticker'])
    op.create_index('idx_price_history_date', 'price_history', ['date'])
    op.create_index('idx_price_history_last_updated', 'price_history', ['last_updated'])


def downgrade():
    # Remove indexes from price_history table
    op.drop_index('idx_price_history_ticker', table_name='price_history')
    op.drop_index('idx_price_history_date', table_name='price_history')
    op.drop_index('idx_price_history_last_updated', table_name='price_history')
