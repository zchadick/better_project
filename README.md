Deployment:

On AWS:
-install both gunicorn and supervisor
	'pip install gunicorn'
	'pip install supervisor'
-install dependencies (only needs to be done once)
	'pip install -r requirements.txt' 
-start supervisor
	'sudo supervisord -c simple.conf'

On localhost:
-add a virtual environment
	'venv venv' or
	'virtualvenv venv' based on system
-open virtual environment
	'source venv/bin/activate'
-install dependencies (only needs to be done once)
	'pip install -r requirements.txt'
-start server
	'python server.py'