@task 
def install_deps():
	sudo("apt-get install -y build-essential openjdk-8-jre openjdk-8-jdk fpc \
	    postgresql postgresql-client gettext python2.7 \
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
