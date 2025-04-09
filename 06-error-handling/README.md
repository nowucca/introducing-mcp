# MCP Agent Planning Example

This example demonstrates how to use an LLM to generate a plan of tool calls based on a user query. In this approach, the LLM analyzes the user's request and decides which tools to call and with what parameters.

## What This Example Does

When you run this example:
1. The client connects to an MCP server
2. The client requests the list of available tools
3. You'll be prompted to enter a question or request
4. The client sends your query to the LLM along with information about available tools
5. The LLM generates a "plan" consisting of tool calls to execute
6. The client executes these tool calls in parallel
7. Results are collected and presented to you

## Key Concepts

- **LLM-based Planning**: Using an LLM to decide which tools to call based on user input
- **Dynamic Tool Selection**: Allowing the LLM to choose tools and parameters based on context
- **Parallel Execution**: Running multiple tool calls concurrently for efficiency
- **Plan Generation**: Creating a structured plan of actions from natural language

## Learning Objectives

- Understand how LLMs can generate plans of tool calls
- Learn how to convert LLM outputs into executable tool calls
- See how to execute a dynamically generated plan
- Explore different approaches to plan formulation in agent systems

## Implementation Details

### How It Works

1. The client connects to the MCP server and retrieves the list of available tools
2. The client sends a query to the OpenAI API along with tool definitions
3. The LLM decides which tools to call based on the query
4. The client executes the tool calls concurrently
5. Results are collected and displayed

### Code Structure

- `client.py`: Connects to the MCP server, sends queries to the LLM, and executes tool calls
- `server.py`: Implements the MCP server with time and weather tools

## Alternative Approaches to Plan Formulation

While this example uses the LLM to generate a plan of tool calls, there are several other approaches to formulating plans in agent systems:

### 1. Rule-based Planning

Instead of using an LLM to decide which tools to call, you could implement a rule-based system that maps specific patterns in user queries to predefined tool calls.

**Pros:**
- Predictable behavior
- No dependency on external LLM APIs
- Potentially faster execution

**Cons:**
- Less flexible
- Requires manual rule creation
- Difficult to handle complex or ambiguous queries

### 2. Hybrid Approach

Combine rule-based planning with LLM planning. Use rules for common, well-defined queries and fall back to LLM planning for more complex or ambiguous requests.

**Pros:**
- Balances predictability with flexibility
- Can reduce costs by minimizing LLM API calls
- Potentially faster for common queries

**Cons:**
- More complex implementation
- Requires maintaining two systems

### 3. Multi-step Planning

Instead of generating the entire plan at once, the LLM could generate one step at a time, observe the result, and then decide on the next step.

**Pros:**
- Can adapt based on intermediate results
- Potentially more accurate for complex tasks
- Better handling of errors or unexpected results

**Cons:**
- More LLM API calls
- Slower execution
- More complex implementation

### 4. User-guided Planning

Present the LLM-generated plan to the user for approval or modification before execution.

**Pros:**
- Greater user control
- Opportunity to correct misunderstandings
- Educational for users

**Cons:**
- Requires more user interaction
- Slower execution
- May frustrate users who want immediate results

### 5. Template-based Planning

Use predefined plan templates for common query types, with the LLM filling in the specifics.

**Pros:**
- More consistent behavior
- Reduced LLM token usage
- Potentially faster

**Cons:**
- Less flexible
- Requires creating and maintaining templates
- May not handle novel requests well
## Running the Example

### Prerequisites: OpenAI API Key

Before running this example, set up your OpenAI API key in the `.env` file:

```
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o
```

> **Note**: If you use the `run_exercises.py` script to run this example, the `.env` file will be created for you automatically.

### Docker Support

This example includes Docker support with helpful scripts:

#### Linux/macOS
- `docker-build.sh`: Builds the Docker image
- `docker-run.sh`: Runs the container with WebSocket implementation
- `docker-clean.sh`: Cleans up containers and images
- `docker-stop.sh`: Stops running containers
- `sdk-run.sh`: Runs the container with SDK implementation

#### Windows
- `docker-build.ps1`: Builds the Docker image
- `docker-run.ps1`: Runs the container with WebSocket implementation
- `docker-clean.ps1`: Cleans up containers and images
- `docker-stop.ps1`: Stops running containers
- `sdk-run.ps1`: Runs the container with SDK implementation

### Running Locally

```bash
# Run the server
./run_server.sh

# In another terminal, run the client
./run_client.sh
```

### Internal Scripts (For Docker Use Only)

The `run.sh` script is used internally by the Docker container and is not intended to be run directly:

```bash
# This is used internally by Docker - DO NOT RUN DIRECTLY
./run.sh
```

It handles:
1. Starting the server in the background
2. Waiting for initialization
3. Running the appropriate client
4. Cleaning up processes when done

> **Important**: Students should always use the Docker scripts (`docker-build.sh`/`docker-run.sh` or `docker-build.ps1`/`docker-run.ps1`) to run the examples, not the internal scripts.

## Conclusion

The approach used in this example—having the LLM generate a complete plan upfront—is just one of many possible approaches to agent planning. The best approach depends on your specific requirements, including factors like predictability, flexibility, cost, and user experience.

By understanding these different approaches, you can design an agent system that best meets your needs.
