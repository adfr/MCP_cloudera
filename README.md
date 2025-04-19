# Cloudera ML Model Control Protocol (MCP)

This MCP implements a Python-based integration with Cloudera Machine Learning, allowing Claude to interact with CML services programmatically.

## Features

1. **Upload Folders**: Upload entire folders to your CML project while preserving directory structure
2. **Create Jobs**: Create new CML jobs with customizable settings
3. **List Jobs**: View all jobs in your project with their current status
4. **Delete Jobs**: Remove individual jobs or all jobs in a project
5. **Get Project ID**: Retrieve project ID from a project name

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

If you don't know your project ID, you can use the `get_project_id` function to retrieve it by project name.

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

# Use MCP functions with the retrieved project ID
jobs = cloudera.list_jobs()
print(jobs)

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

### Example: Getting Project ID by Name

```bash
./run_mcp.py --host "https://ml-xxxx.cloudera.site" --api-key "your-api-key" get_project_id --project-name "my-project-name"
```

## Requirements

- Python 3.8+
- requests
- pathlib
- python-dotenv
- mcp[cli]

## License

MIT 