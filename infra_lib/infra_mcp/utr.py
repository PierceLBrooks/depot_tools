import json
import subprocess
from collections.abc import Sequence

from mcp.server import fastmcp

mcp = fastmcp.FastMCP("utr")


async def run_utr(
    command: str,
    checkout: str,
    builder: str,
    bucket: str,
    test_suite: str,
):
    result = subprocess.run(
        [
            "vpython3",
            "tools",
            "utr",
            "run.py",
            "-B",
            bucket,
            "-b",
            builder,
            "-t",
            test_suite,
            command,
        ],
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    return result.stdout, result.stderr


@mcp.tool(name="test_builder_compile")
async def test_builder_compile(
    ctx: fastmcp.Context,
    checkout: str,
    builder: str,
    bucket: str,
    test_suite: str,
):
    """Recreates the build/compile step of the provided builder and targets

  Args:
    checkout: Location of the current checkout.
    builder: Name of the builder to test
    bucket: Bucket the builder belongs to (e.g. "try", or "ci")
    test_suite: Test suite to build, or "all" to build everything.

  Returns:
    A list of builds run on the current checkout.
  """
    stdout, stderr = run_utr('compile', checkout, builder, bucket, test_suite)
    await ctx.info(f'stdout {stdout}')
    await ctx.info(f'stderr {stderr}')
    return stdout


@mcp.tool(name="test_builder_test")
async def test_builder_test(
    ctx: fastmcp.Context,
    checkout: str,
    builder: str,
    bucket: str,
    test_suite: str = 'all',
):
    """Recreates the test step of the provided builder and targets

  Args:
    checkout: Location of the current checkout.
    builder: Name of the builder to test
    bucket: Bucket the builder belongs to (e.g. "try", or "ci")
    test_suite: Test suite to build, or "all" to build everything.

  Returns:
    A list of builds run on the current checkout.
  """
    stdout, stderr = run_utr('test', checkout, builder, bucket, test_suite)
    await ctx.info(f'stdout {stdout}')
    await ctx.info(f'stderr {stderr}')
    return stdout
