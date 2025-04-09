#!/usr/bin/env python3
"""
MCP Examples Runner

This script allows you to run all MCP examples easily.
It provides information about each exercise and any required user input.
It also generates the necessary API keys based on student name and password.
"""

import os
import sys
import subprocess
import time
import base64
import argparse
import platform
from pathlib import Path

# Define the exercises and their details
EXERCISES = [
    {
        "id": "00",
        "name": "advertise-tool",
        "description": "Demonstrates how MCP servers advertise tools to clients",
        "user_input": False,
        "notes": "Shows both raw JSON-RPC messages and high-level SDK implementation"
    },
    {
        "id": "01",
        "name": "invoke-time-tool",
        "description": "Shows how to invoke a simple time tool",
        "user_input": False,
        "notes": "Demonstrates basic tool invocation"
    },
    {
        "id": "02",
        "name": "llm-client",
        "description": "Demonstrates how an LLM can decide whether to call MCP tools",
        "user_input": True,
        "notes": "Requires OpenAI API key in .env file. Try asking 'What time is it?' or 'Can you tell me the current time?' to trigger tool use. Try 'What time is it in 24-hour format?' to see tool parameters. Try 'Tell me a joke' or 'What is the capital of France?' to see direct LLM response."
    },
    {
        "id": "03",
        "name": "context-memory",
        "description": "Shows how to maintain context between tool calls",
        "user_input": True,
        "notes": "Demonstrates stateful conversations with tools. Try asking 'What is the time?' to see memory in action (automatically uses America/New_York timezone). Try 'What is the time in San Francisco?' to see city name mapping. Try 'What time is it in Chicago?' for another city example. Try 'What's the current time in UTC+2?' to see explicit timezone handling."
    },
    {
        "id": "04",
        "name": "multiple-tools",
        "description": "Demonstrates using multiple tools in a single server",
        "user_input": True,
        "notes": "Shows how to organize and manage multiple tools. Try asking 'What is the time in Tokyo?' or 'Tell me the current time in London' to use the time tool. Try asking 'What is the weather in Tokyo?' or 'How's the weather in New York?' to use the weather tool."
    },
    {
        "id": "05",
        "name": "agent-parallel",
        "description": "Shows how to run multiple agents in parallel",
        "user_input": True,
        "notes": "Demonstrates parallel execution of MCP agents"
    },
    {
        "id": "06",
        "name": "error-handling",
        "description": "Demonstrates error handling with MCP tools",
        "user_input": False,
        "notes": "Shows how errors can be detected by MCP clients"
    }
]

def is_windows():
    """Determine if the current platform is Windows."""
    return platform.system() == 'Windows'

def get_script_ext():
    """Get the appropriate script extension for the current platform."""
    return '.ps1' if is_windows() else '.sh'

def get_script_command(script_path):
    """Get the appropriate command to execute a script on the current platform."""
    if is_windows():
        return ["powershell.exe", "-ExecutionPolicy", "Bypass", "-File", script_path]
    else:
        return ["bash", script_path]

def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f" {text}")
    print("=" * 80)

def generate_api_key(student_name, password):
    """Generate an API key using base64 encoding of student_name:password."""
    auth_string = f"{student_name}:{password}"
    return base64.b64encode(auth_string.encode()).decode()

def print_exercise_list():
    """Print a list of all available exercises."""
    print_header("Available MCP Exercises")
    
    for ex in EXERCISES:
        print(f"{ex['id']}: {ex['name']} - {ex['description']}")
        if ex['user_input']:
            print("   * Requires user input")
        print(f"   * {ex['notes']}")
    
    print("\nUsage:")
    print("  python run_exercises.py -n NAME -p PASSWORD [-e EXERCISE] [-i IMPLEMENTATION]")
    print("  - NAME: Your name (used for API key generation)")
    print("  - PASSWORD: 4-digit password (used for API key generation)")
    print("  - EXERCISE: 00-06 or 'all' (optional, if not provided will list exercises)")
    print("  - IMPLEMENTATION: 'websocket' (default) or 'sdk' (optional)")
    print("\nExamples:")
    print("  python run_exercises.py -n steve72 -p 1234                  # List available exercises")
    print("  python run_exercises.py -n steve72 -p 1234 -e 02            # Run exercise 02 with WebSocket implementation")
    print("  python run_exercises.py -n steve72 -p 1234 -e 03 -i sdk     # Run exercise 03 with SDK implementation")
    print("  python run_exercises.py --name steve72 --password 1234 --exercise all  # Run all exercises")
    
    if is_windows():
        print("\nNote: For Windows users, script execution will be handled with PowerShell automatically.")

def create_env_file(exercise_dir, api_key):
    """Create or update .env file with the generated API key."""
    env_path = os.path.join(exercise_dir, ".env")
    
    # Create the .env file with the required configuration
    with open(env_path, "w") as f:
        f.write(f"OPENAI_API_KEY={api_key}\n")
        f.write("OPENAI_BASE_URL=http://aitools.cs.vt.edu:7860/openai/v1\n")
        f.write("OPENAI_MODEL=gpt-4o\n")
    
    print(f"Regenerated .env file at {env_path}")
    return True

def check_powershell_available():
    """Check if PowerShell is available on Windows systems."""
    if not is_windows():
        return True  # Not relevant for non-Windows systems
    
    try:
        result = subprocess.run(
            ["powershell.exe", "-Command", "echo 'PowerShell is available'"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_docker_available():
    """Check if Docker is available on the system."""
    try:
        result = subprocess.run(
            ["docker", "--version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def run_exercise(exercise_id, implementation="websocket", api_key=None):
    """Run a specific exercise with the specified implementation."""
    # Find the exercise
    exercise = next((ex for ex in EXERCISES if ex["id"] == exercise_id), None)
    if not exercise:
        print(f"Error: Exercise {exercise_id} not found")
        return False
    
    exercise_dir = f"{exercise_id}-{exercise['name']}"
    
    print_header(f"Running Exercise {exercise_id}: {exercise['name']}")
    print(f"Description: {exercise['description']}")
    print(f"Implementation: {implementation}")
        
    # Check if PowerShell is available on Windows
    if is_windows() and not check_powershell_available():
        print("\nError: PowerShell is not available on your system.")
        print("Please ensure PowerShell is installed and accessible in your PATH.")
        return False
    
    # Check if Docker is available
    if not check_docker_available():
        print("\nError: Docker is not available on your system.")
        print("Please install Docker and make sure it's running before continuing.")
        return False
    
    # Always regenerate .env files for all exercises
    print("\nRegenerating environment files for this exercise...")
    create_env_file(exercise_dir, api_key)
    
    # Change to the exercise directory
    original_dir = os.getcwd()
    try:
        os.chdir(exercise_dir)
        print(f"Changed to directory: {os.getcwd()}")
        
        # Build the Docker image
        script_ext = get_script_ext()
        build_script = f"./docker-build{script_ext}"
        if not os.path.exists(build_script):
            print(f"Error: Build script not found at {build_script}")
            print("Checking for alternative scripts...")
            
            # Try to find alternative scripts
            run_script = f"./run{script_ext}"
            if os.path.exists(run_script):
                print(f"Found {run_script} script. Using it instead.")
                env = os.environ.copy()
                env["IMPLEMENTATION"] = implementation
                cmd = get_script_command(run_script)
                subprocess.run(cmd, env=env, check=True)
                print(f"\nExercise {exercise_id} completed using {run_script}")
                return True
            else:
                print("No alternative scripts found.")
                return False
        
        print("\nBuilding Docker image...")
        cmd = get_script_command(build_script)
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            if is_windows():
                print(f"\nError running PowerShell script: {e}")
                print("This might be due to PowerShell execution policy restrictions.")
                print("The script attempted to bypass this with -ExecutionPolicy Bypass, but it may not have worked.")
                print("You can try running PowerShell as Administrator and executing:")
                print("Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned")
            else:
                print(f"\nError running bash script: {e}")
                print("This might be due to permission issues. Try running:")
                print(f"chmod +x {build_script}")
            return False

    
        # Run the Docker container with the appropriate implementation
        # Always use the docker-run script, the implementation is controlled by the environment variable
        run_script = f"./docker-run{script_ext}"
        
        if not os.path.exists(run_script):
            print(f"Error: Run script not found at {run_script}")
            return False
        
        # Set the implementation environment variable
        env = os.environ.copy()
        env["IMPLEMENTATION"] = implementation
        
        # Run the exercise
        print(f"\nStarting exercise with {implementation} implementation...")
        print(f"Running: IMPLEMENTATION={implementation} {run_script}")
        if exercise['user_input']:
            print(f"\nNOTE: This exercise requires user input. {exercise['notes']}")

        cmd = get_script_command(run_script)
        try:
            process = subprocess.Popen(cmd, env=env)
            process.wait()
        except subprocess.SubprocessError as e:
            if is_windows():
                print(f"\nError running PowerShell script: {e}")
                print("This might be due to PowerShell execution policy restrictions.")
                print("The script attempted to bypass this with -ExecutionPolicy Bypass, but it may not have worked.")
                print("You can try running PowerShell as Administrator and executing:")
                print("Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned")
            else:
                print(f"\nError running bash script: {e}")
                print("This might be due to permission issues. Try running:")
                print(f"chmod +x {run_script}")
            return False
        
        print(f"\nExercise {exercise_id} completed")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error running script: {e}")
        return False
    except Exception as e:
        print(f"Error running exercise: {e}")
        return False
    finally:
        # Always return to the original directory
        os.chdir(original_dir)

def main():
    """Main function to parse arguments and run exercises."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run MCP exercises with student credentials")
    parser.add_argument("-n", "--name", required=True, 
                        help="Student name (used for API key generation)")
    parser.add_argument("-p", "--password", required=True,
                        help="4-digit password (used for API key generation)")
    parser.add_argument("-e", "--exercise", default=None, 
                        help="Exercise ID (00-06 or 'all'). If not provided, list available exercises.")
    parser.add_argument("-i", "--implementation", default="websocket",
                        choices=["websocket", "sdk"], 
                        help="Implementation to use (websocket or sdk)")
    
    args = parser.parse_args()
    
    # Validate password is 4 digits
    if not (args.password.isdigit() and len(args.password) == 4):
        print("Error: Password must be exactly 4 digits")
        return
    
    # Generate API key
    api_key = generate_api_key(args.name, args.password)
    print(f"Generated API key for student: {args.name}")
    
    # If no exercise_id provided, just list exercises
    if args.exercise is None:
        print_exercise_list()
        return
    
    exercise_id = args.exercise.lower()
    implementation = args.implementation
    
    if exercise_id == "all":
        print_header("Running All MCP Exercises")
        
        success_count = 0
        for ex in EXERCISES:
            print("\n")
            if run_exercise(ex["id"], implementation, api_key):
                success_count += 1
            
            # Add a small delay between exercises
            time.sleep(2)
        
        print_header(f"Completed {success_count}/{len(EXERCISES)} exercises")
    else:
        # Ensure the exercise ID is two digits
        if len(exercise_id) == 1:
            exercise_id = "0" + exercise_id
        
        run_exercise(exercise_id, implementation, api_key)

if __name__ == "__main__":
    main()
