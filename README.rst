Mallos
======

Mallos is a multiprocess spider, inspired by Alex Kritikos' Patu_, that splits the work of IO bound tasks and
CPU bound tasks into different processes.  IO processes fetch urls and place
them into a queue for processing.  The processing consists of parsing the html,
extracting the links, and is executed by the parent process.

.. _Patu: http://github.com/akrito/patu