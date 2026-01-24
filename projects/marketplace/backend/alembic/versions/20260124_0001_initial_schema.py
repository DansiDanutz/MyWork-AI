"""Initial schema - create all tables

Revision ID: 0001
Revises:
Create Date: 2026-01-24

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(50), nullable=False, unique=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, default='user'),
        sa.Column('subscription_tier', sa.String(20), nullable=False, default='free'),
        sa.Column('is_seller', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
    )
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])

    # Seller profiles table
    op.create_table(
        'seller_profiles',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('website', sa.String(255), nullable=True),
        sa.Column('github_username', sa.String(100), nullable=True),
        sa.Column('twitter_handle', sa.String(100), nullable=True),
        sa.Column('stripe_account_id', sa.String(255), nullable=True),
        sa.Column('payouts_enabled', sa.Boolean(), nullable=False, default=False),
        sa.Column('total_sales', sa.Integer(), nullable=False, default=0),
        sa.Column('total_revenue', sa.Float(), nullable=False, default=0.0),
        sa.Column('average_rating', sa.Float(), nullable=False, default=0.0),
        sa.Column('verification_level', sa.String(20), nullable=False, default='unverified'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
    )
    op.create_index('ix_seller_profiles_user_id', 'seller_profiles', ['user_id'])

    # Products table
    op.create_table(
        'products',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('seller_id', sa.String(255), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('slug', sa.String(220), nullable=False, unique=True),
        sa.Column('short_description', sa.String(500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('subcategory', sa.String(50), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('extended_license_price', sa.Float(), nullable=True),
        sa.Column('unlimited_license_price', sa.Float(), nullable=True),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('preview_images', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('preview_url', sa.String(500), nullable=True),
        sa.Column('demo_url', sa.String(500), nullable=True),
        sa.Column('file_url', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('tech_stack', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('requirements', sa.Text(), nullable=True),
        sa.Column('documentation_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='draft'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, default=False),
        sa.Column('average_rating', sa.Float(), nullable=False, default=0.0),
        sa.Column('review_count', sa.Integer(), nullable=False, default=0),
        sa.Column('sales_count', sa.Integer(), nullable=False, default=0),
        sa.Column('view_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
        sa.Column('published_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_products_seller_id', 'products', ['seller_id'])
    op.create_index('ix_products_slug', 'products', ['slug'])
    op.create_index('ix_products_category', 'products', ['category'])
    op.create_index('ix_products_status', 'products', ['status'])

    # Product versions table
    op.create_table(
        'product_versions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('product_id', sa.String(36), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.String(20), nullable=False),
        sa.Column('changelog', sa.Text(), nullable=True),
        sa.Column('file_url', sa.String(500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('is_current', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_product_versions_product_id', 'product_versions', ['product_id'])

    # Orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('buyer_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('seller_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('product_id', sa.String(36), sa.ForeignKey('products.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('platform_fee', sa.Float(), nullable=False),
        sa.Column('seller_amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('license_type', sa.String(20), nullable=False, default='standard'),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('payment_intent_id', sa.String(255), nullable=True),
        sa.Column('download_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_downloads', sa.Integer(), nullable=False, default=5),
        sa.Column('escrow_release_date', sa.DateTime(), nullable=True),
        sa.Column('refund_reason', sa.Text(), nullable=True),
        sa.Column('refund_requested_at', sa.DateTime(), nullable=True),
        sa.Column('refunded_at', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
    )
    op.create_index('ix_orders_buyer_id', 'orders', ['buyer_id'])
    op.create_index('ix_orders_seller_id', 'orders', ['seller_id'])
    op.create_index('ix_orders_product_id', 'orders', ['product_id'])
    op.create_index('ix_orders_status', 'orders', ['status'])

    # Reviews table
    op.create_table(
        'reviews',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('product_id', sa.String(36), sa.ForeignKey('products.id', ondelete='CASCADE'), nullable=False),
        sa.Column('buyer_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('order_id', sa.String(36), sa.ForeignKey('orders.id'), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('is_verified_purchase', sa.Boolean(), nullable=False, default=False),
        sa.Column('helpful_count', sa.Integer(), nullable=False, default=0),
        sa.Column('seller_response', sa.Text(), nullable=True),
        sa.Column('seller_response_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
    )
    op.create_index('ix_reviews_product_id', 'reviews', ['product_id'])
    op.create_index('ix_reviews_buyer_id', 'reviews', ['buyer_id'])

    # Subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(255), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('tier', sa.String(20), nullable=False, default='free'),
        sa.Column('stripe_subscription_id', sa.String(255), nullable=True),
        sa.Column('stripe_customer_id', sa.String(255), nullable=True),
        sa.Column('stripe_price_id', sa.String(255), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, default='active'),
        sa.Column('current_period_start', sa.DateTime(), nullable=True),
        sa.Column('current_period_end', sa.DateTime(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(), nullable=True),
        sa.Column('brain_queries_used', sa.Integer(), nullable=False, default=0),
        sa.Column('brain_queries_limit', sa.Integer(), nullable=False, default=10),
        sa.Column('products_listed', sa.Integer(), nullable=False, default=0),
        sa.Column('products_limit', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
    )
    op.create_index('ix_subscriptions_user_id', 'subscriptions', ['user_id'])

    # Payouts table
    op.create_table(
        'payouts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('seller_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False, default='USD'),
        sa.Column('status', sa.String(20), nullable=False, default='pending'),
        sa.Column('stripe_transfer_id', sa.String(255), nullable=True),
        sa.Column('stripe_payout_id', sa.String(255), nullable=True),
        sa.Column('order_ids', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('initiated_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('failed_at', sa.DateTime(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
    )
    op.create_index('ix_payouts_seller_id', 'payouts', ['seller_id'])

    # Brain entries table
    op.create_table(
        'brain_entries',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('contributor_id', sa.String(255), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('entry_type', sa.String(30), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('language', sa.String(30), nullable=True),
        sa.Column('framework', sa.String(50), nullable=True),
        sa.Column('embedding_id', sa.String(100), nullable=True),
        sa.Column('quality_score', sa.Float(), nullable=False, default=0.5),
        sa.Column('usage_count', sa.Integer(), nullable=False, default=0),
        sa.Column('upvotes', sa.Integer(), nullable=False, default=0),
        sa.Column('downvotes', sa.Integer(), nullable=False, default=0),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_public', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=True, onupdate=sa.func.now()),
    )
    op.create_index('ix_brain_entries_contributor_id', 'brain_entries', ['contributor_id'])
    op.create_index('ix_brain_entries_category', 'brain_entries', ['category'])
    op.create_index('ix_brain_entries_entry_type', 'brain_entries', ['entry_type'])


def downgrade() -> None:
    op.drop_table('brain_entries')
    op.drop_table('payouts')
    op.drop_table('subscriptions')
    op.drop_table('reviews')
    op.drop_table('orders')
    op.drop_table('product_versions')
    op.drop_table('products')
    op.drop_table('seller_profiles')
    op.drop_table('users')
