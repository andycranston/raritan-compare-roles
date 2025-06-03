# raritan-compare-roles - a utilty to compare the role definitions between two Raritan intelligent PDUs and report differences

The Python 3 program `compare-roles.py` gets the role definitions of all the roles defined on two
Raritan intelligent PDUs and compares them. Differences are then reported. One difference per line of output.

## Why is this useful?

When custom roles are defined on a Raritan PDU it is usual for the same roles to be defined on groups of similar PDUs "en mass".

This utility program can be used to ensure the roles are defined consistently in large sites where the number of deployed PDUs has scaled
into the hundreds or even thousands of units.

## Pre-requisites

You will need the following:

+ python3 installed - tested on Python version 3.12.3 but anything from 3.6.x onwards would probably be ok
+ the Raritan PDU JSON-RPC SDK (downloadable from www.raritan.com)
+ PYTHONPATH defined to include the location of the Python JSON-RPC SDK bindings directory

## Quick start

As an example say we have two PDUs with these details:

```
First PDU:
---------

IP address ...: 10.7.0.11
Username .....: admin
Password .....: Passw0rd!

Second PDU:
----------

IP address ...: 10.7.0.12
Username .....: admin
Password .....: Passw0rd!
```

`NOTE:` the password `Passw0rd!` is NOT a password used on any of MY
devices! It is simply a "place holder" for this README documentation. Also
do NOT be tempted to use it on any of YOUR devices/accounts!

With these details we can run the `compare_roles.py` utility program as follows:

```
python3 ./compare-roles.py  --host1 10.7.0.11 --user1 admin --pass1 'Passw0rd!' --host2 10.7.0.12 --user2 admin --pass2 'Passw0rd!'
```

Example output:

```
Role changeserial is defined on host 10.7.0.11 but not on host 10.7.0.12
Role outlets is defined on host 10.7.0.12 but not on host 10.7.0.11
Role Operator has privilege switchOutlet in host 10.7.0.12 but not in host 10.7.0.11
Descriptions for role reset on host 10.7.0.11 and host 10.7.0.12 are different ("some other desciption" versus "reset the PDU")
Role reset has privilege clearLog in host 10.7.0.11 but not in host 10.7.0.12
Role reset has privilege performReset in host 10.7.0.12 but not in host 10.7.0.11
```

So we can see there are a number of differences in role definitions between these two PDUs.

## A note on passwords

Supplying passwords on the command line is bad practice as commands are often stored in "history" files on disk. The `compare_roles.py`
utility program has a feature that lets the password be stored in an environment variable and the name of the environment variable
is passed to the `compare_roles.py` program.

For example first run:

```
read PW1
export PW1
clear
read PW2
export PW2
clear
```

In response to the read commands enter the password. The clear commands clear the screen to reduce the chance of someone
"looking over your shoulder" seeing the password.

With the two environment variables PW1 and PW2 now containing the passwords for each PDU we can run the `compare_roles.py`
program more securely with:

```
python3 ./compare-roles.py  --host1 10.7.0.11 --user1 admin --pass1 [PW1] --host2 10.7.0.12 --user2 admin --pass2 [PW2]
```

Note the special syntax for the password arguments: the environment variable inside the [ and ] brackets.

## Test coverage

The `compare_roles.py` utility program has currently not been exhaustively tested. In particular the author has not been able to test the
logic that compares, for example, a role that defines the "Switch Outlet" priviledge.

If you have two switched PDUs that you can safely experiment with could you please try the following:

```
create a role called "outlet" with description "outlet role" on two PDUs
enable the priviledge "Switch Outlet" on both PDUs
on the first PDU select a range of outlets
on the second PDU select a different range of outlets
```

Run the `compare_roles.py` program against those two PDUs. Please report any errors/faults/suggestions to:

```
andy [at] cranstonhub [dot] com
```

I will be grateful for all and any feedback.

----------------
End of README.md
