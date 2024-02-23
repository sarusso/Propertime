Welcome to Propertime API documentation!
=============================================


Propertime is an attempt at implementing proper time management in Python,
by fully embracing the extra complications arising due to the intrinsic need of
conflating together physical and calendar time instead of neglecting them.

In a nutshell, it provides two main classes: the ``Time`` class for representing
time (similar to a datetime) and the ``TimeUnit`` class for representing units
of time (similar to a timedelta). Such classes play nice with Python datetimes so
that you can mix and match and use them only when needed.

You can have a look at the `README <https://github.com/sarusso/Propertime/blob/main/README.md>`_
for a better introduction, some example usage and more info about Propertime.

This is the API documentation. You might also want to check out the
`quickstart notebook <https://github.com/sarusso/Propertime/blob/main/Quickstart.ipynb>`_

|

Modules
-------

.. automodule:: propertime
    :members:
    :inherited-members:
    :undoc-members:


.. autosummary::
     :toctree:

     time
     utilities
     logger
     exceptions

|

Other resources
---------------

* :ref:`Alphabetical index <genindex>`

* `GitHub <https://github.com/sarusso/Propertime>`_

* `License <https://github.com/sarusso/Propertime/blob/main/LICENSE>`_
