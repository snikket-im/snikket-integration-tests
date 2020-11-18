# Integration tests for Snikket

# Dependencies

Software:

- terraform (0.12+)
- jq
- Python 3
- [Appium-Python-Client](https://github.com/appium/python-client#appium-python-client)

Services:

- An AWS account
- A BrowserStack account

## Contents

`config-examples/`
: Example configuration files.

`terraform-env`
: Per-environment (e.g. AWS account) resources./

`terraform-server/`
: Per-run resources, used by `setup.sh` and `teardown.sh`.

`tests/`
: The client tests.

`setup.sh`
: Set up the per-run test infrastructure.

`run.sh`
: Run the tests.

`teardown.sh`
: Destroy the per-run test infrastructure.

`upload.sh`
: Upload a new app build to BrowserStack. Accepts an app ID followed by a
  local filename or URL.

# Environment

The following environment variables should be present:

`CONFIG_DIR`
:   The path to the configuration files (see below). Defaults to `/etc/snikket-integration-tests`
    if not set. Should be absolute.

`BUILD_NUM`
:   A unique name for this build, e.g. `Build 555`

# Configuration

The configuration directory should contain the following files:

`browserstack-auth.json`
: Username + access key for Browserstack

`terraform-env.tfvars`
: Configuration specific to the test environment, used as input to Terraform. 
