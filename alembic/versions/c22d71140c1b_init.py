"""init

Revision ID: c22d71140c1b
Revises:
Create Date: 2023-10-31 19:14:16.002918

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = 'c22d71140c1b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Group',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_Group_id'), 'Group', ['id'], unique=False)
    op.create_table('Media',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('path', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_Media_id'), 'Media', ['id'], unique=False)
    op.create_table('Role',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('ImageMedia',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('file_format', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('width', sa.Integer(), nullable=True),
    sa.Column('height', sa.Integer(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('media_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.ForeignKeyConstraint(['media_id'], ['Media.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ImageMedia_id'), 'ImageMedia', ['id'], unique=False)
    op.create_index(op.f('ix_Role_id'), 'Role', ['id'], unique=False)
    op.create_table('Scope',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_Scope_id'), 'Scope', ['id'], unique=False)
    op.create_table('User',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('email', sa.VARCHAR(), nullable=True),
    sa.Column('first_visit', sa.DateTime(timezone=True), nullable=True),
    sa.Column('last_visit', sa.DateTime(timezone=True), nullable=True),
    sa.Column('email_verified', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_new', sa.Boolean(), nullable=False),
    sa.Column('role_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('country', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('email_notification', sa.Boolean(), nullable=True),
    sa.Column('discord_notification', sa.Boolean(), nullable=True),
    sa.Column('newsletter_notification', sa.Boolean(), nullable=True),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('first_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('last_name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('phone', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('image_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('policies_consent', sa.Boolean(), nullable=True),
    sa.Column('primary_wallet_id', sqlmodel.sql.sqltypes.GUID(), nullable=True),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.ForeignKeyConstraint(['image_id'], ['ImageMedia.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['Role.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_User_email'), 'User', ['email'], unique=True)
    op.create_index(op.f('ix_User_id'), 'User', ['id'], unique=False)
    op.create_table('Wallet',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('chain', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('public_key', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('public_key')
    )
    op.create_index(op.f('ix_Wallet_id'), 'Wallet', ['id'], unique=False)

    # Added Manually
    op.create_foreign_key("User_primary_wallet_id_fkey", "User", "Wallet", ["primary_wallet_id"], ["id"])

    op.create_table('GroupScopeLink',
    sa.Column('group_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('scope_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['Group.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['scope_id'], ['Scope.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('group_id', 'scope_id')
    )
    op.create_table('GroupUserLink',
    sa.Column('group_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['group_id'], ['Group.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('group_id', 'user_id')
    )
    op.create_table('RoleScopeLink',
    sa.Column('role_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('scope_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['Role.id'], ondelete='cascade'),
    sa.ForeignKeyConstraint(['scope_id'], ['Scope.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('role_id', 'scope_id')
    )
    op.create_table('SocialAccount',
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('provider', sa.VARCHAR(), nullable=False),
    sa.Column('user_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('username', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('account_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'provider')
    )
    op.create_index(op.f('ix_SocialAccount_id'), 'SocialAccount', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_SocialAccount_id'), table_name='SocialAccount')
    op.drop_table('SocialAccount')
    op.drop_table('RoleScopeLink')
    op.drop_index(op.f('ix_ImageMedia_id'), table_name='ImageMedia')
    op.drop_table('ImageMedia')
    op.drop_table('GroupUserLink')
    op.drop_table('GroupScopeLink')
    op.drop_index(op.f('ix_Wallet_id'), table_name='Wallet')
    op.drop_table('Wallet')
    op.drop_index(op.f('ix_User_id'), table_name='User')
    op.drop_index(op.f('ix_User_email'), table_name='User')
    op.drop_table('User')
    op.drop_index(op.f('ix_Scope_id'), table_name='Scope')
    op.drop_table('Scope')
    op.drop_index(op.f('ix_Role_id'), table_name='Role')
    op.drop_table('Role')
    op.drop_index(op.f('ix_Media_id'), table_name='Media')
    op.drop_table('Media')
    op.drop_index(op.f('ix_Group_id'), table_name='Group')
    op.drop_table('Group')
    # ### end Alembic commands ###
