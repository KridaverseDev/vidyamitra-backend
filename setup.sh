#!/bin/bash

set -e

# Installing pyenv. A python version manager.

if which pyenv >>/dev/null; then
    echo "Pyenv is already installed"
else
    echo "Downloading and Installing pyenv."
    echo ""
    curl https://pyenv.run | bash
    {
        echo ""
        echo "# Variables for pyenv"
        echo 'export PYENV_ROOT="$HOME/.pyenv"'
        echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"'
        echo 'eval "$(pyenv init -)"'
    } >>~/.bashrc
    # Retaining path for current session.
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"

    # verifying if pyenv is installed
    command -v pyenv >>/dev/null
fi

echo ""

# Installing 3.12
echo "Installing python 3.12"
echo ""

pyenv install 3.12 -s

# Setting current python version as global.

echo " Setting 3.12 as global version. You can change this later "
pyenv global 3.12

# Check if python is installed.
python --version >>/dev/null

echo ""

# Addding ~/.local path if does not exsits.
if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    {
        echo ""
        echo "# User local installation directory"
        echo 'PATH="$HOME/.local/bin:$PATH"'
    } >>~/.bashrc
    PATH="$HOME/.local/bin:$PATH"
fi

# Installing pants
echo "Installing pants"
echo ""

if ! command -v pants >>/dev/null; then
    echo "Downloading and Installing pants"
    curl --proto '=https' --tlsv1.2 -fsSL https://static.pantsbuild.org/setup/get-pants.sh | bash
else
    echo "Pants is already installed "
fi

echo ""

# Check if pants is installed
command -v pants >>/dev/null

# Installing poetry
pip install poetry
echo ""

echo "Intialising environment directory"
{
    echo ""
    echo 'export POETRY_VIRTUALENVS_IN_PROJECT=true'
} >>~/.bashrc
export POETRY_VIRTUALENVS_IN_PROJECT=true

# Initializing poetry and pants in the project.
echo "Initializing poetry and pants in the project."
echo ""

poetry install
echo ""

pants
