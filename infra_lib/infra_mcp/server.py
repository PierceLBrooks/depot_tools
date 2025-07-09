"""TODO: sshrimp - DO NOT SUBMIT without one-line documentation for mcp.

TODO: sshrimp - DO NOT SUBMIT without a detailed description of mcp.
"""
import json
import subprocess
from collections.abc import Sequence

from absl import app

from mcp.server import fastmcp
mcp = fastmcp.FastMCP("TestMCP")


@mcp.tool(name="ping_tool")
def ping_tool(
) -> None:
  return


@mcp.tool(name="log_tool")
async def log_tool(
  ctx: fastmcp.Context,
) -> None:
  await ctx.info('hello')
  return


@mcp.tool(name="try_results")
async def try_results(
  checkout: str,
  ctx: fastmcp.Context,
  ):
  """Gets the try builder result for the current CL
  
  Args:
    checkout: Location of the current checkout.

  Returns:
    A list of builds run on the current checkout.
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
  checkout: str, 
  builder: str, 
  bucket: str, 
  test_suite: str, 
  ctx: fastmcp.Context,
  ):
  """Recreates the compile step of the provided builder and targets

  Args:
    checkout: Location of the current checkout.
    builder: Name of the builder to test
    bucket: Bucket the builder belongs to (e.g. "try", or "ci")
    test_suite: Test suite to build.

  Returns:
    A list of builds run on the current checkout.
  """
  stdout, stderr = run_utr('compile', checkout, builder, bucket, test_suite)
  await ctx.info(f'stdout {stdout}')
  await ctx.info(f'stderr {stderr}')
  return stdout


@mcp.tool(name="test_builder_test")
async def test_builder_test(
  checkout: str, 
  builder: str, 
  bucket: str, 
  test_suite: str, 
  ctx: fastmcp.Context,
  ):
  """Recreates the test step of the provided builder and targets

  Args:
    checkout: Location of the current checkout.
    builder: Name of the builder to test
    bucket: Bucket the builder belongs to (e.g. "try", or "ci")
    test_suite: Test suite to build.

  Returns:
    A list of builds run on the current checkout.
  """
  stdout, stderr = run_utr('test', checkout, builder, bucket, test_suite)
  await ctx.info(f'stdout {stdout}')
  await ctx.info(f'stderr {stderr}')
  return stdout


@mcp.tool(name="get_build")
async def get_build(
    request: dict,
    ctx: fastmcp.Context,
) -> str:
  """Calls the buildbucket.v2.Builds.GetBuild RPC to fetch a build.

  The url of a build can be deconstructed and used to get more details about the
  build. e.g.
  https://ci.chromium.org/ui/p/chromium/builders/<bucket>/<builder name>/<build number>/infra
  Builds can also be in the form:
  https://ci.chromium.org/b/<build id>

  Args:
    request: The request body for the RPC. All fields should be represented by
      strings. Integer fields will be parsed later.
      https://chromium.googlesource.com/infra/luci/luci-go/+/main/buildbucket/proto/builds_service.proto
      for more details.

      The request's mask can be set to get more information. By default only
      high level statuses will be returned. Some useful fields to include in this mask are:
      status, input, output, id, builder, builder_info, tags, steps, infra
      Multiple fields in the mask can be included as a comma separated string. e.g.
      {
        "build_number": "<build number>",
        "builder": {
          "bucket": "<bucket>",
          "builder": "<builder name>",
          "project": "chromium"
        },
        "mask": {
          "fields": "steps,tags"
        }
      }
      The build_number is mutually exclusive with the build_id. To get the build from a build_id, only
      the build_id is needed. e.g.
      {
        "id": "<build id>",
        "mask": {
          "fields": "steps,tags"
        }
      }

  Returns:
    The stdout of the prpc command which should be a JSON string for a
    buildbucket.v2.Build proto. See
    https://chromium.googlesource.com/infra/luci/recipes-py/+/main/recipe_proto/go.chromium.org/luci/buildbucket/proto/build.proto
    for more details.
  """
  await ctx.info(f'Received request {request}')
  command = [
      "prpc",
      "call",
      "cr-buildbucket.appspot.com",
      "buildbucket.v2.Builds.GetBuild",
  ]
  try:
    result = subprocess.run(
        command,
        capture_output=True,
        input=json.dumps(request),
        check=False,
        text=True,
    )
    await ctx.info(result.stdout)
    await ctx.info(result.stderr)
  except Exception as e:
    await ctx.info('Exception calling prpc')
    return f'Exception calling prpc return {e}'
  return result.stdout


@mcp.prompt(
  name="fix_chrome_build_request",
  description="Generates a request to fix a specific build from it's url"
)
def fix_chrome_build_request(url:str) -> str:
  """Generates a prompt to attempt to fix a broken chrome build"""
  return f'''
AI Prompt: Chrome Build Failure Resolution Agent


Role: You are a senior software engineer on the Google Chrome team. Your primary responsibility is to diagnose and fix build
failures in the Chromium project. You are an expert in C++, the GN build system, and the Chromium development workflow,
including interacting with the Gerrit code review system.


Goal: Autonomously analyze the failed build {url}, develop a correct code fix, and upload that fix to Gerrit as a
new Change List (CL) for a dry run (CQ+1).


Core Context:
* The Chromium source code is located in the /usr/local/google/home/sshrimp/chromium-checkouts/chromium/src directory.
* Build recipes and related infrastructure code are in /usr/local/google/home/sshrimp/infra_checkouts/build
* You must use the provided tools to interact with the build system, filesystem, and version control.

---


Mandatory Workflow

You must follow this sequence of steps precisely.


Step 1: Analyze the Build Failure
1. You will be given a URL to a failed build (e.g., https://ci.chromium.org/ui/p/chromium/builders/...).
2. Use the get_build tool to fetch the build details.
3. Carefully examine the summaryMarkdown and the steps of the failing steps to determine the root cause.
4. Concisely state the root cause of the failure before proceeding.


Step 2: Investigate and Formulate a Plan
1. Based on the error, determine which files need to be modified. Use glob and search_file_content to locate the relevant
source files (.cc, .h) or build files (BUILD.gn).
2. Read the contents of these files using read_file to understand the context of the required change.
3. Formulate a clear, step-by-step plan to fix the issue. You must state this plan before implementing it. For example: "The build failed due to a missing dependency. I will add //chrome/browser/foo:bar to the deps list in the //chrome/browser/baz/BUILD.gn file."


Step 3: Implement the Fix
1. Create a new git branch for your fix. The branch name should be descriptive of the fix.
    * Command: run_shell_command with git checkout -b <descriptive-branch-name>
2. Modify the necessary files using the replace or write_file tool. Ensure your changes are minimal, correct, and adhere to all surrounding code styles and project conventions.
3. Run `git cl format` to ensure the change is well formatted.


Step 4: Create and Upload the Change List (CL)
1. Stage your changes using git add.
2. Commit your changes with a well-formatted, multi-line commit message.
    * Template:


1         [Component]: Brief, imperative summary of the fix
2 
3         Detailed explanation of the problem and the fix. Describe why the
4         change is necessary and how it resolves the build failure.
5 
6         Fixed: <URL of the failed build>

    * Example Commit Command:
        git commit -m "actor: Add impl dependency to test_support\n\nThis change resolves a GN dependency error by adding the ':impl' target to the test_support' source set. This allows actor_test_util.cc to include headers from the :impl target, fixing the 'Include not allowed' error.\n\nFixed: https://ci.chromium.org/ui/p/chromium/builders/try/linux-rel/2283517/infra"
3. Upload the change to Gerrit to create a new CL. The command must set a dry run (CQ+1) and add sshrimp@google.com as the reviewer.
    * Command: run_shell_command with `git cl upload --reviewers sshrimp@google.com --cq-dry-run`


Step 5: Final Output
* Provide the URL of the newly created Gerrit CL as your final response. Your task is complete once you output the URL.
'''

def main(argv: Sequence[str]) -> None:
  if len(argv) > 1:
    raise app.UsageError("Too many command-line arguments.")
  mcp.run()


if __name__ == "__main__":
  app.run(main)