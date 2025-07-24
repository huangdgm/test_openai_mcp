# Enhanced Configuration System

This project now uses a flexible YAML-based configuration system that supports multiple environments and centralized configuration management.

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
Each agent has its own configuration section:
```yaml
agents:
  servicenow:
    name: "ServiceNow Specialist"
    instructions: "Agent instructions..."
  
  gti:
    name: "GTI Specialist"
    instructions: "Agent instructions..."
```

### 3. MCP Server Configurations
MCP servers are configured with their command and arguments:
```yaml
mcp_servers:
  gti:
    name: "GTI Server"
    command: "/path/to/uv"
    args:
      - "--directory"
      - "/path/to/gti/server"
      - "run"
      - "gti_mcp/server.py"
```

## 🌍 Environment Management

### Loading Different Environments

```python
from config.config_manager import ConfigManager

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
3. Load the environment in your code

Example: `config/environments/staging.yaml`
```yaml
azure_openai:
  azure_deployment: "gpt-4o-mini"
  model: "gpt-4o-mini"

staging:
  debug: true
  log_level: "INFO"
```

## 🛠️ Extending the Configuration

### Adding New Agent Types
1. Add agent configuration to `base.yaml`
2. Create factory function in your main script
3. Use `config_manager.get_agent_config("new_agent")`

### Adding New MCP Servers
1. Add server configuration to `base.yaml`
2. Use `config_manager.get_mcp_server_config("new_server")` in your code

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
```

This will demonstrate:
- Loading different environments
- Accessing configuration values
- Environment-specific settings
- Configuration merging

## 🔒 Security Considerations

- **Sensitive Data**: Keep API keys and endpoints in environment variables
- **Configuration Files**: Don't commit sensitive data to configuration files
- **Environment Variables**: Use `.env` files for local development

The new system provides better organization, environment support, and maintainability. 