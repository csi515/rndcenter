# R&D Center Management System

## Overview
This is a Flask-based web application designed for managing a Research & Development center. The system provides comprehensive functionality for managing research projects, patents, equipment, inventory, safety protocols, purchasing, and communication within an R&D environment. It uses a file-based CSV data storage approach for simplicity and portability.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 dark theme
- **UI Framework**: Bootstrap 5 with Font Awesome icons
- **JavaScript Libraries**: FullCalendar for scheduling, custom JavaScript for interactivity
- **Responsive Design**: Mobile-first approach with Bootstrap grid system
- **Dark Theme**: Consistent dark theme throughout the application

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Architecture Pattern**: Blueprint-based modular structure
- **Session Management**: Flask sessions with configurable secret key
- **Error Handling**: Flash messages for user feedback
- **Logging**: Python logging module for debugging

### Data Storage
- **Primary Storage**: CSV files managed through a custom CSVManager class
- **File Structure**: All data stored in `/data` directory as CSV files
- **Data Operations**: CRUD operations through pandas DataFrame manipulation
- **File Management**: Automatic directory creation and UTF-8 encoding support

## Key Components

### 1. Application Core (`app.py`)
- Flask application initialization
- Blueprint registration for modular routing
- Session and security configuration
- WSGI middleware for proxy support

### 2. Data Management (`csv_manager.py`)
- CSVManager class for file operations
- DataFrame-based data manipulation
- Error handling and logging
- Support for append, update, and read operations

### 3. Route Modules
- **Dashboard** (`routes/dashboard.py`): Overview statistics and recent activities
- **Research** (`routes/research.py`): Project management and researcher tracking
- **Patents** (`routes/patents.py`): Intellectual property management
- **Equipment** (`routes/equipment.py`): Equipment tracking and reservations
- **Inventory** (`routes/inventory.py`): Stock management and tracking
- **Safety** (`routes/safety.py`): Accident reporting and safety protocols
- **Purchasing** (`routes/purchasing.py`): Purchase request management
- **Communication** (`routes/communication.py`): Internal communication and Q&A
- **External** (`routes/external.py`): Contact management
- **Chemical** (`routes/chemical.py`): MSDS and chemical substance management

### 4. Frontend Components
- **Base Template**: Consistent layout with sidebar navigation
- **Responsive Tables**: Data display with search and filter capabilities
- **Modal Forms**: Bootstrap modals for data entry
- **Calendar Integration**: FullCalendar for schedule management
- **Interactive Elements**: JavaScript-enhanced user experience

## Data Flow

### 1. Request Processing
1. User initiates action through web interface
2. Flask routes handle HTTP requests
3. Route handlers process form data or API calls
4. CSVManager performs data operations
5. Results returned to user through templates or JSON responses

### 2. Data Operations
1. **Create**: Form submissions append new records to CSV files
2. **Read**: CSV data loaded into pandas DataFrames for display
3. **Update**: Row-specific updates modify existing records
4. **Delete**: Records marked as inactive or physically removed

### 3. File Management
- CSV files stored in `/data` directory
- Automatic file creation when accessing non-existent files
- UTF-8 encoding for international character support
- Index-based record identification for updates

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **pandas**: Data manipulation and analysis
- **Werkzeug**: WSGI utilities and proxy fix

### Frontend Libraries
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome 6**: Icon library
- **FullCalendar 6**: Calendar and scheduling
- **jQuery**: JavaScript utilities (implied by Bootstrap)

### File Dependencies
- CSV files in `/data` directory for data persistence
- Static files for CSS, JavaScript, and images
- Template files for HTML rendering

## Deployment Strategy

### Development Environment
- Flask development server on port 5000
- Debug mode enabled for development
- Hot reloading for code changes
- Local file-based storage

### Production Considerations
- WSGI-compatible deployment (Gunicorn, uWSGI)
- Environment variable configuration for secrets
- Proxy support through ProxyFix middleware
- File backup and recovery procedures

### Configuration Management
- Session secret from environment variables
- Debug mode configurable
- Host and port configuration
- Data directory path configuration

## Changelog
- July 01, 2025. Initial setup

## User Preferences
Preferred communication style: Simple, everyday language.