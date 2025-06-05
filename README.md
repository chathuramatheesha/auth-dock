Auth Dock

Auth Dock is a full-featured authentication API built with FastAPI. It offers robust features like user registration,
email verification, JWT-based authentication with refresh tokens, token blacklisting, Argon2 password hashing,
role-based access control, an admin panel, and email integration using Gmail or SendGrid.
🚀 Features

    User Registration & Login

    Email Verification

    JWT Authentication with Access & Refresh Tokens

    Token Blacklisting on Logout

    Argon2 Password Hashing

    Role-Based Access Control (RBAC)

    Admin Panel

    Email Integration (Gmail/SendGrid)

    Asynchronous Support with FastAPI

    Pytest Test Suite
    restack.io+2github.com+2forum.cortezaproject.org+2
    restack.io

🛠️ Installation

    Clone the repository:

    git clone https://github.com/chathuramatheesha/auth-dock.git
    cd auth-dock

    Create a virtual environment and activate it:

    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    Install dependencies:

    pip install -r requirements.txt

    Configure environment variables:

    Create a .env file in the root directory and add the necessary configurations:

    DATABASE_URL=sqlite+aiosqlite:///./test.db
    SECRET_KEY=your_secret_key
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    REFRESH_TOKEN_EXPIRE_MINUTES=1440
    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=465
    SMTP_USERNAME=your_email@gmail.com
    SMTP_PASSWORD=your_email_password

    Run database migrations:

    alembic upgrade head

    Start the application:

    uvicorn src.main:app --reload

📂 Project Structure

auth-dock/
├── alembic/ # Database migrations
├── src/ # Application source code
│ ├── api/ # API routes
│ ├── core/ # Core configurations and utilities
│ ├── models/ # Database models
│ ├── schemas/ # Pydantic schemas
│ ├── services/ # Business logic
│ └── main.py # Application entry point
├── tests/ # Test cases
├── .env # Environment variables
├── requirements.txt # Python dependencies
├── alembic.ini # Alembic configuration
└── README.md # Project documentation

🔐 Authentication Flow

    User Registration:

        Endpoint: POST /api/v1/auth/register

        Registers a new user and sends a verification email.

    Email Verification:

        Endpoint: GET /api/v1/auth/verify-email?token=...

        Verifies the user's email address.

    User Login:

        Endpoint: POST /api/v1/auth/login

        Authenticates the user and returns access and refresh tokens.

    Token Refresh:

        Endpoint: POST /api/v1/auth/refresh

        Provides a new access token using the refresh token.

    Logout:

        Endpoint: POST /api/v1/auth/logout

        Blacklists the refresh token to prevent further use.

🧪 Running Tests

pytest

Ensure that your test database is configured correctly in the .env file before running tests.
📬 Email Integration

The application supports sending emails via Gmail or SendGrid. Configure the SMTP settings in the .env file:

SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_email_password

For SendGrid, use the appropriate SMTP host and port, and provide your SendGrid credentials.
🛡️ Security Features

    Argon2 Password Hashing:

        Provides a secure way to store user passwords.

    Token Blacklisting:

        Ensures that refresh tokens are invalidated upon logout.

    Role-Based Access Control (RBAC):

        Assign roles to users and restrict access to certain endpoints based on roles.

📖 API Documentation

Once the application is running, access the interactive API docs at:

    Swagger UI: http://localhost:8000/docs

    ReDoc: http://localhost:8000/redoc
    github.com+1github.com+1

🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request. For major changes, open an issue first
to discuss what you would like to change.
📄 License

This project is licensed under the MIT License. See the LICENSE file for details.