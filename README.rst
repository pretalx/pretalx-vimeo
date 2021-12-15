Vimeo integration
=================

This is a plugin for `pretalx`_ that provides an integration with Vimeo, allowing you to embed recordings on talk pages.

Additionally, the Plugin supplies an API at ``/api/events/<event>/p/vimeo/`` containing all configured Vimeo URLs, and
an API at ``/ap/events/<event>/submissions/<code>/p/vimeo/``, showing a submission's vimeo link.

Development setup
-----------------

1. Make sure that you have a working `pretalx development setup`_.

2. Clone this repository, eg to ``local/pretalx-vimeo``.

3. Activate the virtual environment you use for pretalx development.

4. Execute ``python setup.py develop`` within this directory to register this application with pretalx's plugin registry.

5. Execute ``make`` within this directory to compile translations.

6. Restart your local pretalx server. You can now use the plugin from this repository for your events by enabling it in
   the 'plugins' tab in the settings.


License
-------

Copyright 2021 Tobias Kunze

Released under the terms of the Apache License 2.0


.. _pretalx: https://github.com/pretalx/pretalx
.. _pretalx development setup: https://docs.pretalx.org/en/latest/developer/setup.html
