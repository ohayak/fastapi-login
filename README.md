# Login API

This API is designed to serve as a base for custom APIs that require user management and login functionality. It is built using FastAPI and SQLModel, and follows the CRUD (Create, Read, Update, Delete) pattern for data management.

This API provides a range of features for user management and authentication. Here are the main features available:

1. User Management: The API provides comprehensive user management features. You can create, read, update, and delete users. The user model includes fields like first name, last name, email, phone, and more.

2. Group Management: The API allows you to manage groups. You can create, read, update, and delete groups. The group model includes fields like name and description.

3. Authentication: The API provides robust authentication features. It includes methods for user authentication, password hashing, and token generation.

4. Role-Based Access Control (RBAC): The API supports role-based access control. This allows you to assign roles to users and control their access to resources based on their role.

5. Social Login: The API supports social login. This allows users to log in using their social media accounts.

6. Pagination: The API supports pagination. This allows you to retrieve data in small chunks, which can improve performance for large datasets.

7. Filtering: The API supports filtering. This allows you to retrieve data based on specific criteria.


## Models

Models are Python classes that define the structure of the data. They are used to interact with the database. Here are some of the models used in this API:

- User: Represents a user in the system. It includes fields like first_name, last_name, email, email_verified, is_active, is_superuser, role_id, phone, and image_id.

- Group: Represents a group in the system. It includes fields like name, description, created_by_id, and users.

## Schemas

Schemas are Pydantic models that are used for data validation and serialization. They define the structure of the data that is sent and received by the API. Here are some of the schemas used in this API:

- IUserCreate: Defines the data required to create a new user.
- IGroupCreate: Defines the data required to create a new group.

## CRUD Operations

CRUD operations are defined in the crud directory. Each file in this directory corresponds to a model and defines the CRUD operations for that model. Here are some of the CRUD operations defined in this API:

- CRUDUser: Defines the CRUD operations for the User model. It includes methods like get_by_email, create_with_role, add_social_login, and authenticate.
- CRUDGroup: Defines the CRUD operations for the Group model.

## Endpoints

Endpoints are defined in the api directory. Each file in this directory corresponds to a model and defines the endpoints for that model. Here are some of the endpoints defined in this API:

- list_users: Retrieves a list of users. Requires the admin or manager role.
- login: Authenticates a user and returns a token.

## Quickstart

To start the application, use the command `docker-compose up`

## For Developers

This section provides a guide for developers on how to set up and manage the application.

### Installation

The application requires certain dependencies to run. These dependencies are listed in the `requirements.txt` file. To install these dependencies, run the following command in your terminal: `pip install -r requirements.txt`.

### Starting the Application

Once the dependencies are installed, you can start the application using the `main.py` script. This script accepts several command line arguments:
   - `-v` or `--verbose`: Enables verbose output.
   - `-e` or `--dotenv`: Loads the .env file.
   - `-m` or `--migrate`: Runs database migrations.
   - `-i` or `--init`: Initializes the database.
   - `-r` or `--reload`: Starts the application in reload mode.
   To start the application, run the following command in your terminal: `python main.py`.

### Managing Data Migrations

The application uses Alembic to manage data migrations. Alembic is a database migration tool for SQLAlchemy. Here are the steps to manage data migrations:
   - Generate a Migration Script: After initializing Alembic, you can generate a migration script. The migration script contains the changes you want to make to your database. Run the following command in your terminal to generate a migration script: `alembic revision --autogenerate -m "Your message"`.
   - Apply Migrations: Once you have a migration script, you can apply the migrations to your database. Run the following command in your terminal to apply migrations: `alembic upgrade head`.
