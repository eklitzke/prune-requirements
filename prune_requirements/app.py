import argparse
import os
import subprocess
import re


PYTHON_RE = re.compile('^python-')
PACKAGE_RE = re.compile(r'^([-a-zA-Z0-9._]+)')

BOOTSTRAP_FILE = """
#!/bin/bash
set -e
rm -rf env &>/dev/null
virtualenv env &>/dev/null
. env/bin/activate &>/dev/null
%s
pip install -r "$1" &>/dev/null
pip freeze
""".lstrip()


def munge_package(package):
    munged_package = PYTHON_RE.sub('', package)
    if '-' in munged_package:
        return [munged_package.replace('-', '_'),
                munged_package.replace('-', '.')]
    return [munged_package]


def create_bootstrap_file(bootstrap_commands):
    bootstrap = []
    for cmd in bootstrap_commands:
        if os.path.exists(cmd):
            bootstrap.append('pip install -r "%s" &>/dev/null' % (cmd,))
        else:
            bootstrap.append('pip install "%s" &>/dev/null' % (cmd,))
    bootstrap_text = '\n'.join(bootstrap)
    with open('bootstrap.sh', 'w') as bootstrap_file:
        bootstrap_file.write(BOOTSTRAP_FILE % bootstrap_text)


def parse_requirements(reqfile):
    all_packages = set()
    for line in reqfile:
        line = line.strip()
        m = PACKAGE_RE.match(line)
        if not m:
            continue
        package_name, = m.groups()
        all_packages.add(package_name)
    return all_packages


def prune_packages(packages, aggressive):
    if aggressive:
        return packages

    new_packages = []
    for package in packages:
        saw_package = False
        for pkg in munge_package(package):
            proc = subprocess.Popen(['git', 'grep', '-i', pkg],
                                    stdout=subprocess.PIPE)
            for line in proc.stdout:
                file_name = line.split(':')[0]
                if file_name.endswith('.py'):
                    saw_package = True
                    break
            if saw_package:
                break
        if not saw_package:
            new_packages.append(package)
    return new_packages


def try_package(not_needed, requirements_txt, package_name):
    with open(requirements_txt) as requirements:
        with open('candidate.txt', 'w') as candidate:
            for line in requirements:
                needed = not line.startswith(package_name)
                if needed:
                    for pkg in not_needed:
                        if line.startswith(pkg):
                            needed = False
                            break
                if needed:
                    candidate.write(line)

    saw_package = False
    proc = subprocess.Popen(['bash', 'bootstrap.sh', 'candidate.txt'],
                            stdout=subprocess.PIPE)
    for line in proc.stdout:
        if line.startswith(package_name):
            saw_package = True
            break
    proc.wait()

    if not saw_package and proc.returncode == 0:
        print 'NOT NEEDED: %s' % (package_name,)
        not_needed.add(package_name)
        return True


def iterate_all_packages(all_packages, requirements_txt):
    not_needed = set()
    iteration = 1
    while True:
        packages = set(all_packages) - not_needed
        num_packages = len(packages)
        saw_any = False
        for i, package in enumerate(sorted(packages)):
            print '%d: %d/%d (not needed %d) %s' % (
                iteration, i + 1, num_packages, len(not_needed), package)
            saw_any |= bool(try_package(not_needed, requirements_txt, package))
        if not saw_any:
            break
        else:
            iteration += 1
    return not_needed


def cleanup():
    for f in ['candidate.txt', 'bootstrap.sh']:
        try:
            os.unlink(f)
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--aggressive', action='store_true')
    parser.add_argument('-r', '--requirements-file',
                        default='requirements.txt')
    parser.add_argument('bootstrap', nargs='*')
    args = parser.parse_args()
    try:
        create_bootstrap_file(args.bootstrap)
        with open(args.requirements_file) as requirements_txt:
            packages = parse_requirements(requirements_txt)
        packages = prune_packages(packages, args.aggressive)
        not_needed = iterate_all_packages(packages, args.requirements_file)
        print
        print 'ALL NOT NEEDED'
        print '=============='
        for package in sorted(not_needed):
            print package
    finally:
        cleanup()
