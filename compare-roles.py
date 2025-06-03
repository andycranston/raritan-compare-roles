#! /usr/bin/python3
#
# @(!--#) @(#) compare-roles.py, sversion 0.1.0, fversion 004, 01-june-2025
#
# compare roles between two Raritan inteligent PDUs
#

########################################################################

#
# imports
#

import sys
import os
import argparse

import raritan.rpc.devsettings
import raritan.rpc.usermgmt

########################################################################

#
# constants
#

########################################################################

def normalise_password(password):
    global progname

    newpassword = password

    if len(password) >= 3:
        if password[0] == '[':
            if password[-1] == ']':
                try:
                    newpassword = os.environ[password[1:-1]]
                except KeyError:
                    newpassword = password

    return newpassword

########################################################################

def get_role_names(role_proxy, hostname):
    global progname

    try:
        all_roles = role_proxy.getAllRoles()
    except raritan.rpc.HttpException:
        print('{}: unable to get role names for hostname "{}"'.format(progname, hostname), file=sys.stderr)
        sys.exit(1)

    role_names = []

    for role in all_roles:
        role_name = role.name.lower()

        role_names.append(role_name)

    return role_names

########################################################################

def role_in_roles(rolename, roles):
    for r in roles:
        if rolename.lower() == r.name.lower():
            return True

    return False

########################################################################

def locate_role(rolename, roles):
    global progname

    for r in roles:
        if rolename.lower() == r.name.lower():
            return r

    print('{}: unable to locate role "{}" role name in function locate_role()'.format(progname, rolename), file=sys.stderr)
    sys.exit(2)

########################################################################

def privilege_in_privileges(privname, rp):
    for p in rp:
        if privname == p.name:
            return True

    return False

########################################################################

def locate_privilege(privname, rp):
    global progname

    for p in rp:
        if privname == p.name:
            return p

    print('{}: unable to locate privilege "{}" priviledge name in function locate_privilege()'.format(progname, privname), file=sys.stderr)
    sys.exit(2)

########################################################################

def compare_args(args1, host1, args2, host2, privname):
    for arg in args1:
        if not (arg in args2):
            print('Privilege {} has argument {} in host {} but not in host {}'.format(privname, arg, host1, host2))

    for arg in args2:
        if not (arg in args1):
            print('Privilege {} has argument {} in host {} but not in host {}'.format(privname, arg, host2, host1))

    return

########################################################################

def compare_privileges(roleprivs1, host1, roleprivs2, host2, rolename):
    for rp in roleprivs1:
        if not privilege_in_privileges(rp.name, roleprivs2):
            print('Role {} has privilege {} in host {} but not in host {}'.format(rolename, rp.name, host1, host2))

    for rp in roleprivs2:
        if not privilege_in_privileges(rp.name, roleprivs1):
            print('Role {} has privilege {} in host {} but not in host {}'.format(rolename, rp.name, host2, host1))
    
    for rp in roleprivs1:
        if privilege_in_privileges(rp.name, roleprivs2):
            rp2 = locate_privilege(rp.name, roleprivs2)

            compare_args(rp.args, host1, rp2.args, host2, rp.name);

    return

########################################################################

def compare_roles(role_proxy1, host1, role_proxy2, host2, skipoperator):
    global progname

    try:
        all_roles1 = role_proxy1.getAllRoles()
    except raritan.rpc.HttpException:
        print('{}: unable to get role names for hostname "{}"'.format(progname, host1), file=sys.stderr)
        sys.exit(1)
    
    try:
        all_roles2 = role_proxy2.getAllRoles()
    except raritan.rpc.HttpException:
        print('{}: unable to get role names for hostname "{}"'.format(progname, host2), file=sys.stderr)
        sys.exit(1)

    for r in all_roles1:
        if skipoperator:
            if r.name.lower() == 'operator':
                continue

        if not role_in_roles(r.name, all_roles2):
            print('Role {} is defined on host {} but not on host {}'.format(r.name, host1, host2))

    for r in all_roles2:
        if skipoperator:
            if r.name.lower() == 'operator':
                continue

        if not role_in_roles(r.name, all_roles1):
            print('Role {} is defined on host {} but not on host {}'.format(r.name, host2, host1))

    for r in all_roles1:
        if skipoperator:
            if r.name.lower() == 'operator':
                continue

        if role_in_roles(r.name, all_roles2):
            ### print('Role {} is defined on host {} and on host {} - digging deeper'.format(r.name, host1, host2))

            r2 = locate_role(r.name, all_roles2)

            if r.info.description != r2.info.description:
                print('Descriptions for role {} on host {} and host {} are different ("{}" versus "{}")'.format(r.name, host1, host2, r.info.description, r2.info.description))
                #
                # do a case insensitve conpare and if that is equal then report a note
                #

            compare_privileges(r.info.privileges, host1, r2.info.privileges, host2, r.name)
        
    return

########################################################################

def main():
    global progname

    parser = argparse.ArgumentParser()

    parser.add_argument('--host1',     help='name/IP address of first PDU', required=True)
    parser.add_argument('--user1',     help='username to login as on first PDU', default='admin')
    parser.add_argument('--pass1',     help='password for user on first PDU', required=True)

    parser.add_argument('--host2',     help='name/IP address of second PDU', required=True)
    parser.add_argument('--user2',     help='username to login as on second PDU', default='admin')
    parser.add_argument('--pass2',     help='password for user on second PDU', required=True)

    parser.add_argument('--skipoper',  help='skip comparing the Operator role', action='store_true')

    args = parser.parse_args()

    host1 = args.host1
    host2 = args.host2

    user1 = args.user1
    user2 = args.user2

    pass1 = normalise_password(args.pass1)
    pass2 = normalise_password(args.pass2)

    if args.skipoper:
        skipoperator = True
    else:
        skipoperator = False

    ### print('First ....:', host1, user1, pass1)
    ### print('Second ...:', host2, user2, pass2)

    agent1 = raritan.rpc.Agent("https", host1, user1, pass1, disable_certificate_verification=True)
    agent2 = raritan.rpc.Agent("https", host2, user2, pass2, disable_certificate_verification=True) 

    role_proxy1 = raritan.rpc.usermgmt.RoleManager("/auth/role", agent1)
    role_proxy2 = raritan.rpc.usermgmt.RoleManager("/auth/role", agent2)

    ### role_names1 = get_role_names(role_proxy1, host1)
    ### role_names2 = get_role_names(role_proxy2, host2)

    ### print(role_names1)
    ### print(role_names2)

    compare_roles(role_proxy1, host1, role_proxy2, host2, skipoperator)

    return 0

########################################################################

progname = os.path.basename(sys.argv[0])

sys.exit(main())

# end of file
