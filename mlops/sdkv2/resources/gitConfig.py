# setup git on a workspace

from azure.ai.ml.entities import WorkspaceConnection
from azure.ai.ml.entities import PatTokenConfiguration
import os

# fetching secrets from env var to secure access, these secrets can be set outside or source code
git_pat = os.environ["GIT_PAT"]

credentials = PatTokenConfiguration(pat=git_pat)

ws_connection = WorkspaceConnection(
    name="<connection_name>", target="<git_url>", type="git", credentials=credentials
)

ml_client.connections.create_or_update(ws_connection)