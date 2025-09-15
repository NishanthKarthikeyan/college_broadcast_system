# College Broadcast Notification System 📢

A simple web application built with Flask that allows a college administrator to send bulk announcements to parents. The system uses CSV files to manage parent contact information and allows for flexible filtering by academic year and department.

## Features ✨

- **Secure Admin Login**: A dedicated login page protects the dashboard from unauthorized access.
- **Protected Dashboard**: Only logged-in users can view the dashboard and use the broadcasting features.
- **Flexible Filtering**: Send messages to all parents, or filter recipients by:
  - A specific academic year (e.g., 1st Year only).
  - A specific department (e.g., CSE only).
  - A combination of both (e.g., 1st Year CSE students).
- **CSV Data Management**: Parent contact information is managed through simple, easy-to-edit CSV files organized by year.
- **Broadcast Simulation**: The core logic for gathering recipients is fully functional, with the output printed to the terminal for testing before integrating a live SMS gateway.


## File Structure 📂
📁 college_broadcast_project/
├── 📁 data/
│   ├── 📄 1st_year_parents.csv
│   ├── 📄 2nd_year_parents.csv
│   ├── 📄 3rd_year_parents.csv
│   └── 📄 4th_year_parents.csv
│
├── 📁 templates/
│   ├── 📄 dashboard.html
│   └── 📄 login.html
│
├── 🐍 app.py
├── 🔑 .env
└── 📋 requirements.txt
