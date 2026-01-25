"""add project submissions

Revision ID: 20260125_0002
Revises: 20260124_0001
Create Date: 2026-01-25
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260125_0002"
down_revision = "20260124_0001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_submissions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("seller_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("short_description", sa.String(length=500), nullable=True),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("subcategory", sa.String(length=50), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("license_type", sa.String(length=20), nullable=False),
        sa.Column("tech_stack", sa.JSON(), nullable=True),
        sa.Column("framework", sa.String(length=50), nullable=True),
        sa.Column("requirements", sa.Text(), nullable=True),
        sa.Column("preview_images", sa.JSON(), nullable=True),
        sa.Column("demo_url", sa.String(length=255), nullable=True),
        sa.Column("documentation_url", sa.String(length=255), nullable=True),
        sa.Column("package_url", sa.Text(), nullable=True),
        sa.Column("package_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("audit_report", sa.JSON(), nullable=True),
        sa.Column("audit_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("audit_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("audit_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("product_id", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["seller_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_submissions_seller_id", "project_submissions", ["seller_id"])
    op.create_index("ix_project_submissions_status", "project_submissions", ["status"])
    op.create_index("ix_project_submissions_product_id", "project_submissions", ["product_id"])


def downgrade():
    op.drop_index("ix_project_submissions_product_id", table_name="project_submissions")
    op.drop_index("ix_project_submissions_status", table_name="project_submissions")
    op.drop_index("ix_project_submissions_seller_id", table_name="project_submissions")
    op.drop_table("project_submissions")
