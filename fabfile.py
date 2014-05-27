#-*- coding: utf-8 -*-
import os
from contextlib import nested

from fabric.api import *
from fabric.contrib.console import confirm
from fabric.utils import abort


env.user = 'e5r'
env.home = '/home/e5r/domains/mm-api-demo.e5r.no'
env.hosts = ['heinlein.e5r.no']

def deploy(branch='master'):
    """Lanser HEAD fra master i staging eller production miljøet."""
    require('environment', provided_by=('staging', 'production'))
    if env.environment == 'production':
        if not confirm("Er du sikker på at du vil lansere til 'production'?",
                               default=False):
            abort("Lansering til 'production' kansellert.")
    pull(branch)
    update_requirements()
    #migrate()
    collect_static()
    reload()

def pull(branch):
    """Henter HEAD fra master."""
    require('root', provided_by=('staging', 'production'))
    with nested(cd(env.root), show('stdout')):
        run("git pull")
        run("git checkout -B {0} origin/{0}".format(branch))

def update_requirements():
    """Oppdater pakker definert i requirements.txt og node package.json."""
    require('root', provided_by=('staging', 'production'))
    with nested(cd(env.root), hide('stdout'),
                prefix('source %(virtualenv)s/bin/activate' % env)):
        run("pip install -r requirements.txt")
        run("npm install")
        run("bower install")

def migrate():
    """Migrer databasen."""
    require('root', provided_by=('staging', 'production'))
    with nested(cd(env.root),
                prefix('source %(virtualenv)s/bin/activate' % env)):
        run("./manage.py migrate")

def collect_static():
    """Kompilerer og komprimerer statiske ressurser før lansering."""
    require('root', provided_by=('staging', 'production'))
    with nested(cd(env.root),
                prefix('source %(virtualenv)s/bin/activate' % env)):
        run("grunt build")
        run("yes yes | ./manage.py collectstatic")

def reload():
    """Omstart webserveren."""
    require('root', provided_by=('staging', 'production'))
    with nested(cd(env.home)):
        run("bin/stop.sh && bin/init.sh")

def staging():
    """Forbereder bruk av 'staging' miljøet."""
    env.environment = 'staging'
    env.root = os.path.join(env.home, 'code/staging')
    env.virtualenv = os.path.join(env.home, '.virtualenvs/staging')

def production():
    """Forbereder bruk av 'production' miljøet."""
    env.environment = 'production'
    env.root = os.path.join(env.home, 'code/prod')
    env.virtualenv = os.path.join(env.home, '.virtualenvs/prod')
