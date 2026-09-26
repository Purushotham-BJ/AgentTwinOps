"""Test runner script — writes results to /tmp/pytest_out.txt inside the container."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-p", "no:warnings"],
    cwd="/app",
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

output = result.stdout
print(output)

with open("/tmp/pytest_out.txt", "w") as f:
    f.write(output)

sys.exit(result.returncode)
