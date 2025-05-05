#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Setup zsh as default shell if not already set
if [ "$(basename "$SHELL")" != "zsh" ]; then
  echo "Changing default shell to zsh..."
  chsh -s "$(which zsh)"

  # Install oh-my-zsh
  if [ ! -d ~/.oh-my-zsh ]; then
    echo "Installing oh-my-zsh..."
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
  fi
fi

# Copy zsh config
if [ ! -f ~/.zshrc ]; then
  echo "Copying zsh configuration..."
  cp zshrc ~/.zshrc
fi

# Copy git config
if [ ! -f ~/.gitconfig ]; then
  echo "Copying git configuration..."
  cp gitconfig ~/.gitconfig

  # setup git environment
  git config --global user.name "Manas Maheshwari"
  git config --global user.email "manas.maheshwari@recogni.com"
fi
