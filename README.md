# Medical Appointment Management System
A web-based system for patients to book and manage their medical appointments with doctors using Flask for the backend and React for the frontend.

## Features
Secure user authentication (patients & doctors).  
Patients can book, update, and cancel appointments.  
Doctors can manage their schedules and appointments.  
Real-time appointment validation (no duplicate bookings).

## Installation 
1) Clone the Repository
https://github.com/GiorgosK96/Medical_Appointment_App.git     
cd patient_app


3) Install Backend Dependencies       
cd backend       
pip install -r requirements.txt

4) Install Frontend Dependencies     
cd frontend    
npm install

5) Set Up Environment Variables      
Create a `.env` file in the backend directory with:    
SQLALCHEMY_DATABASE_URI=your_database_url   
JWT_SECRET_KEY=your_secret_key

6) Start the Application     
- Start the backend    
cd backend     
python api.py

- Start the frontend    
cd frontend    
npm start   
