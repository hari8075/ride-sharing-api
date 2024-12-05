Ride-Sharing API
Overview
The Ride-Sharing API is a backend application built using Django and Django Rest Framework. It facilitates a ride-sharing system where:

Riders can request rides.
Drivers can accept rides and complete them.
Unique features include rider verification using a 4-digit code, ride status tracking, and JWT-based authentication for secure access.

Features
Role-Based Access:
Riders can create and cancel rides.
Drivers can accept, start, and complete rides.
Authentication:
JWT-based authentication for secure API access.
Ride Status Management:
Pending, Accepted, Started, Completed, and Cancelled.
Unique Ride Codes:
Each rider is assigned a unique 4-digit code for ride verification.
Endpoints for Drivers and Riders:
Includes actions like accepting, starting, completing, and canceling rides.


Technologies Used
Framework: Django, Django Rest Framework (DRF)
Authentication: Simple JWT
Database: SQLite
Version Control: GitHub

