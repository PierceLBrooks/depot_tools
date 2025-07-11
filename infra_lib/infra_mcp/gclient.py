import subprocess

from mcp.server import fastmcp


async def sync_checkout(
    ctx: fastmcp.Context,
    checkout: str,
    revision: str = 'HEAD',
) -> None:
    """Syncs the current checkout to the provided revision or HEAD

  Handles getting the current checkout to the provided revision or
  HEAD and then syncs all the submodules.

  Args:
    checkout: Location of the current checkout.
    revision: Revision to sync to or HEAD if not provided.

  Returns:
    None
  """
    result = subprocess.run(
        [
            'git',
            'checkout',
            revision,
        ],
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    await ctx.info(f'stdout {result.stdout}')
    await ctx.info(f'stderr {result.stderr}')

    result = subprocess.run(
        [
            'gclient',
            'sync',
            '-f',
        ],
        capture_output=True,
        check=False,
        text=True,
        cwd=checkout,
    )
    await ctx.info(f'stdout {result.stdout}')
    await ctx.info(f'stderr {result.stderr}')
