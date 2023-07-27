#!/bin/sh

export $(grep -v '^#' .env | xargs)

python app.py