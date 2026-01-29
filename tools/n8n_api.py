#!/usr/bin/env python3
"""
Tool: n8n API Client
Purpose: Create, manage, and execute n8n workflows via REST API

Usage:
    python tools/n8n_api.py --action list
    python tools/n8n_api.py --action get --workflow-id "abc123"
    python tools/n8n_api.py --action create --workflow-file "workflow.json"
    python tools/n8n_api.py --action activate --workflow-id "abc123"
    python tools/n8n_api.py --action execute --workflow-id "abc123" --data '{"key": "value"}'

Environment Variables Required:
    - N8N_API_URL: n8n instance URL (e.g., https://seme.app.n8n.cloud)
    - N8N_API_KEY: API key for authentication
"""

import os
import json
import argparse
from pathlib import Path
from typing import Optional
import urllib.error
import urllib.parse
import urllib.request

try:
    import httpx  # type: ignore
    _HTTPX_AVAILABLE = True
except ModuleNotFoundError:
    httpx = None  # type: ignore
    _HTTPX_AVAILABLE = False

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs) -> bool:  # type: ignore
        return False

load_dotenv()


class HttpRequestError(Exception):
    def __init__(self, status_code: int, message: str, response_text: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


def _request_json(
    method: str,
    url: str,
    headers: dict,
    *,
    params: Optional[dict] = None,
    json_body: Optional[dict] = None,
    timeout: float = 30.0,
    allow_text: bool = False,
) -> dict:
    if _HTTPX_AVAILABLE:
        try:
            response = httpx.request(  # type: ignore
                method,
                url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=timeout,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:  # type: ignore
            raise HttpRequestError(e.response.status_code, str(e), e.response.text) from e
        except httpx.RequestError as e:  # type: ignore
            raise HttpRequestError(0, str(e), "") from e

        try:
            return response.json()
        except json.JSONDecodeError:
            if allow_text:
                return {"status": "success", "response": response.text}
            raise

    if params:
        query = urllib.parse.urlencode(params, doseq=True)
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{query}"

    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        headers = dict(headers)
        headers.setdefault("Content-Type", "application/json")

    request = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode()
    except urllib.error.HTTPError as e:
        response_text = ""
        try:
            response_text = e.read().decode()
        except Exception:
            response_text = ""
        raise HttpRequestError(e.code, f"HTTP {e.code}", response_text) from e
    except urllib.error.URLError as e:
        raise HttpRequestError(0, str(e), "") from e

    if allow_text:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"status": "success", "response": text}

    return json.loads(text)


def _is_placeholder(value: str) -> bool:
    if not value:
        return True
    lowered = value.lower()
    return "your-instance" in lowered or "your-n8n-api-key" in lowered


def _load_from_mcp() -> tuple[str, str]:
    mcp_path = Path(__file__).resolve().parents[1] / ".mcp.json"
    if not mcp_path.exists():
        return "", ""
    try:
        config = json.loads(mcp_path.read_text())
    except json.JSONDecodeError:
        return "", ""
    servers = config.get("mcpServers", {})
    n8n_cfg = servers.get("n8n-mcp", {})
    env = n8n_cfg.get("env", {})
    return env.get("N8N_API_URL", ""), env.get("N8N_API_KEY", "")


N8N_API_URL = os.getenv("N8N_API_URL", "").rstrip("/")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

if _is_placeholder(N8N_API_URL) or _is_placeholder(N8N_API_KEY):
    mcp_url, mcp_key = _load_from_mcp()
    if mcp_url:
        N8N_API_URL = mcp_url.rstrip("/")
    if mcp_key:
        N8N_API_KEY = mcp_key


def get_headers() -> dict:
    """Return headers for n8n API requests."""
    return {
        "X-N8N-API-KEY": N8N_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def list_workflows(active_only: bool = False) -> dict:
    """
    List all workflows.

    Args:
        active_only: If True, return only active workflows

    Returns:
        dict: API response with workflow list
    """
    params = {"active": "true"} if active_only else {}
    return _request_json(
        "GET",
        f"{N8N_API_URL}/api/v1/workflows",
        get_headers(),
        params=params,
        timeout=30.0,
    )


def get_workflow(workflow_id: str) -> dict:
    """
    Get a specific workflow by ID.

    Args:
        workflow_id: The workflow ID

    Returns:
        dict: Workflow details
    """
    return _request_json(
        "GET",
        f"{N8N_API_URL}/api/v1/workflows/{workflow_id}",
        get_headers(),
        timeout=30.0,
    )


def create_workflow(workflow_data: dict) -> dict:
    """
    Create a new workflow.

    Args:
        workflow_data: Workflow JSON object with name, nodes, connections, settings

    Returns:
        dict: Created workflow with ID
    """
    return _request_json(
        "POST",
        f"{N8N_API_URL}/api/v1/workflows",
        get_headers(),
        json_body=workflow_data,
        timeout=30.0,
    )


def update_workflow(workflow_id: str, workflow_data: dict) -> dict:
    """
    Update an existing workflow.

    Args:
        workflow_id: The workflow ID
        workflow_data: Updated workflow JSON

    Returns:
        dict: Updated workflow
    """
    return _request_json(
        "PUT",
        f"{N8N_API_URL}/api/v1/workflows/{workflow_id}",
        get_headers(),
        json_body=workflow_data,
        timeout=30.0,
    )


def delete_workflow(workflow_id: str) -> dict:
    """
    Delete a workflow.

    Args:
        workflow_id: The workflow ID

    Returns:
        dict: Deletion confirmation
    """
    _request_json(
        "DELETE",
        f"{N8N_API_URL}/api/v1/workflows/{workflow_id}",
        get_headers(),
        timeout=30.0,
    )
    return {"status": "deleted", "workflow_id": workflow_id}


def activate_workflow(workflow_id: str) -> dict:
    """
    Activate a workflow.

    Args:
        workflow_id: The workflow ID

    Returns:
        dict: Activation result
    """
    return _request_json(
        "POST",
        f"{N8N_API_URL}/api/v1/workflows/{workflow_id}/activate",
        get_headers(),
        timeout=30.0,
    )


def deactivate_workflow(workflow_id: str) -> dict:
    """
    Deactivate a workflow.

    Args:
        workflow_id: The workflow ID

    Returns:
        dict: Deactivation result
    """
    return _request_json(
        "POST",
        f"{N8N_API_URL}/api/v1/workflows/{workflow_id}/deactivate",
        get_headers(),
        timeout=30.0,
    )


def execute_workflow(workflow_id: str, data: Optional[dict] = None) -> dict:
    """
    Execute a workflow with optional input data.

    Args:
        workflow_id: The workflow ID
        data: Optional input data for the workflow

    Returns:
        dict: Execution result
    """
    body = data or {}
    return _request_json(
        "POST",
        f"{N8N_API_URL}/api/v1/workflows/{workflow_id}/execute",
        get_headers(),
        json_body=body,
        timeout=120.0,
    )


def trigger_webhook(webhook_path: str, data: dict, method: str = "POST") -> dict:
    """
    Trigger a webhook workflow.

    Args:
        webhook_path: The webhook path (e.g., "my-webhook")
        data: Data to send to the webhook
        method: HTTP method (POST, GET)

    Returns:
        dict: Webhook response
    """
    url = f"{N8N_API_URL}/webhook/{webhook_path}"

    if method.upper() == "GET":
        return _request_json(
            "GET",
            url,
            get_headers(),
            params=data,
            timeout=60.0,
            allow_text=True,
        )
    return _request_json(
        "POST",
        url,
        get_headers(),
        json_body=data,
        timeout=60.0,
        allow_text=True,
    )


def list_executions(workflow_id: Optional[str] = None, status: Optional[str] = None) -> dict:
    """
    List workflow executions.

    Args:
        workflow_id: Filter by workflow ID
        status: Filter by status (error, success, waiting)

    Returns:
        dict: List of executions
    """
    params = {}
    if workflow_id:
        params["workflowId"] = workflow_id
    if status:
        params["status"] = status

    return _request_json(
        "GET",
        f"{N8N_API_URL}/api/v1/executions",
        get_headers(),
        params=params,
        timeout=30.0,
    )


def health_check() -> dict:
    """
    Perform a lightweight API check to verify connectivity and auth.

    Returns:
        dict: Health status with workflow count (if available)
    """
    data = _request_json(
        "GET",
        f"{N8N_API_URL}/api/v1/workflows",
        get_headers(),
        timeout=10.0,
    )

    # n8n can return either a list or an object containing data
    if isinstance(data, dict) and "data" in data:
        workflows = data.get("data") or []
    else:
        workflows = data if isinstance(data, list) else []

    return {"status": "ok", "workflows": len(workflows)}


def main():
    parser = argparse.ArgumentParser(description="n8n API Client")
    parser.add_argument(
        "--action",
        required=True,
        choices=[
            "list",
            "get",
            "create",
            "update",
            "delete",
            "activate",
            "deactivate",
            "execute",
            "webhook",
            "executions",
            "health",
        ],
        help="Action to perform",
    )
    parser.add_argument(
        "--workflow-id", help="Workflow ID for get/update/delete/activate/deactivate/execute"
    )
    parser.add_argument(
        "--workflow-file", help="JSON file with workflow definition for create/update"
    )
    parser.add_argument("--data", help="JSON data for execute/webhook")
    parser.add_argument("--webhook-path", help="Webhook path for webhook action")
    parser.add_argument("--active-only", action="store_true", help="List only active workflows")
    parser.add_argument("--status", help="Filter executions by status")

    args = parser.parse_args()

    # Validate environment
    if not N8N_API_URL or not N8N_API_KEY:
        print(
            json.dumps(
                {
                    "status": "error",
                    "message": "N8N_API_URL and N8N_API_KEY must be set in environment",
                }
            )
        )
        return

    try:
        result = None

        if args.action == "list":
            result = list_workflows(active_only=args.active_only)

        elif args.action == "get":
            if not args.workflow_id:
                raise ValueError("--workflow-id required for get action")
            result = get_workflow(args.workflow_id)

        elif args.action == "create":
            if not args.workflow_file:
                raise ValueError("--workflow-file required for create action")
            with open(args.workflow_file, "r") as f:
                workflow_data = json.load(f)
            result = create_workflow(workflow_data)

        elif args.action == "update":
            if not args.workflow_id or not args.workflow_file:
                raise ValueError("--workflow-id and --workflow-file required for update action")
            with open(args.workflow_file, "r") as f:
                workflow_data = json.load(f)
            result = update_workflow(args.workflow_id, workflow_data)

        elif args.action == "delete":
            if not args.workflow_id:
                raise ValueError("--workflow-id required for delete action")
            result = delete_workflow(args.workflow_id)

        elif args.action == "activate":
            if not args.workflow_id:
                raise ValueError("--workflow-id required for activate action")
            result = activate_workflow(args.workflow_id)

        elif args.action == "deactivate":
            if not args.workflow_id:
                raise ValueError("--workflow-id required for deactivate action")
            result = deactivate_workflow(args.workflow_id)

        elif args.action == "execute":
            if not args.workflow_id:
                raise ValueError("--workflow-id required for execute action")
            data = json.loads(args.data) if args.data else None
            result = execute_workflow(args.workflow_id, data)

        elif args.action == "webhook":
            if not args.webhook_path:
                raise ValueError("--webhook-path required for webhook action")
            data = json.loads(args.data) if args.data else {}
            result = trigger_webhook(args.webhook_path, data)

        elif args.action == "executions":
            result = list_executions(workflow_id=args.workflow_id, status=args.status)

        elif args.action == "health":
            result = health_check()

        print(json.dumps(result, indent=2))

    except HttpRequestError as e:
        print(
            json.dumps(
                {
                    "status": "error",
                    "code": e.status_code,
                    "message": str(e),
                    "response": e.response_text,
                }
            )
        )
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))


if __name__ == "__main__":
    main()
