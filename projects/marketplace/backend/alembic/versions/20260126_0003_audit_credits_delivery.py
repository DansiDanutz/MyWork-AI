"""add audit runs, repo snapshots, credits ledger, and submission metadata

Revision ID: 20260126_0003
Revises: 20260125_0002
Create Date: 2026-01-26
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20260126_0003"
down_revision = "20260125_0002"
branch_labels = None
depends_on = None


def upgrade():
    # Users: credit balance
    op.add_column(
        "users",
        sa.Column("credit_balance", sa.Numeric(12, 2), server_default="0.00", nullable=False),
    )
    op.add_column(
        "users",
        sa.Column("credit_currency", sa.String(length=3), server_default="USD", nullable=False),
    )

    # Submissions: repo + audit metadata + brain + IP consent
    op.add_column("project_submissions", sa.Column("repo_url", sa.Text(), nullable=True))
    op.add_column("project_submissions", sa.Column("repo_ref", sa.String(length=255), nullable=True))
    op.add_column("project_submissions", sa.Column("repo_commit_sha", sa.String(length=64), nullable=True))
    op.add_column("project_submissions", sa.Column("repo_provider", sa.String(length=50), nullable=True))
    op.add_column("project_submissions", sa.Column("audit_profile", sa.String(length=50), nullable=True))
    op.add_column("project_submissions", sa.Column("audit_plan_version", sa.String(length=50), nullable=True))
    op.add_column(
        "project_submissions",
        sa.Column("brain_opt_in", sa.Boolean(), server_default=sa.text("true"), nullable=False),
    )
    op.add_column("project_submissions", sa.Column("brain_ingest_status", sa.String(length=20), nullable=True))
    op.add_column("project_submissions", sa.Column("brain_ingested_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column(
        "project_submissions",
        sa.Column("ip_consent", sa.Boolean(), server_default=sa.text("false"), nullable=False),
    )

    # Audit runs
    op.create_table(
        "audit_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("submission_id", sa.String(length=36), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("score", sa.Numeric(5, 2), nullable=True),
        sa.Column("report", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("logs_url", sa.Text(), nullable=True),
        sa.Column("gsd_run_id", sa.String(length=100), nullable=True),
        sa.Column("pipeline_version", sa.String(length=50), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["project_submissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_runs_submission_id", "audit_runs", ["submission_id"])
    op.create_index("ix_audit_runs_status", "audit_runs", ["status"])

    # Repo snapshots
    op.create_table(
        "repo_snapshots",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("submission_id", sa.String(length=36), nullable=False),
        sa.Column("repo_url", sa.Text(), nullable=False),
        sa.Column("repo_ref", sa.String(length=255), nullable=True),
        sa.Column("commit_sha", sa.String(length=64), nullable=True),
        sa.Column("tag", sa.String(length=100), nullable=True),
        sa.Column("archive_url", sa.Text(), nullable=True),
        sa.Column("archive_sha256", sa.String(length=64), nullable=True),
        sa.Column("sbom_url", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["submission_id"], ["project_submissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_repo_snapshots_submission_id", "repo_snapshots", ["submission_id"])
    op.create_index("ix_repo_snapshots_commit_sha", "repo_snapshots", ["commit_sha"])

    # Delivery artifacts
    op.create_table(
        "delivery_artifacts",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("order_id", sa.String(length=36), nullable=True),
        sa.Column("submission_id", sa.String(length=36), nullable=True),
        sa.Column("product_id", sa.String(length=36), nullable=True),
        sa.Column("snapshot_id", sa.String(length=36), nullable=True),
        sa.Column("artifact_url", sa.Text(), nullable=True),
        sa.Column("artifact_sha256", sa.String(length=64), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.ForeignKeyConstraint(["snapshot_id"], ["repo_snapshots.id"]),
        sa.ForeignKeyConstraint(["submission_id"], ["project_submissions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_delivery_artifacts_order_id", "delivery_artifacts", ["order_id"])
    op.create_index("ix_delivery_artifacts_submission_id", "delivery_artifacts", ["submission_id"])
    op.create_index("ix_delivery_artifacts_product_id", "delivery_artifacts", ["product_id"])
    op.create_index("ix_delivery_artifacts_snapshot_id", "delivery_artifacts", ["snapshot_id"])
    op.create_index("ix_delivery_artifacts_status", "delivery_artifacts", ["status"])

    # Credits ledger
    op.create_table(
        "credit_ledger",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("entry_type", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("related_order_id", sa.String(length=36), nullable=True),
        sa.Column("related_submission_id", sa.String(length=36), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["related_order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["related_submission_id"], ["project_submissions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_credit_ledger_user_id", "credit_ledger", ["user_id"])
    op.create_index("ix_credit_ledger_entry_type", "credit_ledger", ["entry_type"])
    op.create_index("ix_credit_ledger_status", "credit_ledger", ["status"])


def downgrade():
    op.drop_index("ix_credit_ledger_status", table_name="credit_ledger")
    op.drop_index("ix_credit_ledger_entry_type", table_name="credit_ledger")
    op.drop_index("ix_credit_ledger_user_id", table_name="credit_ledger")
    op.drop_table("credit_ledger")

    op.drop_index("ix_delivery_artifacts_status", table_name="delivery_artifacts")
    op.drop_index("ix_delivery_artifacts_snapshot_id", table_name="delivery_artifacts")
    op.drop_index("ix_delivery_artifacts_product_id", table_name="delivery_artifacts")
    op.drop_index("ix_delivery_artifacts_submission_id", table_name="delivery_artifacts")
    op.drop_index("ix_delivery_artifacts_order_id", table_name="delivery_artifacts")
    op.drop_table("delivery_artifacts")

    op.drop_index("ix_repo_snapshots_commit_sha", table_name="repo_snapshots")
    op.drop_index("ix_repo_snapshots_submission_id", table_name="repo_snapshots")
    op.drop_table("repo_snapshots")

    op.drop_index("ix_audit_runs_status", table_name="audit_runs")
    op.drop_index("ix_audit_runs_submission_id", table_name="audit_runs")
    op.drop_table("audit_runs")

    op.drop_column("project_submissions", "ip_consent")
    op.drop_column("project_submissions", "brain_ingested_at")
    op.drop_column("project_submissions", "brain_ingest_status")
    op.drop_column("project_submissions", "brain_opt_in")
    op.drop_column("project_submissions", "audit_plan_version")
    op.drop_column("project_submissions", "audit_profile")
    op.drop_column("project_submissions", "repo_provider")
    op.drop_column("project_submissions", "repo_commit_sha")
    op.drop_column("project_submissions", "repo_ref")
    op.drop_column("project_submissions", "repo_url")

    op.drop_column("users", "credit_currency")
    op.drop_column("users", "credit_balance")
