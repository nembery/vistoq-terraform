#!/usr/bin/env python3
#
# pexpect script to configure a freshly installed panorama instance in a public cloud
#
# nembery@paloaltonetworks.com  09/25/18
#
# This tool expects to find the following environment variables:
#
#   TF_VAR_sshkeyfile   :   path to the private ssh key of the user that was used to configure panorama in the cloud
#                               default: ~/.ssh/id_rsa
#   PANORAMA_PASSWORD   :   Password that will be used to for the admin AND api-admin users
#                                default: Clouds123
#   PANORAMA_IP         :   IPv4 Address of the Panorama instance to configure
#                                 default: None, will exit is not found
#   PANORAMA_HOSTNAME   :   Hostname to set the panorma server
#                                 default: vistoq-panorama
#

import pexpect
import os
import sys

# check env for PANORAMA_IP variable
panorama_ip = os.environ.get('PANORAMA_IP', '')
panorama_hostname = os.environ.get('PANORAMA_HOSTNAME', 'vistoq-panorama')

if panorama_ip == '':
    # panorama ip was not set on env, check local file from terraform build script
    panorama_ip_file_path = '/var/tmp/vistoq_panorama_ip.txt'
    if not os.path.exists(panorama_ip_file_path):
        print('Could not locate panorama ip configuration file at %s' % panorama_ip_file_path)
        sys.exit(1)

    try:
        with open(panorama_ip_file_path, 'r') as pipf:
            panorama_ip = pipf.read()
    except IOError as ioe:
        print('Could not open panorama_ip local file!')
        print(ioe)
        sys.exit(1)

# quick sanity check on ip address format
if not len(panorama_ip.split('.')) == 4:
    print('This does not look like an IPv4 Address ?')
    sys.exit(1)

print('Getting configuration values from environment')
# attempt to get values from the ENV, otherwise use 'get' with defaults
pw = os.environ.get('PANORAMA_PASSWORD', 'Clouds123')
sshkey = os.environ.get('TF_VAR_sshkeyfile', '~/.ssh/id_rsa')
sshkeypub = f'{sshkey}.pub'

print('Generating base64 encoded key for panorama')
encoded_ssh_key = os.popen(f'cat {sshkeypub} | base64').read()
print(encoded_ssh_key)

print('Running SSH command to newly created panorama')
cmd = f'ssh -i {sshkey} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no admin@{panorama_ip}'
print(cmd)

print('Connecting to panorama')
child = pexpect.spawn(cmd)
child.setecho(False)
child.sendline()
index = child.expect(['admin@Panorama>', 'Password', pexpect.EOF, pexpect.TIMEOUT])
if index != 0:
    print('Could not log in using provided SSH Key!')
    print(child.before)
    sys.exit(1)

# we are assuming that we've logged in successfully if we've gotten to this point
print('Login successful')
# this is what we'll see if using the raw CLI
# admin@Panorama# set mgt-config users admin password
# Enter password   :
# Confirm password :
child.sendline('configure')
child.expect('admin@Panorama#')
print('Found configure prompt')
print('Setting admin password')
child.sendline('set mgt-config users admin password')
child.expect('Enter password')
print(f'sending password #1 {pw}')
child.sendline(pw)
child.expect('Confirm password')
print(f'sending password #2 {pw}')
child.sendline(pw)
child.expect('admin@Panorama#')
print('Setting admin ssh key in correct format')
child.sendline(f'set mgt-config users admin public-key {encoded_ssh_key}')
child.expect('admin@Panorama#')
print('Creating api-admin user')
child.sendline('set mgt-config users api-admin permissions role-based panorama-admin yes')
child.expect('admin@Panorama#')
child.sendline()
child.expect('admin@Panorama#')
print('Setting api-user password')
child.sendline('set mgt-config users api-admin password')
child.expect('Enter password')
print(f'sending password #1 {pw}')
child.sendline(pw)
child.expect('Confirm password')
print(f'sending password #2 {pw}')
child.sendline(pw)
child.expect('admin@Panorama#')
child.sendline('set deviceconfig system dns-setting servers primary 8.8.8.8 secondary 1.1.1.1')
child.expect('admin@Panorama#')
child.sendline()
child.expect('admin@Panorama#')
child.sendline(f'set deviceconfig system hostname {panorama_hostname}')
print('Committing configuration')
child.sendline('commit')
print('Exiting config mode')
child.expect('admin@.*#')
child.sendline('exit')
print('Exiting...')
child.expect('admin@.*>')
child.sendline('exit')
print('All Good!')

