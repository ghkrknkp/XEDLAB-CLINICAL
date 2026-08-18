"""Initial Schema for AI Medical Report Analyzer

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-17 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        'users',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # 2. reports
    op.create_table(
        'reports',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('report_id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('stored_path', sa.String(), nullable=False),
        sa.Column('storage_type', sa.String(), server_default='local'),
        sa.Column('report_type', sa.String(), server_default='Unknown'),
        sa.Column('report_type_confidence', sa.Float(), server_default='0.0'),
        sa.Column('processing_status', sa.String(), server_default='queued'),
        sa.Column('page_count', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_reports_user_id'), 'reports', ['user_id'], unique=False)
    op.create_index(op.f('ix_reports_report_id'), 'reports', ['report_id'], unique=True)
    op.create_index(op.f('ix_reports_created_at'), 'reports', ['created_at'], unique=False)

    # 3. report_pages
    op.create_table(
        'report_pages',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('raw_text', sa.Text(), server_default=''),
        sa.Column('cleaned_text', sa.Text(), server_default=''),
        sa.Column('ocr_used', sa.Boolean(), server_default='0'),
    )
    op.create_index(op.f('ix_report_pages_report_id'), 'report_pages', ['report_id'], unique=False)

    # 4. entities
    op.create_table(
        'entities',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('page_number', sa.Integer(), server_default='1'),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_text', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), server_default='0.8'),
    )
    op.create_index(op.f('ix_entities_report_id'), 'entities', ['report_id'], unique=False)

    # 5. lab_results
    op.create_table(
        'lab_results',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('page_number', sa.Integer(), server_default='1'),
        sa.Column('test_name', sa.String(), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(), nullable=True),
        sa.Column('reference_low', sa.Float(), nullable=True),
        sa.Column('reference_high', sa.Float(), nullable=True),
        sa.Column('original_reference_text', sa.String(), nullable=True),
        sa.Column('reference_text', sa.String(), nullable=True),
        sa.Column('status', sa.String(), server_default='not_classified'),
        sa.Column('confidence', sa.Float(), server_default='0.5'),
        sa.Column('source_text', sa.String(), server_default=''),
    )
    op.create_index(op.f('ix_lab_results_report_id'), 'lab_results', ['report_id'], unique=False)

    # 6. summaries
    op.create_table(
        'summaries',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('model', sa.String(), server_default='rule-based'),
        sa.Column('summary_source', sa.String(), server_default='deterministic_fallback'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_summaries_report_id'), 'summaries', ['report_id'], unique=False)

    # 7. embeddings
    op.create_table(
        'embeddings',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding', sa.Text(), nullable=False),
        sa.Column('page_number', sa.Integer(), server_default='1'),
        sa.Column('section_name', sa.String(), server_default='General'),
    )
    op.create_index(op.f('ix_embeddings_report_id'), 'embeddings', ['report_id'], unique=False)

    # 8. jobs
    op.create_table(
        'jobs',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('status', sa.String(), server_default='queued'),
        sa.Column('stage', sa.String(), server_default='QUEUED'),
        sa.Column('progress', sa.Integer(), server_default='0'),
        sa.Column('error_code', sa.String(), nullable=True),
        sa.Column('safe_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_jobs_report_id'), 'jobs', ['report_id'], unique=False)
    op.create_index(op.f('ix_jobs_created_at'), 'jobs', ['created_at'], unique=False)

    # 9. conversations & messages
    op.create_table(
        'conversations',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_conversations_report_id'), 'conversations', ['report_id'], unique=False)
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    op.create_table(
        'messages',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('conversation_id', sa.String(), sa.ForeignKey('conversations.id'), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources_json', sa.Text(), server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)

    # 10. audit_events
    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('report_id', sa.String(), sa.ForeignKey('reports.id'), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('details', sa.String(), server_default=''),
    )
    op.create_index(op.f('ix_audit_events_user_id'), 'audit_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_audit_events_report_id'), 'audit_events', ['report_id'], unique=False)


def downgrade() -> None:
    op.drop_table('audit_events')
    op.drop_table('messages')
    op.drop_table('conversations')
    op.drop_table('jobs')
    op.drop_table('embeddings')
    op.drop_table('summaries')
    op.drop_table('lab_results')
    op.drop_table('entities')
    op.drop_table('report_pages')
    op.drop_table('reports')
    op.drop_table('users')
