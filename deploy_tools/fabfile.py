import random
from fabric.contrib.files import append, exists
from fabric.api import cd, env, local, run, hosts
import re

REPO_URL = 'https://github.com/yamen225/Superlists'


@hosts(['superlists-staging.ottg.eu'])
def get_vagrant_staging_connection():
    local('cd ~/vagrant_ObeyTheTestingGoat_staging; vagrant up')
    result = local('cd ~/vagrant_ObeyTheTestingGoat; vagrant ssh-config',
                   capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(
        r'IdentityFile\s+([^\n]+)', result)[0].lstrip("\"").rstrip("\"")
    deploy()


@hosts(['superlists.ottg.eu'])
def get_vagrant_deployment_connection():
    local('cd ~/vag_OTG_prod; vagrant up')
    result = local('cd ~/vag_OTG_prod; vagrant ssh-config',
                   capture=True)
    hostname = re.findall(r'HostName\s+([^\n]+)', result)[0]
    port = re.findall(r'Port\s+([^\n]+)', result)[0]
    env.hosts = ['%s:%s' % (hostname, port)]
    env.user = re.findall(r'User\s+([^\n]+)', result)[0]
    env.key_filename = re.findall(
        r'IdentityFile\s+([^\n]+)', result)[0].lstrip("\"").rstrip("\"")
    deploy()


def deploy():
    site_folder = f'/home/{env.user}/sites/{env.host}'
    run(f'mkdir -p {site_folder}')
    with cd(site_folder):
        _get_latest_source()
        _update_virtualenv()
        _create_or_update_dotenv()
        _update_static_files()
        _update_database()


def _get_latest_source():
    if exists('.git'):
        run('git fetch')
    else:
        run(f'git clone {REPO_URL} .')
    current_commit = local(
        "git --git-dir ~/ObeyTheTesingGoat/superlists/.git log -n 1 --format=%H",
        capture=True)

    run(f'git reset --hard {current_commit}')


def _update_virtualenv():
    if not exists('virtualenv/bin/pip'):
        run(f'python3.6 -m venv virtualenv')
    run('./virtualenv/bin/pip install -r requirements.txt')


def _create_or_update_dotenv():
    append('.env', 'DJANG_DEBUG_FALSE=y')
    append('.env', f'SITENAME={env.host}')
    current_contents = run('cat .env')
    if 'DJANGO_SECRET_KEY' not in current_contents:
        new_secret = ''.join(random.SystemRandom().choices(
            'abcdefghijklmnopqrstuvwxyz0123456789', k=50
        ))
        append('.env', f'DJANGO_SECRET_KEY={new_secret}')


def _update_static_files():
    run('./virtualenv/bin/python manage.py collectstatic --noinput')


def _update_database():
    run('./virtualenv/bin/python manage.py migrate --noinput')
