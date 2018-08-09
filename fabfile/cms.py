from fabric.api import *
from fabric.contrib.files import *
import common


@task
@roles('cms-db')
def db():
    "Install PostgreSQL and create the eio database"

#    execute(common.all)
#    execute(hosts)
    execute(install_db)
    execute(create_db)

@task
@roles('cms-head')
def head(reinstall='false'):
    "Provision CMS web frontend. When reinstall='true', recreates the cmsuser and its homedir from scratch."

#    execute(firewall)
#    execute(common.all)
#    execute(common.ssh_private_key)
    sudo('apt install -y daemon fabric')
#    execute(hosts)
    execute(install_deps)
#    execute(mail)
    execute(cmsuser, reinstall)
    execute(install_core)
#    execute(install_web)
#    execute(install_cmscli)
    execute(nginx)
    execute(init_db)


@task
def cmsuser(reinstall='false'):
    "Create cmsuser. When reinstall='true', recreates the cmsuser and its homedir from scratch."
    
    if reinstall.lower() in ['true', 'yes', 't', 'y', '1']: execute(delete_cmsuser)
    if contains('/etc/passwd', 'cmsuser'): return
    sudo("useradd cmsuser -c 'CMS user' -U -m")

@task
def delete_cmsuser():
    "Deletes cmsuser and its home directory, effectively uninstalling everything except the DB"

    sudo("killall -u cmsuser", warn_only=True)
    sudo("killall -u cmsuser -KILL", warn_only=True)
    sudo("deluser cmsuser")
    sudo("rm -rf /home/cmsuser")


@task
def install_db():
	sudo("apt-get install -y postgresql postgresql-client")
	#TODO: fancier conf
    
@task 
def install_deps():
	sudo("apt-get install -y build-essential openjdk-8-jre openjdk-8-jdk fpc \
	    gettext python2.7 \
	        iso-codes shared-mime-info stl-manual libcap-dev python-dev libpq-dev libcups2-dev libyaml-dev \
	     libffi-dev python-pip nginx-full php7.0-cli php7.0-fpm phppgadmin \
	     texlive-latex-base a2ps gcj-jdk haskell-platform git virtualenv nginx certbot")



@task
def install_core():
    "Install CMS core into /home/cmsuser"

    if exists('/home/cmsuser/install/cms'): return
    put(env.ROOTDIR + "/cfg/cms/" + env.CMS_CONF_NAME, '/home/cmsuser/cms.conf', use_sudo=True)
    sudo("""
        cd
        virtualenv env
        . env/bin/activate
        mkdir install
        cd install

        git clone http://github.com/raoz/cms.git -b master -changes --recursive
        cd cms
        pip install -r REQUIREMENTS.txt
        ./setup.py build install

        echo '. ~/env/bin/activate' >> /home/cmsuser/.bashrc
    """, user='cmsuser')
    sudo("""
        chown cmsuser.cmsuser /home/cmsuser/cms.conf
        mv /home/cmsuser/install/cms/isolate/isolate /usr/local/bin
        chown root.cmsuser /usr/local/bin/isolate
        chmod 04750 /usr/local/bin/isolate
    """)



@task
def create_db():
    "Create eio database"

    sudo(f"""
        psql <<EOS
        create user cmsuser password '{env.DB_PASSWORD}';
        create database cmsdb owner cmsuser;
        \c {dbname};
        ALTER SCHEMA public OWNER TO cmsuser;
        GRANT SELECT ON pg_largeobject TO cmsuser;
        EOS
        """)

def init_db():
    "cmsInitDb"
    pass

@task
def nginx():
    "Configure nginx to proxy CMS web"

    sudo('apt install -y nginx-full php7.0')
    with cd('/etc/nginx'):
        put(env.ROOTDIR + '/cfg/nginx', '.', use_sudo=True)
#        sudo('ln -fs /etc/nginx/sites-available/cms.eio.ee sites-enabled')
#    sudo('service php7.0-fpm start')
#TODO: use sites-available instead
#TODO: use php7.0-fpm
    sudo('service nginx reload')

@task
def init_db():
    "Initialize database tables for CMS and UserDB (run after install and install_web)"

    if 'cmsdb' in sudo("echo '\d' | psql cmsuser", user="postgres", quiet=True): return
    sudo("""
    cd
    . env/bin/activate
    CMS_CONFIG=cms.conf cmsInitDB
    """, user='cmsuser')
# eioUserDB --createdb
#TODO: enable eiouserdb
#TODO: cms.conf
