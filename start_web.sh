#!/bin/bash
uwsgi --http :5000 --wsgi-file sar2python.py --callable app --processes 4 --threads 2
