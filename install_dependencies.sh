#!/bin/bash
set -e

echo "Installing dependencies..."
mkdir -p dependencies_layer/python
echo "pymysql" > dependencies_layer/python/requirements.txt
pip install -r dependencies_layer/python/requirements.txt -t dependencies_layer/python
echo "Dependencies installed successfully."
