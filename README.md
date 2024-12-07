# FarmTasks

A Flask-based task management system designed specifically for farm operations.

## Description
FarmTasks helps farm managers organize and track daily tasks, create task templates, and manage worker assignments efficiently.

## Features
- Task Management
  - Create and manage task templates
  - Assign tasks to workers
  - Track task completion
  
- Day Templates
  - Create reusable daily task templates
  - Schedule tasks with specific times
  - Bulk duplicate templates
  
- User Management
  - Admin and worker roles
  - User assignment tracking
  - Task completion history

## Technology Stack
- Backend: Python/Flask
- Database: PostgreSQL
- Frontend: HTML/CSS
- Docker for development environment

## Installation

1. Clone the repository: 

git clone https://github.com/centralchaos/FarmTasks.git
cd FarmTasks

2. Set up Docker environment:

docker-compose up -d

3. Install Python dependencies:

python -m venv farmtasks
source farmtasks/bin/activate # On Windows: farmtasks\Scripts\activate
pip install -r requirements.txt

4. Run the application:

flask run

5. Access the application:
- Visit http://localhost:5000
- Complete the installation wizard
- Create admin account

## Project Structure

FarmTasks/
├── app/
│ ├── main/                    # Main application routes
│ │ ├── __init__.py
│ │ └── routes.py
│ ├── installer/               # Installation wizard
│ │ ├── __init__.py
│ │ └── routes.py
│ ├── templates/               # HTML templates
│ │ ├── base.html
│ │ ├── dashboard.html
│ │ ├── day_templates/
│ │ └── tasks/
│ ├── static/                  # CSS, JS files
│ │ └── css/
│ │ └── style.css
│ ├── __init__.py             # Application factory
│ ├── extensions.py           # Flask extensions
│ ├── models.py               # Database models
│ └── utils.py                # Utility functions
├── docker-compose.yml          # Docker configuration
├── instance/                   # Instance configuration
│ └── config.py
├── reset_installation.py      # Installation reset script
├── requirements.txt           # Python dependencies
└── run.py                    # Application entry point


## Development
- Reset installation:python reset_installation.py`
- Database migrations: `flask db upgrade`
- Run tests: `python -m pytest`

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Authors
- centralchaos / Jose Carlo Sia `