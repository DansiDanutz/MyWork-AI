"""Tests for mw api command."""
import os
import shutil
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from tools.mw import cmd_api


@pytest.fixture
def temp_dir():
    d = tempfile.mkdtemp()
    old = os.getcwd()
    os.chdir(d)
    yield d
    os.chdir(old)
    shutil.rmtree(d, ignore_errors=True)


def test_api_help(capsys):
    ret = cmd_api(["--help"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "API Generator" in out


def test_api_init(temp_dir, capsys):
    ret = cmd_api(["init", "myapp"])
    assert ret == 0
    assert os.path.exists(os.path.join(temp_dir, "myapp", "app", "main.py"))
    assert os.path.exists(os.path.join(temp_dir, "myapp", "app", "database.py"))
    assert os.path.exists(os.path.join(temp_dir, "myapp", "requirements.txt"))
    assert os.path.exists(os.path.join(temp_dir, "myapp", "run.py"))
    assert os.path.exists(os.path.join(temp_dir, "myapp", "README.md"))


def test_api_init_duplicate(temp_dir, capsys):
    cmd_api(["init", "dup"])
    ret = cmd_api(["init", "dup"])
    assert ret == 1
    out = capsys.readouterr().out
    assert "already exists" in out


def test_api_init_no_name(capsys):
    ret = cmd_api(["init"])
    assert ret == 1


def test_api_add_model(temp_dir, capsys):
    cmd_api(["init", "proj"])
    os.chdir(os.path.join(temp_dir, "proj"))
    ret = cmd_api(["add-model", "User", "name:str", "email:str", "age:int"])
    assert ret == 0
    assert os.path.exists("app/models/user.py")
    assert os.path.exists("app/schemas/user.py")
    assert os.path.exists("app/routes/user.py")
    # Check main.py has the import
    with open("app/main.py") as f:
        content = f.read()
    assert "user_router" in content


def test_api_add_model_invalid_type(temp_dir, capsys):
    cmd_api(["init", "proj2"])
    os.chdir(os.path.join(temp_dir, "proj2"))
    ret = cmd_api(["add-model", "Bad", "name:banana"])
    assert ret == 1


def test_api_add_model_invalid_field(temp_dir, capsys):
    cmd_api(["init", "proj3"])
    os.chdir(os.path.join(temp_dir, "proj3"))
    ret = cmd_api(["add-model", "Bad", "nocolon"])
    assert ret == 1


def test_api_add_model_no_project(temp_dir, capsys):
    ret = cmd_api(["add-model", "User", "name:str"])
    assert ret == 1


def test_api_add_model_missing_args(capsys):
    ret = cmd_api(["add-model"])
    assert ret == 1


def test_api_routes_no_project(temp_dir, capsys):
    ret = cmd_api(["routes"])
    assert ret == 1


def test_api_routes(temp_dir, capsys):
    cmd_api(["init", "rproj"])
    os.chdir(os.path.join(temp_dir, "rproj"))
    cmd_api(["add-model", "Item", "name:str", "price:float"])
    ret = cmd_api(["routes"])
    assert ret == 0
    out = capsys.readouterr().out
    assert "Item" in out


def test_api_unknown_subcmd(capsys):
    ret = cmd_api(["banana"])
    assert ret == 1


def test_api_multiple_models(temp_dir, capsys):
    cmd_api(["init", "multi"])
    os.chdir(os.path.join(temp_dir, "multi"))
    cmd_api(["add-model", "User", "name:str"])
    cmd_api(["add-model", "Post", "title:str", "body:text"])
    assert os.path.exists("app/models/user.py")
    assert os.path.exists("app/models/post.py")
    with open("app/main.py") as f:
        content = f.read()
    assert "user_router" in content
    assert "post_router" in content


def test_api_all_field_types(temp_dir, capsys):
    cmd_api(["init", "types"])
    os.chdir(os.path.join(temp_dir, "types"))
    ret = cmd_api(["add-model", "AllTypes", "s:str", "i:int", "f:float", "b:bool", "d:datetime", "t:text"])
    assert ret == 0
    with open("app/models/alltypes.py") as f:
        content = f.read()
    assert "String" in content
    assert "Integer" in content
    assert "Float" in content
    assert "Boolean" in content
    assert "DateTime" in content
    assert "Text" in content
