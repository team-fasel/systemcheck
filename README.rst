===========
systemcheck
===========


A Python based extensible configuration validation solution


* Free software: MIT license
* Documentation: https://systemcheck.readthedocs.io.

The software is under heavy development at the moment. I started this project 4+ years ago to teach myself Python. It
became quite sophisticated over time and was instrumental during my last engagement, where I shared it with my
teammates.

My previous customer claims ownership on the improvements I made during my last engagement. That means, I can't release
that version anymore. It's not a big deal. I guess everybody who learned a new programming language cringes at the code
they wrote when they started out ;-)

I gave myself 4 weeks to get the software to a stage where all that's left is implementing the plugins. So check back
in 4 weeks if you are interested.

Mini-Roadmap
------------

* Foundations:
  - SQLAlchemy data models for systems and credentials
  - Credential Manager to securely store and retrieve credentials to get assigned to a system

* Generic System:
  - Develop the UI independent generic system manager
  - Develop the generic system manager UI

* ABAP:
  - Develop the UI independent ABAP management routines
    + A simple batch scheduling mechanism
    + Spool Downloader
    + Table Downloader
  - Adapt the generic UI for ABAP
  - Develop Plugin Types:
    + Retrieve and validate runtime parameters
    + Retrieve and validate the parameters in the profile
    + Retrieve and validate table contents
    + Execute and validate RSUSR* reports using their RFC API
    + Validate Batch Scheduling
    + ...
  - Develop Plugins based on the plugin types
    + Use Case Demonstration based on implementing SAP's Security Baseline Guide (https://support.sap.com/sos)

