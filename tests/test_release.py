# ABOUTME: One-off verification tests for release.sh — dry-run mode and SKIP_TESTS support.
# ABOUTME: Verifies AC3.1: coding standards adherence for release script.
# NOTE: These are NOT part of the regression pack (make test). Run manually.
import os
import subprocess

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RELEASE_SH = os.path.join(REPO_ROOT, 'scripts', 'release.sh')
ENV = {
    **os.environ,
    'PATH': f'/usr/bin:/bin:/usr/sbin:/sbin:{os.path.expanduser("~/bin")}:'
            f'{os.path.expanduser("~/.local/bin")}:/opt/homebrew/bin:'
            f'/opt/homebrew/sbin:/usr/local/bin:{os.environ.get("PATH", "")}',
}


def test_release_dry_run_exits_zero():
    """AC3.1 test 2: ./scripts/release.sh --dry-run exits 0 with descriptive output."""
    result = subprocess.run(
        [RELEASE_SH, '--dry-run'],
        cwd=REPO_ROOT,
        env=ENV,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, (
        f'release.sh --dry-run failed:\nstdout: {result.stdout}\nstderr: {result.stderr}'
    )
    # Must produce output (descriptive)
    assert len(result.stdout.strip()) > 0, 'No output from --dry-run'


def test_release_dry_run_shows_test_before_tag():
    """AC3.1 test 3: --dry-run output shows test step before tag step."""
    result = subprocess.run(
        [RELEASE_SH, '--dry-run'],
        cwd=REPO_ROOT,
        env=ENV,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout
    # Find positions of test and tag mentions
    test_pos = output.find('make test')
    tag_pos = output.find('git tag')
    assert test_pos != -1, f'No "make test" step found in dry-run output:\n{output}'
    assert tag_pos != -1, f'No "git tag" step found in dry-run output:\n{output}'
    assert test_pos < tag_pos, (
        f'"make test" should appear before "git tag" in dry-run output:\n{output}'
    )


def test_release_dry_run_skip_tests_shows_message():
    """AC3.1 test 4: SKIP_TESTS=1 --dry-run shows skip message instead of test step."""
    env_skip = {**ENV, 'SKIP_TESTS': '1'}
    result = subprocess.run(
        [RELEASE_SH, '--dry-run'],
        cwd=REPO_ROOT,
        env=env_skip,
        capture_output=True,
        text=True,
        timeout=30,
    )
    output = result.stdout.lower()
    assert 'skip' in output, f'No skip message in SKIP_TESTS=1 dry-run output:\n{result.stdout}'
