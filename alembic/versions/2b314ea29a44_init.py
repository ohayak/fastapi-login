"""init

Revision ID: 2b314ea29a44
Revises:
Create Date: 2022-12-23 04:50:31.115833

"""
import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision = "2b314ea29a44"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "Media",
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("path", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Media_id"), "Media", ["id"], unique=False)
    op.create_table(
        "ImageMedia",
        sa.Column("file_format", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("media_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(["media_id"], ["Media.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ImageMedia_id"), "ImageMedia", ["id"], unique=False)
    op.create_table(
        "Role",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Role_id"), "Role", ["id"], unique=False)
    op.create_table(
        "User",
        sa.Column("birthdate", sa.DateTime(timezone=True), nullable=True),
        sa.Column("first_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("last_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("role_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("phone", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("country", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("address", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("image_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(["image_id"], ["ImageMedia.id"], ondelete="set null"),
        sa.ForeignKeyConstraint(["role_id"], ["Role.id"], ondelete="set null"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_User_email"), "User", ["email"], unique=True)
    op.create_index(op.f("ix_User_hashed_password"), "User", ["hashed_password"], unique=False)
    op.create_index(op.f("ix_User_id"), "User", ["id"], unique=False)
    op.create_table(
        "Group",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(["created_by_id"], ["User.id"], ondelete="set null"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Group_id"), "Group", ["id"], unique=False)
    op.create_table(
        "LinkGroupUser",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("group_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(["group_id"], ["Group.id"], ondelete="cascade"),
        sa.ForeignKeyConstraint(["user_id"], ["User.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("id", "group_id", "user_id"),
    )
    op.create_index(op.f("ix_LinkGroupUser_id"), "LinkGroupUser", ["id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_LinkGroupUser_id"), table_name="LinkGroupUser")
    op.drop_table("LinkGroupUser")
    op.drop_index(op.f("ix_Group_id"), table_name="Group")
    op.drop_table("Group")
    op.drop_index(op.f("ix_User_id"), table_name="User")
    op.drop_index(op.f("ix_User_hashed_password"), table_name="User")
    op.drop_index(op.f("ix_User_email"), table_name="User")
    op.drop_table("User")
    op.drop_index(op.f("ix_ImageMedia_id"), table_name="ImageMedia")
    op.drop_table("ImageMedia")
    op.drop_index(op.f("ix_Role_id"), table_name="Role")
    op.drop_table("Role")
    op.drop_index(op.f("ix_Media_id"), table_name="Media")
    op.drop_table("Media")
    # ### end Alembic commands ###
