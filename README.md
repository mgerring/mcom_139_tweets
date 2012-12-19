django-live-template
====================

A Django project template based on [mbg-boilerplate](https://github.com/mgerring/mbg-boilerplate). Updates live in the browser. Vertical rhythym based on φ. Includes South and Django Debug Toolbar for great success.

Requirements
-----
pip, Django 1.4

Usage
-----

Use this project as a template with the ```startproject``` command, like so:

```django-admin.py startproject myproject --template=/path/to/django-live-template```

After your project has been created, run: 

```pip -r requirements.txt``` 

to install some useful development tools like [django-debug-toolbar](https://github.com/django-debug-toolbar/django-debug-toolbar), [django-livejs](https://github.com/wellnesstelecom/django-livejs), and [south](http://south.aeracode.org/).

It is reccomended that you create a file called ```local_settings.py``` in the same directory as ```settings.py```.

In ```local_settings.py``` include the line ```DEBUG=True```. Git will ignore your ```local_settings.py``` by default, so when you deploy to production, ```DEBUG``` will be set to ```False```.

Setting ```DEBUG=True``` enables settings in ```debug_settings.py```, which includes settings that enable the development tools you installed earlier, and also loads ```less.js``` on the frontend, allowing you to develop your application's stylesheet using [less](https://github.com/cloudhead/less.js).

Issues
------

Use the [issue tracker](https://github.com/mgerring/django-live-template/issues) to report any problems.
