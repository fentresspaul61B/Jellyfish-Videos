import time
from datetime import datetime
from functools import wraps
from typing import Callable
from icecream import ic
import inspect
import logging


def log_function_call(func: Callable) -> Callable:

    def wrapper(*args, **kwargs):
        # Get function name
        func_name = func.__name__

        # Get input arguments and their types
        input_args = args
        input_kwargs = kwargs
        input_types = [type(arg).__name__ for arg in args] + \
            [f"{key}: {type(value).__name__}" for key, value in kwargs.items()]

        # Timestamp of when the function was called
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Start time
        start_time = time.time()

        # Execute the function and get the result
        result = func(*args, **kwargs)

        # End time
        end_time = time.time()
        duration = end_time - start_time

        # Get output type
        output_type = type(result).__name__

        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        file_path = outer_frames[1].filename

        # ic the collected information
        ic()
        print(f"Function Name: {func_name}")
        print(f"Source File: {file_path}")
        print(f"Call Time: {timestamp}")
        print(timestamp)
        print("Input Arguments:")
        print(input_args)
        print("Input Keyword Arugments:")
        print(input_kwargs)
        print("Input Data Types:")
        print(input_types)
        print("Output Data Types:")
        print(output_type)
        print(f"Execution Time: {duration}")
        print()

        return result

    return wrapper
