redis server 

redis-server

mail hog 

~/go/bin/MailHog

backend terminal 

python3 main.py 

worker 

celery -A main.celery_app worker --loglevel=INFO

beat

celery -A main.celery_app beat --loglevel=INFO





Create virtual env 

python3 -m venv wsl

. wsl/bin/activate

pip install -r wslrequirements.txt





