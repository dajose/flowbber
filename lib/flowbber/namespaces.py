# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 KuraLabs S.R.L
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Namespaces for variables replacement.
"""

from os import environ
from collections import namedtuple

from .utils.command import run
from .logging import get_logger


log = get_logger(__name__)


def namespace_env(path):
    # Get the environment object
    safe_env = {
        key: value
        for key, value in environ.items()
        if not key.startswith('_')
    }

    env_type = namedtuple(
        'env',
        safe_env.keys()
    )
    env = env_type(**safe_env)

    log.debug('env namespace: {}'.format(env._replace(
        **{key: '****' for key in safe_env.keys()}
    )))
    return env


def namespace_pipeline(path):
    # Get pipeline object
    pipeline_type = namedtuple(
        'pipeline',
        ['dir', 'ext', 'file', 'name']
    )
    pipeline = pipeline_type(
        dir=str(path.parent),
        ext=path.suffix,
        file=path.name,
        name=path.stem,
    )

    log.debug('pipeline namespace: {}'.format(pipeline))
    return pipeline


def namespace_git(path):

    from shutil import which

    gitcmd = which('git')
    if gitcmd is None:
        log.debug('git executable not found')
        return None

    parent = str(path.parent)

    # Get repository root
    cmd_root = run([
        gitcmd, '-C', parent,
        'rev-parse', '--show-toplevel'
    ])
    if cmd_root.returncode != 0:
        log.debug('Unable to determine git repository root: {}'.format(
            cmd_root.stderr
        ))
        return None

    # Get current branch
    cmd_branch = run([
        gitcmd, '-C', parent,
        'rev-parse', '--abbrev-ref', 'HEAD'
    ])
    if cmd_branch.returncode != 0:
        log.debug('Unable to determine git branch: {}'.format(
            cmd_branch.stderr
        ))
        return None

    # Get current revision
    cmd_rev = run([
        gitcmd, '-C', parent,
        'rev-parse', '--short', '--verify', 'HEAD'
    ])
    if cmd_rev.returncode != 0:
        log.debug('Unable to determine git revision: {}'.format(
            cmd_rev.stderr
        ))
        return None

    # Get git object
    git_type = namedtuple(
        'git',
        ['root', 'branch', 'rev']
    )

    git = git_type(
        root=cmd_root.stdout,
        branch=cmd_branch.stdout,
        rev=cmd_rev.stdout,
    )

    log.debug('git namespace: {}'.format(git))
    return git


def get_namespaces(path):
    return {
        'env': namespace_env(path),
        'pipeline': namespace_pipeline(path),
        'git': namespace_git(path),
    }


__all__ = ['get_namespaces']