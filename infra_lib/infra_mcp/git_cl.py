import subprocess

from mcp.server import fastmcp


async def try_builder_results(
    ctx: fastmcp.Context,
    checkout: str,
):
    """Gets the try builder results for the current CL
  
  Args:
    checkout: Location of the current checkout.

  Returns:
    A json list of builds that either ran or are still running on the current CL
  """
    command = [
        "git",
        "cl",
        "try-results",
        "--json=-",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    await ctx.info(f'stdout {result.stdout}')
    await ctx.info(f'stderr {result.stderr}')
    return result.stdout


async def get_current_changes(
    ctx: fastmcp.Context,
    checkout: str,
) -> str:
    """Shows differences between local tree and last upload.
  
  Args:
    checkout: Location of the current checkout.

  Returns:
    A diff of the current checkout and the last upload.
  """
    command = [
        "git",
        "cl",
        "diff",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    await ctx.info(f'stdout {result.stdout}')
    await ctx.info(f'stderr {result.stderr}')
    return result.stdout


async def format(
    ctx: fastmcp.Context,
    checkout: str,
) -> None:
    """Format the current checkout.

  This step should be called before attempting to upload any
  code.
  
  Args:
    checkout: Location of the current checkout.

  Returns:
    None
  """
    command = [
        "git",
        "cl",
        "format",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    await ctx.info(f'stdout {result.stdout}')
    await ctx.info(f'stderr {result.stderr}')
    return result.stdout


async def upload(
    ctx: fastmcp.Context,
    checkout: str,
) -> None:
    """Uploads the current committed changes to codereview

  This step should be called before attempting to upload any
  code.
  
  Args:
    checkout: Location of the current checkout.

  Returns:
    None
  """
    command = [
        "git",
        "cl",
        "upload",
        "-f",
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    await ctx.info(f'stdout {result.stdout}')
    await ctx.info(f'stderr {result.stderr}')
    return result.stdout


async def checkout(
    ctx: fastmcp.Context,
    checkout: str,
    issue: int,
) -> None:
    """Checks out a branch associated with a given Gerrit issue

  This should be run if an existing gerrit CL should be edited

  Args:
    checkout: Location of the current checkout.
    issue: The gerrit issue number
      The issue can be found in the url for a gerrit change.
      e.g. https://crrev.com/c/<gerrit-issue>
      e.g. https://chromium-review.googlesource.com/c/chromium/src/+/<gerrit-issue>

  Returns:
    None
  """
    command = [
        "git",
        "cl",
        "checkout",
        str(issue),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    await ctx.info(f'stdout {result.stdout}')
    await ctx.info(f'stderr {result.stderr}')
    return result.stdout
