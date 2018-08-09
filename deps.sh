yes |sudo service apache2 stop
# Feel free to change OpenJDK packages with your preferred JDK.
yes |sudo apt-get install build-essential openjdk-8-jre openjdk-8-jdk fpc \
	    postgresql postgresql-client gettext python2.7 \
	        iso-codes shared-mime-info stl-manual libcap-dev

# Only if you are going to use pip/virtualenv to install python dependencies
yes |sudo apt-get install python-dev libpq-dev libcups2-dev libyaml-dev \
	     libffi-dev python-pip

# Optional
yes |sudo apt-get install nginx-full php7.0-cli php7.0-fpm phppgadmin \
	     texlive-latex-base a2ps gcj-jdk haskell-platform

yes |sudo apt-get install git virtualenv
