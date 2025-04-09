# MCP SDK Versions Guide

This document provides an overview of the differences between MCP SDK implementations across versions and suggests user prompts to exercise different code paths.

## Version Implementations

### 00-advertise-tool

- **Basic Functionality**: Only advertises tools without actual implementation
- **Key Features**:
  - Tool advertisement structure
  - Basic JSON-RPC protocol implementation
  - No actual tool functionality

#### Testing Prompts

- This version only advertises tools without implementation, so no specific user prompts will trigger functionality.

### 01-invoke-time-tool

- **Basic Tool Implementation**: Adds actual functionality to the advertised tools
- **Key Features**:
  - Functional time tool with format parameter
  - Tool discovery and invocation
  - Result handling and display

### 02-llm-client

- **LLM Integration**: Adds language model capabilities
- **Key Features**:
  - OpenAI API integration
  - Tool conversion to OpenAI function format
  - LLM-driven tool selection
  - User prompt handling

#### Testing Prompts

- "What time is it?"
- "Tell me the current time."
- "What's the weather like?" (should not work, but tests LLM's understanding of available tools)
- "Can you help me with my homework?" (tests LLM's response when no relevant tools are available)
- "What time is it in 24-hour format?" (tests format parameter)
- "Show me the time in HH:MM format." (tests custom format)

### 03-context-memory

- **Context and Memory**: Adds persistent memory and context
- **Key Features**:
  - Timezone support instead of format strings
  - Memory system for user preferences
  - City-to-timezone knowledge base
  - Parameter completion from memory
  - System messages to guide LLM behavior

#### Testing Prompts

- "What time is it?" (uses default timezone from memory)
- "What time is it in Tokyo?" (tests city-to-timezone mapping)
- "What's the time in PST?" (tests direct timezone specification)
- "What time is it in New York?" (tests another city mapping)
- "What time is it in InvalidCity?" (tests fallback to default timezone)

### 04-multiple-tools

- **Multiple Tool Support**: Adds ability to work with multiple tools
- **Key Features**:
  - Weather tool in addition to time tool
  - Multiple tool advertisement
  - Handling multiple tool calls from a single LLM response

#### Testing Prompts

- "What time is it?" (exercises time tool)
- "What's the weather in Seattle?" (exercises weather tool)
- "What time is it in Tokyo and what's the weather in London?" (exercises multiple tool calls)
- "Tell me the time and weather in New York." (exercises both tools with a single city)

### 05-agent-parallel

- **Parallel Processing**: Adds concurrent tool execution
- **Key Features**:
  - Parallel processing of multiple tool calls
  - Asynchronous task collection and execution
  - Performance improvements for multiple tool calls

#### Testing Prompts

- "What's the time in Tokyo, London, and New York?" (exercises parallel processing of multiple time tool calls)
- "What's the weather in Seattle, Miami, and Berlin?" (exercises parallel processing of multiple weather tool calls)
- "Tell me the time and weather in Tokyo, London, and New York." (exercises parallel processing of mixed tool calls)

### 06-error-handling

- **Error Handling**: Focuses on error handling patterns and techniques
- **Key Features**:
  - Error tool that intentionally fails
  - Error handling patterns
  - Error reporting and recovery

#### Automated Prompt

- "Try to get an error." (exercises the error tool)
- "Get an error with a custom message." (tests error handling with custom parameters)
- "Call a non-existent tool." (tests error handling for invalid tools)
