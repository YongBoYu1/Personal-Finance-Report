#!/bin/sh

# Check if the 'data' directory exists
if [ ! -d "./data" ]; then
  # Create the 'data' directory
  mkdir ./data
  echo "Directory 'data' created."
else
  echo "Directory 'data' already exists."
fi