#!/bin/bash

python scripts/fill_env.py

uvicorn app.app:app --host 0.0.0.0 --port 8080