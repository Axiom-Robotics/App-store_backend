#!/usr/bin/env python3
def get_shapes():
    return {
        "circle": {
            "action": "twist_continuous",
            "params": {
                "linear": {
                    "x": 1.0,  # Forward velocity (equivalent to radius)
                    "y": 0.0,
                    "z": 0.0
                },
                "angular": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 1.0   # Angular velocity (1 rad/sec)
                },
                "duration": 6.28  # Time for one complete circle (2π seconds)
            }
        }
    }
