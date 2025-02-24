# Website Monitor

Website Monitor is a Django-based application that tracks website uptime and downtime, logs response times, and provides real-time notifications via SMS and email. Built with Celery and Redis for handling background tasks and SQLite for data storage, this project enables efficient and scalable website performance monitoring.

## Features

- **Real-Time Uptime Monitoring**: Continuously checks the uptime and downtime of specified websites, logging response times for analysis.
- **Notification Options**: Offers multiple notification methods (SMS and email) to alert users of any downtime events in real-time.
- **Asynchronous Task Processing**: Uses Celery with Redis as a message broker to run background tasks without blocking the main application.
- **User Management**: Role-based access controls allow secure user management, with customizable experiences based on user roles.
  
## Technology Stack

- **Backend**: Django, Celery, Redis, PostgreSQL
- **Frontend**: HTML, CSS, JavaScript
- **Dependencies**: Django REST Framework, Twilio API for SMS notifications, SMTP for email

## Getting Started

### Prerequisites

- Python 3.8+
- Django 4.x
- SQLite
- Redis
- Celery
