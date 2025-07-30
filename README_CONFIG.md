# Enhanced Configuration System

This project uses a flexible YAML-based configuration system that supports multiple environments and centralized configuration management. The system provides easy deployment across different environments while maintaining clean separation of concerns.

## 🏗️ Configuration Structure

```
config/
├── environments/
│   ├── base.yaml          # Base configuration shared across all environments
│   ├── development.yaml   # Development-specific overrides
│   └── production.yaml    # Production-specific overrides
└── config_manager.py      # Configuration management utilities
```

## 🔧 Configuration Components

### 1. Azure OpenAI Configuration
```yaml
azure_openai:
  api_version: "2025-01-01-preview"
  azure_deployment: "gpt-4o"
  model: "gpt-4o"
```

### 2. Agent Configurations
Each agent has its own configuration section with name and instructions:
```yaml
agents:
  servicenow:
    name: "ServiceNow Specialist"
    instructions: |
      You are a ServiceNow specialist agent. Your responsibilities include:
      - Querying ServiceNow for incident information, tickets, and system data
      - Providing detailed analysis of ServiceNow records
      - Extracting relevant information from ServiceNow responses
      - Formatting results in a clear, structured manner

      Always use the available ServiceNow tools to ensure you provide comprehensive and accurate information from ServiceNow.

  gti:
    name: "GTI Specialist"
    instructions: |
      You are a Google Threat Intelligence specialist agent. Your responsibilities include:
      - Querying GTI for threat actor information, indicators, and intelligence
      - Analyzing threat intelligence data and providing insights
      - Searching for specific threat actors, malware, or attack patterns
      - Providing detailed threat analysis and context

      Always use the available GTI tools to gather comprehensive threat intelligence information from GTI.

  opensearch:
    name: "OpenSearch Specialist"
    instructions: |
      You are an OpenSearch specialist agent. Your responsibilities include:
      - Querying OpenSearch for log data, metrics, and analytics
      - Searching through indexed documents and logs
      - Performing complex queries and aggregations
      - Analyzing search results and providing insights
      - Extracting relevant information from OpenSearch responses
      - Formatting results in a clear, structured manner

      Always use the available OpenSearch tools to ensure you provide comprehensive and accurate information from the search engine.

  guardrail:
    name: "Guardrail Check"
    instructions: |
      Check if the user prompt contains sensitive information that should NOT be processed.
      
      This is an INTERNAL application, so the following are ACCEPTABLE:
      - Names of employees or users (e.g., "coco liu", "john smith")
      - Internal system names, IP addresses, or URLs
      - ServiceNow ticket numbers, incident IDs
      - Internal project names or team names
      
      ONLY flag as sensitive if the prompt contains:
      - Passwords, API keys, tokens, or credentials
      - Private keys, SSH keys, or cryptographic material
      - Database connection strings with passwords
      - Authentication tokens or session cookies
      - Any other authentication/authorization secrets
      
      Be conservative - only flag if there are clear credentials or secrets present.
      Names and internal identifiers are fine for this internal application.

  orchestrator:
    name: "Orchestrator"
    instructions: |
      You are an orchestrator agent that determines which specialized agents should handle a user query.
      
      Analyze the user's request and determine if it requires:
      1. ServiceNow data (incidents, tickets, system information, etc.)
      2. Threat Intelligence data (threat actors, indicators, malware, etc.)
      3. OpenSearch data (logs, metrics, analytics, search results, etc.)
      4. Multiple services
      
      Consider keywords and context:
      - ServiceNow: incidents, tickets, cases, service desk, ITIL, etc.
      - GTI: threat actors, malware, indicators, APT, cyber threats, etc.
      - OpenSearch: logs, metrics, analytics, search, queries, aggregations, etc.
      
      IMPORTANT: You must respond with a JSON object in this exact format:
      {
          "servicenow": true/false,
          "gti": true/false,
          "opensearch": true/false,
          "reasoning": "Detailed explanation of why each service is needed or not needed"
      }
      
      Example responses:
      - For ServiceNow only: {"servicenow": true, "gti": false, "opensearch": false, "reasoning": "Query asks for incident information which is stored in ServiceNow"}
      - For GTI only: {"servicenow": false, "gti": true, "opensearch": false, "reasoning": "Query asks for threat intelligence about specific threat actors"}
      - For OpenSearch only: {"servicenow": false, "gti": false, "opensearch": true, "reasoning": "Query asks for log analysis or search results from OpenSearch"}
      - For multiple: {"servicenow": true, "gti": true, "opensearch": false, "reasoning": "Query asks for both incident data and threat intelligence information"}
      
      Always provide clear reasoning for your decision.

  visualization:
    name: "Visualization Agent"
    instructions: |
      You are a visualization expert. Given plaintext results from ServiceNow, Google Threat Intelligence, and/or OpenSearch, analyze the data and generate a suitable visualization for presentation.
      - Summarize the key findings in natural language.
      - Decide on the best visualization type (bar, pie, timeline, table, etc.) to visualize the key findings.
      - Provide Python code snippet to generate the visualization.
      - Respond ONLY with a valid JSON object matching this schema:
        {
          "summary": string,
          "visualization_type": string,
          "code_snippet": string
        }
      - Do NOT include any text, markdown, or explanation before or after the JSON.
      - Begin your response with '{' and end with '}'.
      - For code_snippet, provide Python/Markdown code to generate the visualization, or empty string if not needed.
      - If you cannot generate a visualization, return a JSON object with only a summary and an explanation why.
```

### 3. MCP Server Configurations
MCP servers are configured with their command and arguments for each service:
```yaml
mcp_servers:
  gti:
    name: "GTI Server"
    command: "/path/to/uv"
    args:
      - "--directory"
      - "/path/to/gti/server"
      - "run"
      - "--env-file"
      - "/path/to/.env"
      - "gti_mcp/server.py"

  servicenow:
    name: "ServiceNow Server"
    command: "/path/to/uv"
    args:
      - "--directory"
      - "/path/to/servicenow/server"
      - "run"
      - "--env-file"
      - "/path/to/.env"
      - "cli.py"

  opensearch:
    name: "OpenSearch Server"
    command: "/path/to/uv"
    args:
      - "--directory"
      - "/path/to/opensearch/server"
      - "run"
      - "--env-file"
      - "/path/to/.env"
      - "-m"
      - "mcp_server_opensearch"
```

## 🌍 Environment Management

### Loading Different Environments

```python
from config.config_manager import config_manager

# Create config manager
config_manager = ConfigManager()

# Load specific environment
config_manager.load_config("development")
config_manager.load_config("production")

# Use environment variable
import os
os.environ["ENV"] = "development"
config_manager.load_config()  # Uses ENV variable
```

### Environment-Specific Overrides

The system automatically merges base configuration with environment-specific overrides:

- **Base Configuration**: Common settings shared across all environments
- **Environment Overrides**: Environment-specific settings that override base config

### Environment Variable Setup

The system uses a two-tier environment variable approach:

1. **Base `.env` file** (in home directory):
   ```bash
   # Environment type
   ENV=development
   
   # Azure OpenAI Configuration
   AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   ```

2. **Environment-specific `.env.{environment}` files**:
   ```bash
   # Development environment (.env.development)
   AZURE_OPENAI_ENDPOINT=https://your-dev-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_dev_api_key
   
   # Production environment (.env.production)
   AZURE_OPENAI_ENDPOINT=https://your-prod-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your_prod_api_key
   ```

## 📖 Usage Examples

### Accessing Configuration Values

```python
# Get Azure OpenAI configuration
azure_config = config_manager.get("azure_openai")

# Get specific agent configuration
servicenow_config = config_manager.get("agents.servicenow")

# Get MCP server configuration
gti_server_config = config_manager.get("mcp_servers.gti")

# Use dot notation for nested values
model = config_manager.get("azure_openai.model")
deployment = config_manager.get("azure_openai.azure_deployment")
```

### Creating Agents with Configuration

```python
# Get agent config
agent_config = config_manager.get("agents.servicenow")

# Create agent
agent = Agent(
    name=agent_config["name"],
    instructions=agent_config["instructions"],
    model=azure_openai_model,
    mcp_servers=[mcp_server]
)
```

### Creating MCP Servers with Configuration

```python
# Get MCP server config
server_config = config_manager.get("mcp_servers.gti")

# Create MCP server
mcp_server = MCPServerStdio(
    name=server_config["name"],
    params={
        "command": server_config["command"],
        "args": server_config["args"]
    }
)
```

## 🚀 Environment Differences

### Development Environment
- Uses `gpt-4o-mini` for cost efficiency
- Debug mode enabled
- Development-specific paths and env files
- Detailed logging

### Production Environment
- Uses `gpt-4o` for full capabilities
- Debug mode disabled
- Production paths and env files
- Optimized logging

## 🔄 Adding New Environments

1. Create a new YAML file in `config/environments/`
2. Define environment-specific overrides
3. Create corresponding `.env.{environment}` file
4. Load the environment in your code

Example: `config/environments/staging.yaml`
```yaml
azure_openai:
  azure_deployment: "gpt-4o-mini"
  model: "gpt-4o-mini"

staging:
  debug: true
  log_level: "INFO"
```

Example: `~/.env.staging`
```bash
AZURE_OPENAI_ENDPOINT=https://your-staging-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your_staging_api_key
```

## 🛠️ Extending the Configuration

### Adding New Agent Types
1. Add agent configuration to `base.yaml`
2. Create factory function in your main script
3. Use `config_manager.get("agents.new_agent")` to access configuration

### Adding New MCP Servers
1. Add server configuration to `base.yaml`
2. Use `config_manager.get("mcp_servers.new_server")` in your code
3. Update the main workflow to include the new server

### Adding New Configuration Sections
1. Add section to `base.yaml`
2. Create helper methods in `ConfigManager` if needed
3. Access using `config_manager.get("section.key")`

## 🧪 Testing the Configuration

You can test the configuration system by running your main script with different environments:

```bash
# Test development environment
ENV=development python main.py

# Test production environment  
ENV=production python main.py

# Test staging environment
ENV=staging python main.py
```

This will demonstrate:
- Loading different environments
- Accessing configuration values
- Environment-specific settings
- Configuration merging
- MCP server initialization

## 🔒 Security Considerations

- **Sensitive Data**: Keep API keys and endpoints in environment variables
- **Configuration Files**: Don't commit sensitive data to configuration files
- **Environment Variables**: Use `.env` files for local development
- **Path Security**: Ensure MCP server paths are secure and accessible only to authorized users

## 📋 Configuration Best Practices

### 1. Environment Separation
- Keep development, staging, and production configurations separate
- Use environment variables for sensitive data
- Never commit API keys to version control

### 2. Configuration Validation
- Validate configuration on startup
- Provide clear error messages for missing or invalid configuration
- Use type hints and Pydantic models for configuration validation

### 3. Documentation
- Document all configuration options
- Provide examples for each environment
- Keep configuration documentation up to date

### 4. Deployment
- Use environment-specific configuration files
- Validate configuration before deployment
- Test configuration in staging environment first

The enhanced configuration system provides better organization, environment support, maintainability, and security for the MCP orchestrator project. 