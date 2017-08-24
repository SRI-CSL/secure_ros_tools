#!/usr/bin/env python
# Software License Agreement (BSD License)
#
# Copyright (c) 2017, SRI International
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of Willow Garage, Inc. nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


import os
import stat
import subprocess
import logging
import shutil


def make_plainrsa_private( filename, bits=4096 ):
    """ Create RSA private key
    """
    cmd = "plainrsa-gen -b %d -f %s" % ( bits, filename )
    logging.info( "Executing: %s" % cmd )
    subprocess.call( cmd.split() )


def make_plainrsa_public( private_filename, public_filename ):
    """ Create RSA public key from private key
    """
    pub_found = False
    with open( private_filename, 'r' ) as f:
        for l in f.readlines():
            words = l.split()
            if len( words ) == 4:
                if words[2] == "PUB":
                    pub_found = True
                    with open( public_filename, 'w' ) as f2:
                        f2.write( ' '.join( '%s' % x for x in words[1:] ) )
                    break
    return pub_found


def make_keys( hostname, prefix, certs_folder = "etc/racoon/certs" ):
    """ Make RSA public and private keys for host
        The key file is composed from the hostname: <prefix>/<certs_folder>/<hostname>
    """
    private_file = os.path.join( prefix, certs_folder, hostname )
    if not os.path.exists( os.path.dirname( private_file ) ):
        os.makedirs( os.path.dirname( private_file ) )

    public_file = os.path.join( prefix, certs_folder, hostname + ".pub" )
    if not os.path.exists( os.path.dirname( public_file ) ):
        os.makedirs( os.path.dirname( public_file ) )

    if os.path.exists( private_file ):
        logging.info( "Using existing private key %s" % private_file )
    else:
        logging.info( "Writing private key to %s" % private_file )
        make_plainrsa_private( private_file )
    logging.info( "Writing public key to %s" % public_file )
    make_plainrsa_public( private_file, public_file )
    # change permissions on file
    os.chmod( private_file, stat.S_IRUSR | stat.S_IWUSR )
    return public_file


def copy_public_keys( hostname, prefix, prefix2, certs_folder = "etc/racoon/certs" ):
    """ Copy public keys from one host to all other hosts
    """
    src = os.path.join( prefix, certs_folder, hostname + ".pub" )
    dst = os.path.join( prefix2, certs_folder, hostname + ".pub" )
    logging.info( "Copying %s -> %s" % ( src, dst ) )
    shutil.copy2( src, dst )


def make_racoon_header( file_obj ):
    """ Create racoon configuration file header
    """
    file_obj.write( '# Racoon IKE daemon configuration file.\n#\n' )
    file_obj.write( 'log notify;\n' )
    file_obj.write( 'path certificate "/etc/racoon/certs";\n\n' )


def make_racoon_remote( file_obj, host_ip, host_name, peer_ip, peer_name ):
    """ Create racoon configuration file remote component
    """
    file_obj.write( 'remote %s\n{\n' % peer_ip )
    file_obj.write( '  exchange_mode main;\n' )
    file_obj.write( '  lifetime time 12 hour;\n' )
    file_obj.write( '  certificate_type plain_rsa "%s";\n' % host_name )
    file_obj.write( '  peers_certfile plain_rsa "%s.pub";\n' % peer_name )
    file_obj.write( '  verify_cert off;\n' )
    file_obj.write( '  proposal {\n' )
    file_obj.write( '    encryption_algorithm 3des;\n' )
    file_obj.write( '    hash_algorithm sha256;\n' )
    file_obj.write( '    authentication_method rsasig;\n' )
    file_obj.write( '    dh_group modp1024;\n' )
    file_obj.write( '  }\n' )
    file_obj.write( '  generate_policy off;\n' )
    file_obj.write( '}\n\n' )



def make_racoon_sainfo( file_obj ):
    """ Create racoon.conf sainfo component
    """
    file_obj.write( 'sainfo anonymous\n' )
    file_obj.write( '{\n' )
    file_obj.write( '	pfs_group modp1024;\n' )
    file_obj.write( '	encryption_algorithm 3des;\n' )
    file_obj.write( '	authentication_algorithm hmac_sha256;\n' )
    file_obj.write( '	compression_algorithm deflate;\n' )
    file_obj.write( '}\n' )



def make_setkey_header( file_obj ):
    """ Create ipsec-tools.conf file header
    """
    file_obj.write( '#!/usr/sbin/setkey -f\n#\n\n' )
    file_obj.write( 'flush;\n' )
    file_obj.write( 'spdflush;\n\n' )



def make_setkey_spd( file_obj, host_ip, peer_ip, val ):
    """ Create ipsec-tools.conf file spd component
    """
    file_obj.write( 'spdadd %s %s any -P %s ipsec\n' % ( host_ip, peer_ip, val ) )
    file_obj.write( '\tesp/transport//require\n' )
    file_obj.write( '\tah/transport//require;\n\n' )



def make_racoon_conf( filename, host, ip_addresses ):
    """ Make racoon.conf file for host
        Note that the key is expected to be named as {hostname} and {hostname}.pub
        filename: configuration filename 
        host: hostname 
        ip_addresses: dict{ hostname: ip_address } 
    """
    if not os.path.exists( os.path.dirname( filename ) ): 
        os.makedirs( os.path.dirname( filename ) )
    peers = set( ip_addresses.keys() ) - set( [host] )
    with open( filename, "w" ) as f:
        make_racoon_header( f )
        for peer in peers:
            make_racoon_remote( f, ip_addresses[host], host, ip_addresses[peer], peer )
        make_racoon_sainfo( f )



def make_setkey_conf( filename, host, ip_addresses ):
  """ Make ipsec-tools.conf file for host
      Note that the key is expected to be named as {hostname} and {hostname}.pub
      filename: configuration filename 
      host: hostname 
      ip_addresses: dict{ hostname: ip_address } 
  """
  if not os.path.exists( os.path.dirname( filename ) ): 
      os.makedirs( os.path.dirname( filename ) )
  peers = set( ip_addresses.keys() ) - set( [host] )
  with open( filename, "w" ) as f:
      make_setkey_header( f )
      for peer in peers:
          make_setkey_spd( f, ip_addresses[host], ip_addresses[peer], 'out' )
          make_setkey_spd( f, ip_addresses[peer], ip_addresses[host], 'in' )



def make_conf( host, ip_addresses, prefix ):
    """ Make racoon.conf and ipsec-tools.conf file
    """
    racoon_conf = '%s/etc/racoon/racoon.conf' % prefix
    logging.info( 'Writing to %s' % racoon_conf )
    make_racoon_conf( racoon_conf, host, ip_addresses )

    setkey_conf = '%s/etc/ipsec-tools.conf' % prefix
    logging.info( 'Writing to %s' % setkey_conf )
    make_setkey_conf( setkey_conf, host, ip_addresses )



