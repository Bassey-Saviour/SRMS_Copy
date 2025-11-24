# Student-Result-Management-System

A system for management results of students in a school, for COSC 333 / ITGY 401

# Student Result Management System (SR MS)

## Project Structure

student_result_management_system/
│
├── public/  
│ ├── index.html
│ ├── student.html
│ ├── lecturer.html
│ ├── css/
│ │ └── style.css
│ └── images/
│ └── placeholder.txt
│
├── cgi-bin/  
│ ├── student_results.py
│ ├── upload_results.py
│ ├── db_config.py
│ └── utils.py
│
├── database/
│ ├── schema.sql
│ ├── sample_data.sql
│ └── erd.png
│
└── README.md

## How to run locally

1. Install Python 3
2. Install MySQL
3. Create the database using schema.sql
4. Start CGI server:
   ```bash
   python3 -m http.server --cgi 8000
   ```
