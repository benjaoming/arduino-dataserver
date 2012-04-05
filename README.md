Arduino Data Server
===================

Use case: You have an arduino and an ethernet shield. You want to log and display data send from the arduino on a web and mobile platform. No problem, with arduino-dataserver, you can manage your sensor data and automatically have a whole range of auto-generated summaries visualised through a fancy, modern interface based on Twitter Bootstrap and Google Charts.

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

    python manage.py dataserver --port=9999 --addr=192.168.100.1

Running the TCP server in daemon mode
-------------------------------------
If you want to make a start-up script for your server, you can also run in daemon mode. If there is an existing pid file, then that server process will be killed.

    python manage.py dataserver --daemon --port=9999 --addr=192.168.100.1 --pid-file=/tmp/arduinodataserver.pid

Creating a test project
-----------------------

Before getting started, you might want to explore how this application is working.

Arduino test script
-------------------

UNFINISHED. Connect to the server and send some data:

    /*
      Telnet client
     
     This sketch showcases an incremental 
     counter sending data to arduino-dataserver every second.
     
     Based on Tom Igoe's sketchbook example "TelnetClient"
     
     */
    
    #include <SPI.h>
    #include <Ethernet.h>
    
    // Enter a MAC address and IP address for your controller below.
    // The IP address will be dependent on your local network:
    byte mac[] = {  
      0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
    byte ip[] = { 
      192,168,100,2 };
    
    // Enter the IP address of the server you're connecting to:
    byte server[] = { 
      192,168,100,1 }; 
    
    int meter_counter = 0;
    int meter_id = 1;
    
    Client client(server, 9999);
    
    void setup() {
      // start the Ethernet connection:
      Ethernet.begin(mac, ip);
      // start the serial library:
      Serial.begin(9600);
      // give the Ethernet shield a second to initialize:
      delay(1000);
    }
    
    void loop()
    {
    
      delay(1000);
    
      // if you get a connection, report back via serial:
      if (!client.connected()) {
        Serial.println("Creating connection...");
        if (client.connect()) {
          Serial.println("Connection established");
        }
        else {
          // if you didn't get a connection to the server:
          Serial.println("connection failed");
          client.stop();
          return;
        }
      }
      
      // If the connection works, send data
      if (client.connected()) {
        client.print(meter_id);
        client.print(":");
        client.print(meter_counter);
        client.print(";");
      }
      
      // Increment test data no matter what. The arduino
      // should keep collecting sensor data, disregarding
      // the network's health.
      meter_counter ++;
      
      // Simulate that the counter restarts
      if (meter_counter > 1000) {
        meter_counter = 1;
      }
      
    }
