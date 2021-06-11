.. image:: https://raw.githubusercontent.com/giotto-ai/pyflagser/master/doc/images/Giotto_logo_RGB.svg
   :width: 590

|Azure|_ |Azure-cov|_ |Azure-test|_

.. |Azure| image:: https://dev.azure.com/maintainers/Giotto/_apis/build/status/giotto-ai.pyflagser?branchName=master
.. _Azure: https://dev.azure.com/maintainers/Giotto/_build?definitionId=5&_a=summary&repositoryFilter=5&branchFilter=116&requestedForFilter=ae4334d8-48e3-4663-af95-cb6c654474ea

.. |Azure-cov| image:: https://img.shields.io/azure-devops/coverage/maintainers/Giotto/5/master
.. _Azure-cov: 

.. |Azure-test| image:: https://img.shields.io/azure-devops/tests/maintainers/Giotto/5/master
.. _Azure-test:

.. |Twitter-follow| image:: https://img.shields.io/twitter/follow/giotto_ai?label=Follow%20%40giotto_ai&style=social
.. _Twitter-follow: https://twitter.com/intent/follow?screen_name=giotto_ai

.. |Slack-join| image:: https://img.shields.io/badge/Slack-Join-yellow
.. _Slack-join: https://slack.giotto.ai/

pyflagser
=========


``pyflagser`` is a python API for the flagser C++ library by Daniel Lütgehetmann which computes the homology of directed flag complexes. Please check out the original `luetge/flagser <https://github.com/luetge/flagser>`_ GitHub repository for more information.

Project genesis
---------------

``pyflagser`` is the result of a collaborative effort between `L2F SA <https://www.l2f.ch/>`_, the `Laboratory for Topology and Neuroscience <https://www.epfl.ch/labs/hessbellwald-lab/>`_ at EPFL, and the `Institute of Reconfigurable & Embedded Digital Systems (REDS) <https://heig-vd.ch/en/research/reds>`_ of HEIG-VD.

Installation
------------

Dependencies
~~~~~~~~~~~~

``pyflagser`` requires:

- Python (>= 3.6)
- NumPy (>= 1.17.0)
- SciPy (>= 0.17.0)

User installation
~~~~~~~~~~~~~~~~~

If you already have a working installation of numpy and scipy, the easiest way to install pyflagser is using ``pip``   ::

    python -m pip install -U pyflagser

Documentation
-------------

API reference (stable release): https://docs-pyflagser.giotto.ai

Contributing
------------

We welcome new contributors of all experience levels. The Giotto community goals are to be helpful, welcoming, and effective. To learn more about making a contribution to ``pyflagser``, please see the `CONTRIBUTING.rst <https://github.com/giotto-ai/pyflagser/blob/master/CONTRIBUTING.rst>`_ file.

Developer installation
~~~~~~~~~~~~~~~~~~~~~~

C++ dependencies:
'''''''''''''''''

-  C++14 compatible compiler
-  CMake >= 3.9

Source code
'''''''''''

You can check the latest sources with the command::

    git clone https://github.com/giotto-ai/pyflagser.git


To install:
'''''''''''

From the cloned repository's root directory, run

.. code-block:: bash

   python -m pip install -e ".[tests]"

This way, you can pull the library's latest changes and make them immediately available on your machine.

Testing
~~~~~~~

After installation, you can launch the test suite from outside the source directory::

    pytest pyflagser


Changelog
---------

See the `RELEASE.rst <https://github.com/giotto-ai/pyflagser/blob/master/RELEASE.rst>`__ file
for a history of notable changes to pyflagser.

Important links
~~~~~~~~~~~~~~~

- Official source code repo: https://github.com/giotto-ai/pyflagser
- Download releases: https://pypi.org/project/pyflagser/
- Issue tracker: https://github.com/giotto-ai/pyflagser/issues


Contacts:
---------

maintainers@giotto.ai
