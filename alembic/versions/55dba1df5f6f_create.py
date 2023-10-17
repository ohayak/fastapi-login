"""create

Revision ID: 55dba1df5f6f
Revises:
Create Date: 2022-12-24 01:51:11.469357

"""
import sqlalchemy as sa
import sqlmodel

from alembic import op

# revision identifiers, used by Alembic.
revision = "55dba1df5f6f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
    op.execute(sa.text("CREATE CAST (varchar AS uuid) WITH INOUT AS IMPLICIT"))
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
        sa.ForeignKeyConstraint(
            ["media_id"],
            ["Media.id"],
        ),
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
        sa.Column("first_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("last_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("role_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("phone", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("image_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("hashed_password", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("social_logins", sa.ARRAY(sa.VARCHAR()), nullable=True),
        sa.ForeignKeyConstraint(
            ["image_id"],
            ["ImageMedia.id"],
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["Role.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_User_email"), "User", ["email"], unique=True)
    op.create_index(op.f("ix_User_id"), "User", ["id"], unique=False)
    op.create_table(
        "Group",
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("created_by_id", sqlmodel.sql.sqltypes.GUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["created_by_id"],
            ["User.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_Group_id"), "Group", ["id"], unique=False)
    op.create_table(
        "LinkGroupUser",
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("group_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("user_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["Group.id"],
            ondelete="cascade",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["User.id"],
            ondelete="cascade",
        ),
        sa.PrimaryKeyConstraint("group_id", "user_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("LinkGroupUser")
    op.drop_index(op.f("ix_Group_id"), table_name="Group")
    op.drop_table("Group")
    op.drop_index(op.f("ix_User_id"), table_name="User")
    op.drop_index(op.f("ix_User_email"), table_name="User")
    op.drop_table("User")
    op.drop_index(op.f("ix_Role_id"), table_name="Role")
    op.drop_table("Role")
    op.drop_index(op.f("ix_ImageMedia_id"), table_name="ImageMedia")
    op.drop_table("ImageMedia")
    op.drop_index(op.f("ix_Media_id"), table_name="Media")
    op.drop_table("Media")
    op.execute(sa.text("DROP CAST IF EXISTS (varchar AS uuid)"))
    op.execute(sa.text("DROP EXTENSION IF EXISTS pg_trgm"))
    # ### end Alembic commands ###
