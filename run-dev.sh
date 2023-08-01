#!/bin/sh

export $(grep -v '^#' .env | xargs)

echo "DEV_USERNAME=${DEV_USERNAME}"

python app.py