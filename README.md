Before Run
==========
Need to set up environment variable PYTHONPATH once (only need to run once)
# source path.env

Run
====
# python project/RebootTime.py --device-ip 10.26.25.116 --snmp-read comstr_ro1

When arguments not provided, the default value will be used.  For example, username/password will default to su/wwp.

Input Help
==========
# python project/RebootTime.py -h

Directories
============
project/: test project scripts.  Each script is a main entrance of each test project

pvauto/: shared library and APIs in a common place

test/: some internal unit test scripts, for internal use only

Logging
=======
logging.ini: configure logger
project.log.x: logging output file, rotate by 10M per file and total 5 files (configured via logging.ini)
