Arduino Data Server
===================

Installation
------------

Dependencies: Django>=1.3, south

There is no package for pip yet. Currently, you need to checkout the project and link the *arduinodataserver* library in your project. For instance:

    django-admin.py startproject testproject
    cd testproject
    ln -s /path/to/arduinodataserver .

Edit your settings.py and add *arduinodataserver* to INSTALLED_APPS. Then run:

    python manage.py syncdb
    python manage.py migrate arduinodataserver

Add arduinodataserver to your urls.py. For instance:

    from django.conf.urls.defaults import patterns, include, url
    
    # Uncomment the next two lines to enable the admin:
    from django.contrib import admin
    admin.autodiscover()
    
    urlpatterns = patterns('',
        url(r'^admin/', include(admin.site.urls)),
        url(r'', include('arduinodataserver.urls')),
    )

Running the TCP server
----------------------

    python manage.py dataserver --port=9999 --addr=192.168.1.1

Running the TCP server in daemon mode
-------------------------------------
If you want to make a start-up script for your server, you can also run in daemon mode. If there is an existing pid file, then that server process will be killed.

    python manage.py dataserver --daemon --port=9999 --addr=192.168.1.1 --pid-file=/tmp/arduinodataserver.pid

Creating a test project
-----------------------

Before getting started, you might want to explore how this application is working.
