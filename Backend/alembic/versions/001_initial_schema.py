"""initial schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-18 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from app.models.guid import GUID

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create application_status enum for PostgreSQL
    bind = op.get_bind()
    status_enum = postgresql.ENUM(
        'applied', 'oa', 'interview', 'offer', 'rejected', 'withdrawn',
        name='application_status',
        create_type=False
    )
    if bind.dialect.name == 'postgresql':
        status_enum.create(bind, checkfirst=True)

    # 1. users table
    op.create_table(
        'users',
        sa.Column('user_id', GUID(), primary_key=True),
        sa.Column('user_name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # 2. resumes table
    op.create_table(
        'resumes',
        sa.Column('resume_id', GUID(), primary_key=True),
        sa.Column('user_id', GUID(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('resume_name', sa.String(length=150), nullable=False),
        sa.Column('resume_key', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_resumes_user_id', 'resumes', ['user_id'])

    # 3. applications table
    app_status_type = (
        status_enum
        if bind.dialect.name == 'postgresql'
        else sa.Enum('applied', 'oa', 'interview', 'offer', 'rejected', 'withdrawn', name='application_status')
    )
    op.create_table(
        'applications',
        sa.Column('application_id', GUID(), primary_key=True),
        sa.Column('user_id', GUID(), sa.ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False),
        sa.Column('resume_id', GUID(), sa.ForeignKey('resumes.resume_id', ondelete='SET NULL'), nullable=True),
        sa.Column('company_name', sa.String(length=150), nullable=False),
        sa.Column('role_name', sa.String(length=150), nullable=False),
        sa.Column('ctc_amount', sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column('ctc_currency', sa.String(length=3), server_default='INR', nullable=False),
        sa.Column('status', app_status_type, server_default='applied', nullable=False),
        sa.Column('job_description_url', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    op.create_index('ix_applications_resume_id', 'applications', ['resume_id'])


def downgrade() -> None:
    op.drop_table('applications')
    op.drop_table('resumes')
    op.drop_table('users')
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        status_enum = postgresql.ENUM(name='application_status')
        status_enum.drop(bind, checkfirst=True)
