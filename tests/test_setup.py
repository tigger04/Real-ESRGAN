# ABOUTME: Tests for setup.py metadata — verifies Python version classifiers and constraints.
# ABOUTME: Verifies AC5.1–AC5.3: Python 3.12 classifiers, python_requires, BSD licence.
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETUP_PY = os.path.join(REPO_ROOT, 'setup.py')


def _read_setup():
    with open(SETUP_PY) as f:
        return f.read()


def test_setup_classifiers_python_312_only():
    """AC5.1: Classifiers reference Python 3.12, not 3.7 or 3.8."""
    content = _read_setup()
    assert '3.12' in content, 'Python 3.12 not in setup.py classifiers'
    assert "'Programming Language :: Python :: 3.7'" not in content, 'Python 3.7 still in classifiers'
    assert "'Programming Language :: Python :: 3.8'" not in content, 'Python 3.8 still in classifiers'


def test_setup_python_requires():
    """AC5.2: setup.py declares python_requires >= 3.12."""
    content = _read_setup()
    assert 'python_requires' in content, 'python_requires not in setup.py'
    assert '3.12' in content, 'python_requires does not reference 3.12'


def test_setup_bsd_licence_classifier():
    """AC5.3: Licence classifier matches BSD-3-Clause."""
    content = _read_setup()
    assert 'BSD' in content, 'No BSD licence classifier in setup.py'
    assert 'Apache' not in content, 'Apache licence classifier still in setup.py'
