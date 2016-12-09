#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/01/25 21:56:45
#   Desc    :   core connection module to ssh or telnet to server
#

from config import *
import pexpect
import paramiko
from paramiko.ssh_exception import SSHException
import socket
from interactive import interactive_shell
from utils import Timeout

#Manager Class to manager connections
class Connection(object):
    """
    Core connection manager to remote control server through ssh and telnet,
    to excute command, run interactive shell, upload and download files.
    #connection = Connection("10.35.82.23", "root", "ysyhl9t")
    """
    prompt = ".*[#>%$\]] ?"
    def __init__(self, ipaddr, username, password):
        """
        initialize ip, username password.
        """
        self._ipaddr = ipaddr
        self._username = username
        self._password = password

    def ssh_client(self, disp = False):
        """
        create a SSHClient for ssh connection if ssh protocol
        return: ssh connection client for interactive
                None if not create successful
        """
        self.client = pexpect.spawn("ssh -o 'StrictHostKeyChecking no' %s -l %s" % \
                                     (self._ipaddr, self._username))
        if disp:
            self.client.logfile = sys.stdout
        else:
            self.client.logfile = None
        index = self.client.expect([".*assword:", pexpect.EOF, pexpect.TIMEOUT])
        if 0 != index:
            printd("%s: cannot ssh connect to server\n" % self._ipaddr)
            return None
        self.client.send(self._password + "\r")
        index = self.client.expect([self.prompt, pexpect.EOF, pexpect.TIMEOUT])
        if 0 != index:
            printd("%s: cannot create ssh client with credential\n" % self._ipaddr)
            return None
        return self.client

    def _execute_cmds(self, cmds):
        """
        Excute all the commands in cmds list through ssh or telnet
        parameter: commands in list.
        return: output string of all the commands
        """
        if not self.client:
            return
        std_output = ""
        for cmd in cmds:
            self.client.send(cmd + "\r")
            self.client.expect(self.prompt)
            printd("%s: execute commands: %s\n" % (self._ipaddr, cmd))
            cmd_output = self.client.after
            std_output += cmd_output
            printd(cmd_output)
        return std_output


    #def ssh_cmds(self, cmds):
    #    """
    #    Excute all the commands in cmds list through ssh
    #    parameter: commands in list.
    #    return: output string of all the commands
    #            None if some errors
    #    """
    #    self.ssh_client()
    #    try:
    #        std_output = self._execute_cmds(cmds)
    #    except:
    #        printd("%s: execute ssh commands not successful\n" % self._ipaddr)
    #        std_output = None
    #    finally:
    #        self.client.close()
    #        return std_output

    def ssh_cmds(self, cmds):
        """
        Excute all the commands in cmds list through ssh
        parameter: commands in list.
        return: output string of all the commands
                None if some errors
        """
        self.paramiko_ssh_client()
        if not self.p_client:
            return
        std_output = ""
        try:
            for cmd in cmds:
                stdin, stdout, stderr = self.p_client.exec_command(cmd)
                lines = stdout.readlines()
                ##
                #import pdb
                #pdb.set_trace()
                ##
                printd("%s: execute ssh commands: %s\n" % (self._ipaddr, cmd))
                for line in lines:
                    std_output += line
                    printd(line)
                ########
                # stderr for debug
                #err_lines = stderr.readlines()
                #for line in err_lines:
                #    std_output += line
                #    printd(line)
                ########
        except (SSHException, socket.error) as ex:
            printd("%s: execute ssh commands not successful: %s\n" % \
                    (self._ipaddr, ex.message))
            std_output = None
        finally:
            self.p_client.close()
            return std_output

    def telnet_client(self, disp = False):
        """
        create a telnet client to run commands after prompt
        return: a telnet client
                None if some issue
        """
        #object field
        self.client = pexpect.spawn("telnet %s" % self._ipaddr)
        if disp:
            self.client.logfile = sys.stdout
        else:
            self.client.logfile = None
        index = self.client.expect([".*ogin:", "refused$", pexpect.TIMEOUT, pexpect.EOF])
        if index != 0:
            printd("%s: cannot telnet connect to server\n" % self._ipaddr)
            return None
        self.client.send(self._username + "\r")
        self.client.expect(r".*assword:.*")
        self.client.send(self._password + "\r")
        index = self.client.expect([self.prompt, r".*invalid.*", pexpect.TIMEOUT])
        if index != 0:
            printd("%s: cannot create telnet client with credential\n" % self._ipaddr)
            return None
        return self.client

    def telnet_cmds(self, cmds):
        """
        Excute all the commands in cmds list through telnet
        parameter: commands in list.
        return: output string of all the commands
                None if some errors
        """
        self.telnet_client()
        try:
            std_output = self._execute_cmds(cmds)
        except:
            printd("%s: execute telnet commands not successful\n" % self._ipaddr)
            std_output = None
        finally:
            self.client.close()
            return std_output

    def paramiko_ssh_client(self):
        """
        create a paramiko SSHClient for ssh connection 
        return: SSHClient, None if not create successfully
        """
        try:
            self.p_client = paramiko.SSHClient()
            self.p_client.load_system_host_keys()
            self.p_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#for thread comment out
            #with Timeout(12):
#for thread: intend <<
            self.p_client.connect(self._ipaddr, 22, self._username, self._password, timeout=10, banner_timeout=10)
########## comment below
            #printd("paramiko ssh client created successfully\n")
##########
        except (SSHException, socket.error, Timeout.Timeout) as ex:
            printd("%s: paramiko ssh client create not successful: %s\n" % \
                   (self._ipaddr, ex.message))
            self.p_client = None
        finally:
            return self.p_client

    def ssh_download_file(self, remote_file, local_file):
        """
        download file from remote server through sftp
        parameter: remote_file - the remote file path
                   local_file - the local file path
        return: True, None if some error
        #ssh_download_file testing
        connection.ssh_download_file("/root/update_motd", "/home/yuejd/update_motd")
        """
        self.paramiko_ssh_client()
        if not self.p_client:
            return
        try:
            sftp_client = self.p_client.open_sftp()
            sftp_client.get(remote_file, local_file)
            printd("%s: file %s download to %s completely\n" % (self._ipaddr, remote_file, local_file))
            return True
        except (SSHException, socket.error) as ex:
            printd("%s: file download not successful: %s\n" % \
                    (self._ipaddr, ex.message))
            return
        finally:
            self.p_client_close()

    #upload file to remote server through sftp
    def ssh_upload_file(self, local_file, remote_file):
        """
        #ssh_upload_file testing
        parameter: remote_file - the remote file path
                   local_file - the local file path
        return: True, None if some error
        connection.ssh_upload_file("/home/yuejd/update_motd", "/tmp/update_motd")
        """
        #printd("ssh upload file to server:%s\n" % self._ipaddr)
        self.paramiko_ssh_client()
        if not self.p_client:
            return
        try:
            sftp_client = self.p_client.open_sftp()
            sftp_client.put(local_file, remote_file)
            printd("%s: file %s upload to %s completely\n" % (self._ipaddr, local_file, remote_file))
            return True
        except (SSHException, socket.error) as ex:
            printd("%s: file upload not successful: %s\n" % \
                    (self._ipaddr, ex.message))
            return
        finally:
            self.p_client.close()

    def ssh_interact_shell(self):
        """
        create an interactive shell,
        return: None if some error
        # ssh_interact_shell testing
        connection.ssh_interact_shell()
        """
        self.paramiko_ssh_client()
        if not self.p_client:
            return
        try:
            chan = self.p_client.invoke_shell()
            printd("%s: interactive shell create \n" % self._ipaddr)
            interactive_shell(chan)
        except:
            self.p_client.close()

    #close client
    def close(self):
        """
        close ssh or telnet client
        """
        try:
            self.client.close()
        except:
            pass

if __name__ == "__main__":
    printd("run moudle, testing below.\n")
    #connection = Connection("10.108.104.124", "lin", "password")
    #print connection.ssh_cmds(["switchshow"])
    #connection = Connection("127.0.0.1", "yuejd", "yue123")
    #connection.ssh_interact_shell()
    #connection.ssh_upload_file("/home/yuejd/Develop/python/emc/nwc2/lib/config.py", "/tmp/config.py")
    #ssh_cmds testing
    #output = connection.ssh_cmds(["pwd", "ls -l", "cd /dev", "ls"])
    #print output
    connection = Connection("10.103.118.119", "root", "dangerous")
    connection.ssh_cmds(["/usr/contrib/bin/machinfo"])
