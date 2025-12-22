command = '/var/www/artisan/venv/bin/gunicorn'
pythonpath = '/var/www/artisan'
bind = 'unix:/var/www/artisan/artisan.sock'
workers = 3
