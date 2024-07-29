#!/bin/bash
if [ -z "$1" ]; then
    echo "No file path provided."
    exit 1
fi

vendor/bin/phpstan analyse $1
