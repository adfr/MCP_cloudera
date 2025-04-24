# Cloudera ML Model Control Protocol (MCP)

This MCP implements a Python-based integration with Cloudera Machine Learning, allowing Claude to interact with CML services programmatically.

## Features

1. **Upload Folders**: Upload entire folders to your CML project while preserving directory structure
2. **Create Jobs**: Create new CML jobs with customizable settings
3. **List Jobs**: View all jobs in your project with their current status
4. **Delete Jobs**: Remove individual jobs or all jobs in a project
5. **Get Project ID**: Retrieve project ID from a project name
6. **List Project Files**: View files and directories in your project
7. **Model Management**: Create, list, and manage ML models and deployments
8. **Experiment Tracking**: Log and manage ML experiments and runs
9. **Application Management**: Create, update, and manage CML applications

## Installation

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The MCP requires the following configuration:

1. **host**: Your CML instance URL (e.g., "https://ml-xxxx.cloudera.site")
2. **api_key**: Your API key for authentication
3. **project_id**: Your CML project ID (optional - you can now get it by project name)

You can provide this configuration in code when initializing the MCP, or use environment variables:

```bash
export CLOUDERA_ML_HOST="https://ml-xxxx.cloudera.site"
export CLOUDERA_ML_API_KEY="your-api-key"
# Optional: export CLOUDERA_ML_PROJECT_ID="your-project-id"
```

### URL Configuration Notes
- The host URL should not include duplicate "https://" prefixes
- Trailing slashes are automatically handled
- The MCP will automatically format URLs correctly

## Running the MCP Server

This MCP can be run as a server that allows Claude to interact with Cloudera ML.

### Set up the environment

Copy the example .env file and add your credentials:

```bash
cp .env.example .env
# Edit .env with your credentials
```

### Start the server

```bash
./server.py
```

The server uses the stdio transport by default, which allows it to connect directly to Claude.

### Usage with Claude Desktop

To use this server with the Claude Desktop app, add the following configuration to the "mcpServers" section of your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cloudera-ml-mcp-server": {
      "command": "python",
      "args": [
        "/path/to/MCP_cloudera/server.py"
      ],
      "env": {
        "CLOUDERA_ML_HOST": "https://ml-xxxx.cloudera.site",
        "CLOUDERA_ML_API_KEY": "your-api-key"
      }
    }
  }
}
```

Replace `/path/to` with your path to this repository and set the environment variables.

## Using in Your Own Python Code

You can also import and use the MCP in your own Python code:

```python
from MCP_cloudera.src import ClouderaMCP

# Initialize the MCP
config = {
    "host": "https://ml-xxxx.cloudera.site",
    "api_key": "your-api-key"
}
cloudera = ClouderaMCP(config)

# Get project ID by name
project_info = cloudera.get_project_id(project_name="my-project-name")
project_id = project_info["project_id"]
print(f"Project ID: {project_id}")

# List project files
files = cloudera.list_project_files(project_id=project_id)
print(files)

# Upload a folder
result = cloudera.upload_folder(
    folder_path="/path/to/local/folder",
    ignore_folders=["node_modules", ".git"]
)
```

## Command-line Testing

You can test the MCP functions from the command line using the provided script:

```bash
./run_mcp.py [--host HOST] [--api-key API_KEY] [--project-id PROJECT_ID] COMMAND [command options]
```

Where `COMMAND` is one of:
- `list_jobs` - List all jobs in the project
- `upload_folder` - Upload a folder to the project
- `create_job` - Create a new job
- `delete_job` - Delete a specific job
- `delete_all_jobs` - Delete all jobs in the project
- `get_project_id` - Get project ID from a project name (`--project-name` required)
- `list_project_files` - List files in a project
- `list_models` - List ML models in a project
- `list_model_deployments` - List model deployments
- `list_experiments` - List experiments in a project
- `list_job_runs` - List job runs

### Example: Listing Project Files

```bash
./run_mcp.py --host "https://ml-xxxx.cloudera.site" --api-key "your-api-key" list_project_files --project-id "your-project-id"
```

## Requirements

- Python 3.8+
- requests
- pathlib
- python-dotenv
- mcp[cli]

## License

MIT 