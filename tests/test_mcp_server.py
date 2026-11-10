"""Integration tests for the MCP server using FastMCP's in-memory client.

Tool calls are mocked at the server boundary so the suite does not need a live
Smalltalk image. Each tool is exercised on FastMCP 4's default modern protocol
(``mode="auto"``) and on the legacy handshake (``mode="legacy"``).
"""

import asyncio
from unittest.mock import patch

import fastmcp
import pytest
from fastmcp import Client

from smalltalk_interop_mcp_server.server import mcp

# Read snake_case MCP fields. The camelCase bridge is temporary and warns.
# https://gofastmcp.com/docs/getting-started/upgrading/from-fastmcp-3
fastmcp.settings.mcp_camelcase_compat = False

MODES = ["auto", "legacy"]

# Fields set on each tool. Unset hints stay at the SDK default and are not
# asserted, so this stays aligned with the annotations in server.py.
EXPECTED_ANNOTATIONS = {
    "eval": {
        "title": "Evaluate Smalltalk",
        "destructive_hint": True,
        "open_world_hint": False,
    },
    "get_class_source": {
        "title": "Get Class Source",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "get_method_source": {
        "title": "Get Method Source",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "get_class_comment": {
        "title": "Get Class Comment",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "search_classes_like": {
        "title": "Search Classes Like",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "search_methods_like": {
        "title": "Search Methods Like",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "search_implementors": {
        "title": "Search Implementors",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "search_references": {
        "title": "Search References",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "list_packages": {
        "title": "List Packages",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "list_classes": {
        "title": "List Classes",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "export_package": {
        "title": "Export Package",
        "idempotent_hint": True,
        "open_world_hint": False,
    },
    "import_package": {
        "title": "Import Package",
        "destructive_hint": True,
        "open_world_hint": False,
    },
    "run_package_test": {
        "title": "Run Package Test",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "run_class_test": {
        "title": "Run Class Test",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "list_extended_classes": {
        "title": "List Extended Classes",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "list_methods": {
        "title": "List Methods",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "search_traits_like": {
        "title": "Search Traits Like",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "search_references_to_class": {
        "title": "Search References to Class",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "install_project": {
        "title": "Install Project",
        "destructive_hint": True,
        "open_world_hint": True,
    },
    "read_screen": {
        "title": "Read Screen",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "get_settings": {
        "title": "Get Settings",
        "read_only_hint": True,
        "open_world_hint": False,
    },
    "apply_settings": {
        "title": "Apply Settings",
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
    },
    "reset_connection": {
        "title": "Reset Connection",
        "destructive_hint": False,
        "idempotent_hint": True,
        "open_world_hint": False,
    },
}

# (tool, arguments, core function, positional args, keyword args)
TOOL_CALLS = [
    ("eval", {"code": "1 + 1"}, "interop_eval", ("1 + 1",), {}),
    (
        "get_class_source",
        {"class_name": "Object"},
        "interop_get_class_source",
        ("Object",),
        {},
    ),
    (
        "get_method_source",
        {
            "class_name": "Array",
            "method_name": "with:",
            "is_class_method": True,
        },
        "interop_get_method_source",
        ("Array", "with:"),
        {"is_class_method": True},
    ),
    (
        "get_class_comment",
        {"class_name": "Object"},
        "interop_get_class_comment",
        ("Object",),
        {},
    ),
    (
        "search_classes_like",
        {"class_name_query": "Obj*"},
        "interop_search_classes_like",
        ("Obj*",),
        {},
    ),
    (
        "search_methods_like",
        {"method_name_query": "hash*"},
        "interop_search_methods_like",
        ("hash*",),
        {},
    ),
    (
        "search_implementors",
        {"method_name": "hash"},
        "interop_search_implementors",
        ("hash",),
        {},
    ),
    (
        "search_references",
        {"method_name_or_symbol": "#hash"},
        "interop_search_references",
        ("#hash",),
        {},
    ),
    ("list_packages", {}, "interop_list_packages", (), {}),
    (
        "list_classes",
        {"package_name": "Kernel"},
        "interop_list_classes",
        ("Kernel",),
        {},
    ),
    (
        "export_package",
        {"package_name": "Kernel", "path": "/tmp/out"},
        "interop_export_package",
        ("Kernel", "/tmp/out"),
        {},
    ),
    (
        "import_package",
        {"package_name": "Kernel", "path": "/tmp/in"},
        "interop_import_package",
        ("Kernel", "/tmp/in"),
        {},
    ),
    (
        "run_package_test",
        {"package_name": "Kernel"},
        "interop_run_package_test",
        ("Kernel",),
        {},
    ),
    (
        "run_class_test",
        {"class_name": "KernelTest"},
        "interop_run_class_test",
        ("KernelTest",),
        {},
    ),
    (
        "list_extended_classes",
        {"package_name": "Kernel"},
        "interop_list_extended_classes",
        ("Kernel",),
        {},
    ),
    (
        "list_methods",
        {"package_name": "Kernel"},
        "interop_list_methods",
        ("Kernel",),
        {},
    ),
    (
        "search_traits_like",
        {"trait_name_query": "T*"},
        "interop_search_traits_like",
        ("T*",),
        {},
    ),
    (
        "search_references_to_class",
        {"class_name": "Object"},
        "interop_search_references_to_class",
        ("Object",),
        {},
    ),
    (
        "install_project",
        {
            "project_name": "Proj",
            "repository_url": "https://example.com/proj.git",
            "load_groups": "Core,Tests",
            "force": True,
        },
        "interop_install_project",
        ("Proj", "https://example.com/proj.git", "Core,Tests", True),
        {},
    ),
    (
        "read_screen",
        {"target_type": "spec", "capture_screenshot": False},
        "interop_read_screen",
        ("spec", False),
        {},
    ),
    ("get_settings", {}, "interop_get_settings", (), {}),
    (
        "apply_settings",
        {"settings": {"stackSize": 200}},
        "interop_apply_settings",
        ({"stackSize": 200},),
        {},
    ),
    (
        "reset_connection",
        {"host": "127.0.0.1", "port": 8081},
        "interop_reset_connection",
        ("127.0.0.1", 8081),
        {},
    ),
]


async def _list_tools(mode: str):
    async with Client(mcp, mode=mode) as client:
        return await client.list_tools()


async def _call_tool(mode: str, name: str, arguments: dict):
    async with Client(mcp, mode=mode) as client:
        return await client.call_tool(name, arguments)


class TestMCPServer:
    """Tools exposed through the MCP protocol on FastMCP 4."""

    @pytest.mark.parametrize("mode", MODES)
    def test_list_tools(self, mode):
        tools = asyncio.run(_list_tools(mode))
        assert {tool.name for tool in tools} == set(EXPECTED_ANNOTATIONS)

    @pytest.mark.parametrize("mode", MODES)
    def test_tool_annotations_are_snake_case(self, mode):
        tools = {tool.name: tool for tool in asyncio.run(_list_tools(mode))}
        wire_names = {
            "title": "title",
            "read_only_hint": "readOnlyHint",
            "destructive_hint": "destructiveHint",
            "idempotent_hint": "idempotentHint",
            "open_world_hint": "openWorldHint",
        }
        for name, expected in EXPECTED_ANNOTATIONS.items():
            annotations = tools[name].annotations
            wire = annotations.model_dump(by_alias=True)
            for field, value in expected.items():
                assert getattr(annotations, field) == value, name
                # Wire format stays camelCase; only the Python attributes moved.
                assert wire[wire_names[field]] == value, name
            with pytest.raises(AttributeError):
                annotations.readOnlyHint  # noqa: B018

    @pytest.mark.parametrize("mode", MODES)
    def test_input_schemas_use_snake_case(self, mode):
        expected_properties = {
            name: set(arguments) for name, arguments, *_rest in TOOL_CALLS
        }
        tools = asyncio.run(_list_tools(mode))
        assert {tool.name for tool in tools} == set(expected_properties)
        for tool in tools:
            schema = tool.input_schema
            assert schema["type"] == "object"
            assert set(schema.get("properties", {})) == expected_properties[tool.name]
            with pytest.raises(AttributeError):
                tool.inputSchema  # noqa: B018

    @pytest.mark.parametrize("mode", MODES)
    @pytest.mark.parametrize(
        ("tool_name", "arguments", "impl_name", "args", "kwargs"),
        TOOL_CALLS,
        ids=[call[0] for call in TOOL_CALLS],
    )
    def test_call_tool(self, mode, tool_name, arguments, impl_name, args, kwargs):
        payload = {"success": True, "result": tool_name}
        with patch(
            f"smalltalk_interop_mcp_server.server.{impl_name}",
            return_value=payload,
        ) as mock_impl:
            result = asyncio.run(_call_tool(mode, tool_name, arguments))

        assert result.data == payload
        mock_impl.assert_called_once_with(*args, **kwargs)
