# 90 NORTH ASSIGNMENT
## TO SETUP THE ENVIRONMENT
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```
## END POINTS
- localhost:8000
- localhost:8000/chat
- localhost:8000/accounts/login
- localhost:8000/accounts/signup
- localhost:8000/accounts/logout
## ADMIN PANNEL FOR DATABASE
Create superuser for admin pannel
- python manage.py createsuperuser
- localhost:8000/admin