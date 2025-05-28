"""add legal texts table

Revision ID: ad9f5c7e8b23
Revises: create_default_admin
Create Date: 2025-05-20 19:59:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ad9f5c7e8b23'
down_revision = 'create_default_admin'
branch_labels = None
depends_on = None


def upgrade():
    # 检查表是否已存在
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'legal_texts' not in tables:
        # 创建legal_texts表
        op.create_table(
            'legal_texts',
            sa.Column('id', sa.Integer(), primary_key=True),
            sa.Column('type', sa.String(50), nullable=False, index=True),  # 文本类型
            sa.Column('subtype', sa.String(50), nullable=True, index=True),  # 子类型
            sa.Column('content', sa.Text(), nullable=True),  # 文本内容
            sa.Column('version', sa.String(20), nullable=False),  # 版本号
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(),
                      onupdate=sa.func.now(), nullable=False),
            sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
            sa.Column('language', sa.String(10), nullable=False, default='zh-CN'),  # 语言代码
            sa.Column('content_path', sa.String(255), nullable=True),  # 指向文件系统中的文件路径
        )

        # 创建索引
        op.create_index('idx_legal_texts_type_subtype', 'legal_texts', ['type', 'subtype'])
        op.create_index('idx_legal_texts_language', 'legal_texts', ['language'])
        op.create_index('idx_legal_texts_version', 'legal_texts', ['version'])
        op.create_index('idx_legal_texts_is_active', 'legal_texts', ['is_active'])
        print("legal_texts表已创建")
    else:
        print("legal_texts表已存在，跳过创建")


def downgrade():
    # 删除表和索引
    op.drop_index('idx_legal_texts_is_active', table_name='legal_texts')
    op.drop_index('idx_legal_texts_version', table_name='legal_texts')
    op.drop_index('idx_legal_texts_language', table_name='legal_texts')
    op.drop_index('idx_legal_texts_type_subtype', table_name='legal_texts')
    op.drop_table('legal_texts')