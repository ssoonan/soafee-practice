#!/bin/bash
# Source the setup.bash file to set up the environment
if [ -f /fastdds_python_ws/install/setup.bash ]; then
    echo "Sourcing /fastdds_python_ws/install/setup.bash"
    source /fastdds_python_ws/install/setup.bash
else
    echo "Error: /fastdds_python_ws/install/setup.bash not found"
    exit 1
fi

# Execute the command passed from ENTRYPOINT
echo "Executing command: $@"
exec "$@"
