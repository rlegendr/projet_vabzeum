#!/bin/bash
echo "export app"; export FLASK_APP=app
echo "export dev"; export FLASK_ENV=development
echo "flask python"; python3.9 -m flask run