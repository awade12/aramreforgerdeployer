from __future__ import annotations

import argparse

from ..config import load_config


_COMMANDS = "setup quickstart menu helpdesk start stop restart logs tail update install status info check fix backup mods workshop configure ports doctor"


def cmd_completion(args: argparse.Namespace) -> None:
    if args.shell == "servers":
        try:
            _, config = load_config(args.config)
        except SystemExit:
            return
        print(" ".join(str(item.get("name", "")) for item in config.get("instances", []) if item.get("name")))
    elif args.shell == "bash":
        print(_bash())
    else:
        print(_zsh())


def _bash() -> str:
    return f'''# Add this to ~/.bashrc: eval "$(reforger completion bash)"
_reforger() {{
  local cur="${{COMP_WORDS[COMP_CWORD]}}" first="${{COMP_WORDS[1]}}"
  local servers="$(reforger completion servers 2>/dev/null)"
  local commands="{_COMMANDS}"
  if [[ $COMP_CWORD -eq 1 ]]; then
    COMPREPLY=( $(compgen -W "$commands $servers" -- "$cur") )
  elif [[ " $servers " == *" $first "* ]]; then
    COMPREPLY=( $(compgen -W "on off start stop restart logs tail health update install backup mods" -- "$cur") )
  else
    COMPREPLY=( $(compgen -W "$servers" -- "$cur") )
  fi
}}
complete -F _reforger reforger
'''


def _zsh() -> str:
    return f'''# Add this to ~/.zshrc: eval "$(reforger completion zsh)"
_reforger() {{
  local -a commands servers
  commands=({_COMMANDS})
  servers=(${{(s: :)$(reforger completion servers 2>/dev/null)}})
  _arguments '1:command or server:($commands $servers)' '*:server:($servers)'
}}
compdef _reforger reforger
'''
