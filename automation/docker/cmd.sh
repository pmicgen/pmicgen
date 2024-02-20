#!/bin/bash

mkdir .logs

jupyter notebook --no-browser \
    --NotebookApp.password='' \
    --KernelSpecManager.ensure_native_kernel=False \
    --NotebookApp.allow_origin='*' \
    --NotebookApp.ip='0.0.0.0' > .logs/jupyter.txt 2>&1 &

# Loop until the server is up
while true; do
    if jupyter server list | grep -q "http://"; then
        break
    else
        echo "Waiting for Jupyter server to start..."
        sleep 1
    fi
done

# Extract token without additional part
token=$(jupyter server list | grep "http://" | awk '{split($0, a, "="); split(a[2], b, " "); print b[1]}')
echo "The server is now running, access it from http://localhost:8888/?token=$token"
echo "Access or change your password with the token: $token"

sleep infinity