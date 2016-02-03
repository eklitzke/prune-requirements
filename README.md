# Prune Requirements

Over time your `requirements.txt` file may become cluttered with a lot of
unnecessary dependencies. This tool helps your figure out what you can remove.

Note that because of the dynamic nature of Python, it's impossible to really
tell what you can remove. You could integrate a tool like this with your unit
tests, but it would make it a lot slower.

You should carefully review any recommendations it makes.

## Installation

Install it like this:

```
python setup.py install
```

## Usage

You run it like this:

```bash
prune-requirements -r requirements.txt <bootstrap1> <bootstrap2> ...
```

Most projects won't need to bootstrap anything. However, let's say that your
project requires a certain version of pip, like 1.7.0. Then you might do:

```bash
prune-requirements -r requirements.txt "pip==1.7.0"
```

Some projects also have a file called `requirements-bootstrap.txt` that specify
certain dependencies that are needed to install the rest of the requirements.
Then you might do:

```bash
python prune_requirements.py -r requirements.txt "pip==1.7.0" "requirements-bootstrap.txt"
```

This would cause the bootstrapper to run the equivalent of:

```bash
pip install "pip==1.7.0"
pip install -r requirements-bootstrap.txt
```

The `prune-requirements` command will infer which bootstrap dependencies are
packages and which are files based on whether the dependency exists as a file on
the local filesystem.
