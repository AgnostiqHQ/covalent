#!/usr/bin/env python

import subprocess

import refactor


def main():
    command = refactor.__path__[0] + "/queuer/nats-server"
    subprocess.Popen([command])
