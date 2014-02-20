# encoding: utf-8
import os
from fabric.api import *
from fabric.colors import green
from fabric.contrib.files import exists

PROJECT_NAME = 'site'
PROJECT_PATH = '/var/www/{0}'.format(PROJECT_NAME)

def prod():
    env.hosts = ['54.201.154.206']
    env.name = 'prod'
    env.user = 'ubuntu'
    env.key_filename = "deploy/site.pem"

def initial_setup():
    create_project_structure()
    sudo("echo \"localhost\" > /etc/hostname")
    sudo("hostname localhost")
    sudo("apt-get update")
    sudo("apt-get upgrade")
    install_packages()
    create_virtualenv()
    configure_nginx()
    configure_uwsgi() 
    deploy()
    sudo("reboot")

def deploy():
    upload()
    install_requirements()
    sudo("service nginx stop")
    sudo("service nginx start")

def create_project_structure():
    print(green("Creating directory structure in %s" % PROJECT_PATH))
    sudo("mkdir -p {0}".format(PROJECT_PATH))
    with cd(PROJECT_PATH):
        sudo("mkdir -p conf src logs/nginx logs/uwsgi run")

    sudo("chown -R {0} {1}".format(env.user, PROJECT_PATH))

def install_packages():
    f = open('./deploy/packages.txt')
    list_packages = ' '.join(f.read().split('\n'))
    sudo("apt-get install {0}".format(list_packages))

def install_requirements():
    print(green("Installing requirements"))

    requirements_path = os.path.join('requirements.txt')
    with cd(PROJECT_PATH):
        for line in open(requirements_path):
            package = line.replace("\n", "")
            run('virtualenv/bin/pip install {package}'.format(package=package), shell=False) 

def create_virtualenv():
    with cd(PROJECT_PATH):
        if not exists("virtualenv"):
            run("mkdir -p virtualenv")
            run("virtualenv ./virtualenv")

def configure_nginx():
    put("deploy/{env}/nginx.conf".format(env=env.name), "/tmp/nginx.conf")
    sudo("mv /tmp/nginx.conf {project_path}/conf/nginx.conf".format(project_path=PROJECT_PATH))

    sudo("rm -f /etc/nginx/sites-enabled/{0}.conf".format(PROJECT_NAME))
    sudo("ln -s {project_path}/conf/nginx.conf /etc/nginx/sites-enabled/{site}.conf".format(project_path=PROJECT_PATH, site=PROJECT_NAME))
    sudo("service nginx stop")
    sudo("service nginx start")

def configure_uwsgi():
    put("deploy/{env}/uwsgi.conf".format(env=env.name), "/tmp/uwsgi.conf")
    sudo("mv /tmp/uwsgi.conf /etc/init/")
    with cd(PROJECT_PATH):
        run('virtualenv/bin/pip install uwsgi', shell=False)

    run("touch {project_path}/run/uwsgi.pid".format(project_path=PROJECT_PATH))
    sudo("{project_path}/virtualenv/bin/uwsgi --reload {project_path}/run/uwsgi.pid".format(project_path=PROJECT_PATH)) 

def upload():
    print(green("Deploying site {0}".format(PROJECT_NAME)))

    local("tar -czf /tmp/{0}.tgz website/".format(PROJECT_NAME))
    put("/tmp/{0}.tgz".format(PROJECT_NAME), "/tmp/")
    run("tar -C /tmp -xzf /tmp/{0}.tgz".format(PROJECT_NAME))
    sudo("rm -rf {0}/src/website".format(PROJECT_PATH))
    sudo("mv /tmp/website {1}/src/".format(PROJECT_NAME, PROJECT_PATH))
    run("rm /tmp/{0}.tgz".format(PROJECT_NAME))
    local("rm -f /tmp/{0}.tgz".format(PROJECT_NAME))
