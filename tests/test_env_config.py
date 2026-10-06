"""Env contract tests (Task 1): prod guard with strong secret, conftest secret pin."""

import os

from app.main import create_app


def test_prod_with_strong_secret_boots(monkeypatch):
    """APP_ENV=production + strong JWT_SECRET -> create_app() boots without error."""
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "task1-strong-secret-not-the-default")
    create_app()


def test_conftest_pins_test_secret():
    """Suite-wide pin: os.environ JWT_SECRET == 'test-secret' with no per-test setup."""
    assert os.environ.get("JWT_SECRET") == "test-secret"
