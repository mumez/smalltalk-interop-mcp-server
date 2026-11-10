"""FastMCP server for Smalltalk evaluation."""

from typing import Annotated, Any

from fastmcp import Context, FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from .core import (
    interop_apply_settings,
    interop_eval,
    interop_export_package,
    interop_get_class_comment,
    interop_get_class_source,
    interop_get_method_source,
    interop_get_settings,
    interop_import_package,
    interop_install_project,
    interop_list_classes,
    interop_list_extended_classes,
    interop_list_methods,
    interop_list_packages,
    interop_read_screen,
    interop_reset_connection,
    interop_run_class_test,
    interop_run_package_test,
    interop_search_classes_like,
    interop_search_implementors,
    interop_search_methods_like,
    interop_search_references,
    interop_search_references_to_class,
    interop_search_traits_like,
)

# MCP SDK v2 (FastMCP 4) uses snake_case ToolAnnotations fields.
# https://gofastmcp.com/docs/getting-started/upgrading/from-fastmcp-3
mcp = FastMCP("smalltalk-interop-mcp-server")


@mcp.tool(
    "eval",
    annotations=ToolAnnotations(
        title="Evaluate Smalltalk",
        destructive_hint=True,
        open_world_hint=False,
    ),
)
def eval_code(
    _: Context,
    code: Annotated[str, Field(description="The Smalltalk code to evaluate")],
) -> dict[str, Any]:
    """
    Evaluate a Smalltalk expression via the Smalltalk Interop Server.

    Args:
        code: The Smalltalk code to evaluate

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": any} - result contains the evaluation result
        - Error: {"success": False, "error": str | dict} - error contains an error message,
          or a detailed object with description/stack_trace/receiver for enhanced errors
        - Unserializable result: {"success": True, "error": {"description": str,
          "suggestion": str}} - the expression evaluated without error but its result
          could not be serialized as JSON; error.suggestion advises how to adjust the
          expression (e.g. append `printString`)
    """
    return interop_eval(code)


@mcp.tool(
    "get_class_source",
    annotations=ToolAnnotations(
        title="Get Class Source",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def get_class_source(
    _: Context,
    class_name: Annotated[
        str, Field(description="The name of the class to retrieve source for")
    ],
) -> dict[str, Any]:
    """
    Get the source code of a Smalltalk class.

    Args:
        class_name: The name of the class to retrieve source for

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains the class source code
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_get_class_source(class_name)


@mcp.tool(
    "get_method_source",
    annotations=ToolAnnotations(
        title="Get Method Source",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def get_method_source(
    _: Context,
    class_name: Annotated[
        str, Field(description="The name of the class containing the method")
    ],
    method_name: Annotated[
        str, Field(description="The name of the method to retrieve source for")
    ],
    is_class_method: Annotated[
        bool,
        Field(
            description="Set to True for class-side methods, False for instance methods (default: False)"
        ),
    ] = False,
) -> dict[str, Any]:
    """
    Get the source code of a specific method in a class.

    Args:
        class_name: The name of the class containing the method
        method_name: The name of the method to retrieve source for
        is_class_method: True for class-side methods, False for instance methods (default: False)

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains the method source code
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_get_method_source(
        class_name, method_name, is_class_method=is_class_method
    )


@mcp.tool(
    "get_class_comment",
    annotations=ToolAnnotations(
        title="Get Class Comment",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def get_class_comment(
    _: Context,
    class_name: Annotated[
        str, Field(description="The name of the class to retrieve comment for")
    ],
) -> dict[str, Any]:
    """
    Get the comment of a Smalltalk class.

    Args:
        class_name: The name of the class to retrieve comment for

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains the class comment
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_get_class_comment(class_name)


@mcp.tool(
    "search_classes_like",
    annotations=ToolAnnotations(
        title="Search Classes Like",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def search_classes_like(
    _: Context,
    class_name_query: Annotated[
        str, Field(description="The pattern to search for in class names")
    ],
) -> dict[str, Any]:
    """
    Find classes matching a pattern.

    Args:
        class_name_query: The pattern to search for in class names

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[str]} - result contains list of matching class names
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_search_classes_like(class_name_query)


@mcp.tool(
    "search_methods_like",
    annotations=ToolAnnotations(
        title="Search Methods Like",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def search_methods_like(
    _: Context,
    method_name_query: Annotated[
        str, Field(description="The pattern to search for in method names")
    ],
) -> dict[str, Any]:
    """
    Find methods matching a pattern.

    Args:
        method_name_query: The pattern to search for in method names

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[str]} - result contains list of matching method names
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_search_methods_like(method_name_query)


@mcp.tool(
    "search_implementors",
    annotations=ToolAnnotations(
        title="Search Implementors",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def search_implementors(
    _: Context,
    method_name: Annotated[
        str, Field(description="The method name to find implementors for")
    ],
) -> dict[str, Any]:
    """
    Get all implementors of a method selector.

    Args:
        method_name: The method name to find implementors for

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[dict]} - result contains list of implementors
          Each implementor: {"class": str, "method": str, "package": str}
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_search_implementors(method_name)


@mcp.tool(
    "search_references",
    annotations=ToolAnnotations(
        title="Search References",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def search_references(
    _: Context,
    method_name_or_symbol: Annotated[
        str, Field(description="The method name or symbol to find references for")
    ],
) -> dict[str, Any]:
    """
    Get all references to a method selector or a symbol.

    Args:
        method_name_or_symbol: The method name to find references for

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[dict]} - result contains list of references
          Each reference: {"class": str, "method": str, "package": str}
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_search_references(method_name_or_symbol)


@mcp.tool(
    "list_packages",
    annotations=ToolAnnotations(
        title="List Packages",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def list_packages(_: Context) -> dict[str, Any]:
    """
    Get list of all packages.

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[str]} - result contains list of all package names
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_list_packages()


@mcp.tool(
    "list_classes",
    annotations=ToolAnnotations(
        title="List Classes", read_only_hint=True, open_world_hint=False
    ),
)
def list_classes(
    _: Context,
    package_name: Annotated[str, Field(description="The name of the package")],
) -> dict[str, Any]:
    """
    Get list of classes in a package.

    Args:
        package_name: The name of the package

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[str]} - result contains list of class names in package
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_list_classes(package_name)


@mcp.tool(
    "export_package",
    annotations=ToolAnnotations(
        title="Export Package",
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def export_package(
    _: Context,
    package_name: Annotated[
        str, Field(description="The name of the package to export")
    ],
    path: Annotated[
        str, Field(description="The path where to export the package")
    ] = "/tmp",
) -> dict[str, Any]:
    """
    Export a package in Tonel format.

    Args:
        package_name: The name of the package to export
        path: The path where to export the package (default: /tmp)

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains export success message with path
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_export_package(package_name, path)


@mcp.tool(
    "import_package",
    annotations=ToolAnnotations(
        title="Import Package",
        destructive_hint=True,
        open_world_hint=False,
    ),
)
def import_package(
    _: Context,
    package_name: Annotated[
        str, Field(description="The name of the package to import")
    ],
    path: Annotated[
        str, Field(description="The path to the package file to import")
    ] = "/tmp",
) -> dict[str, Any]:
    """
    Import a package from specified path.

    Args:
        package_name: The name of the package to import
        path: The path to the package file to import (default: /tmp)

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains import success message
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_import_package(package_name, path)


@mcp.tool(
    "run_package_test",
    annotations=ToolAnnotations(
        title="Run Package Test",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def run_package_test(
    _: Context,
    package_name: Annotated[
        str, Field(description="The package name to run tests for")
    ],
) -> dict[str, Any]:
    """
    Run tests for a package.

    Args:
        package_name: The package name to run tests for

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains test results summary
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_run_package_test(package_name)


@mcp.tool(
    "run_class_test",
    annotations=ToolAnnotations(
        title="Run Class Test",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def run_class_test(
    _: Context,
    class_name: Annotated[str, Field(description="The class name to run tests for")],
) -> dict[str, Any]:
    """
    Run tests for a class.

    Args:
        class_name: The class name to run tests for

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains test results summary
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_run_class_test(class_name)


@mcp.tool(
    "list_extended_classes",
    annotations=ToolAnnotations(
        title="List Extended Classes",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def list_extended_classes(
    _: Context,
    package_name: Annotated[str, Field(description="The name of the package")],
) -> dict[str, Any]:
    """
    Get list of extended classes in a package.

    Args:
        package_name: The name of the package

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[str]} - result contains list of extended class names
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_list_extended_classes(package_name)


@mcp.tool(
    "list_methods",
    annotations=ToolAnnotations(
        title="List Methods", read_only_hint=True, open_world_hint=False
    ),
)
def list_methods(
    _: Context,
    package_name: Annotated[str, Field(description="The name of the package")],
) -> dict[str, Any]:
    """
    Get list of methods in a package.

    Args:
        package_name: The name of the package

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[str]} - result contains list of method signatures
          Each method: "ClassName>>#methodName"
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_list_methods(package_name)


@mcp.tool(
    "search_traits_like",
    annotations=ToolAnnotations(
        title="Search Traits Like",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def search_traits_like(
    _: Context,
    trait_name_query: Annotated[
        str, Field(description="The pattern to search for in trait names")
    ],
) -> dict[str, Any]:
    """
    Find traits matching a pattern.

    Args:
        trait_name_query: The pattern to search for in trait names

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[str]} - result contains list of matching trait names
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_search_traits_like(trait_name_query)


@mcp.tool(
    "search_references_to_class",
    annotations=ToolAnnotations(
        title="Search References to Class",
        read_only_hint=True,
        open_world_hint=False,
    ),
)
def search_references_to_class(
    _: Context,
    class_name: Annotated[
        str, Field(description="The name of the class to find references for")
    ],
) -> dict[str, Any]:
    """
    Find references to a class.

    Args:
        class_name: The name of the class to find references for

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": list[dict]} - result contains list of class references
          Each reference: {"package": str, "class": str, "method": str}
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_search_references_to_class(class_name)


@mcp.tool(
    "install_project",
    annotations=ToolAnnotations(
        title="Install Project",
        destructive_hint=True,
        open_world_hint=True,
    ),
)
def install_project(
    _: Context,
    project_name: Annotated[
        str, Field(description="The name of the project to install")
    ],
    repository_url: Annotated[
        str, Field(description="The repository URL for the project")
    ],
    load_groups: Annotated[
        str | None, Field(description="Comma-separated list of groups to load")
    ] = None,
    force: Annotated[
        bool,
        Field(description="Force load ignoring conflicts, upgrades, and image changes"),
    ] = False,
) -> dict[str, Any]:
    """
    Install a project using Metacello.

    Args:
        project_name: The name of the project to install
        repository_url: The repository URL for the project
        load_groups: Comma-separated list of groups to load (optional)
        force: Force load ignoring conflicts, upgrades, and image changes (optional)

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains installation success message
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_install_project(project_name, repository_url, load_groups, force)


@mcp.tool(
    "read_screen",
    annotations=ToolAnnotations(
        title="Read Screen", read_only_hint=True, open_world_hint=False
    ),
)
def read_screen(
    _: Context,
    target_type: Annotated[
        str,
        Field(
            description="UI type to inspect: 'world' (morphs), 'spec' (windows, Pharo only), or 'roassal' (visualizations, Pharo only)"
        ),
    ] = "world",
    capture_screenshot: Annotated[
        bool, Field(description="Include PNG screenshot in response")
    ] = True,
) -> dict[str, Any]:
    """
    Comprehensive UI screen reader for debugging Smalltalk interfaces.

    Captures screenshot and extracts complete UI structure for World morphs (Pharo and Squeak),
    and Spec presenters and Roassal visualizations (Pharo only).

    Args:
        target_type: 'world' for morphs, 'spec' for Spec windows (Pharo only), 'roassal' for visualizations (Pharo only)
        capture_screenshot: Include PNG screenshot in response (default: true)

    Returns:
        dict: UI structure and metrics
        - screenshot: Path to PNG file in /tmp/ (if capture_screenshot=true)
        - target_type: Which UI type was inspected
        - structure: Complete UI hierarchy data
        - summary: Human-readable description
    """
    return interop_read_screen(target_type, capture_screenshot)


@mcp.tool(
    "get_settings",
    annotations=ToolAnnotations(
        title="Get Settings", read_only_hint=True, open_world_hint=False
    ),
)
def get_settings(_: Context) -> dict[str, Any]:
    """
    Retrieve current server configuration.

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": dict} - result contains current server settings
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_get_settings()


@mcp.tool(
    "apply_settings",
    annotations=ToolAnnotations(
        title="Apply Settings",
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def apply_settings(
    _: Context,
    settings: Annotated[
        dict[str, Any], Field(description="Settings dictionary to apply to the server")
    ],
) -> dict[str, Any]:
    """
    Modify server configuration dynamically.

    Args:
        settings: Dictionary containing server settings to modify

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": str} - result contains confirmation message
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_apply_settings(settings)


@mcp.tool(
    "reset_connection",
    annotations=ToolAnnotations(
        title="Reset Connection",
        destructive_hint=False,
        idempotent_hint=True,
        open_world_hint=False,
    ),
)
def reset_connection(
    _: Context,
    host: Annotated[
        str | None,
        Field(
            description="SIS host to connect to (default: localhost). Empty values use localhost."
        ),
    ] = None,
    port: Annotated[
        int | None,
        Field(
            description="SIS port to connect to (default: SIS_PORT, or 8086 if unset/invalid)"
        ),
    ] = None,
) -> dict[str, Any]:
    """
    Recreate the HTTP connection to the Smalltalk Interop Server.

    Use this to switch the MCP server to another SIS host or port at runtime
    without restarting the process. Omitted arguments fall back to localhost
    and SIS_PORT (or 8086).

    Args:
        host: SIS host (default: localhost)
        port: SIS port (default: SIS_PORT or 8086)

    Returns:
        dict: API response with success/error and result
        - Success: {"success": True, "result": {"host": str, "port": int, "base_url": str}}
        - Error: {"success": False, "error": str} - error contains error message
    """
    return interop_reset_connection(host, port)


def main():
    """Main entry point for the server."""
    mcp.run()


if __name__ == "__main__":
    main()
