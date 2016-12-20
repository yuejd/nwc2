#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   Jiadi Yue
#   E-mail  :   jiadi.yue@emc.com
#   Date    :   15/01/26 10:13:46
#   Desc    :   nwc_lib to get server information
#

from core_connect import Connection
from config import *
from utils import trans_wwn
import re

def get_linux_wwn(ipaddr, username, password):
    """
    get linux server wwn/symbolic/port_state
    parameter: ip address, username, password
    return: a list with wwn/symbolic/port_state
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        for card in /sys/class/fc_host/host*; do
             tail_name=$(basename ${card})
             for info in {port_name,symbolic_name,port_state} ; do
                 [[ ${info} == "symbolic_name" && ! -r ${card}/${info} ]] && { echo -n "$(cat /sys/class/scsi_host/${tail_name}/info)@#$"  ; continue ; }
                 [[ -r ${card}/${info} ]] && echo -n "$(cat ${card}/${info})@#$"
             done
             echo
         done
         """])
    if output:
        wwns = output.strip().splitlines()
        wwn_info_list = []
        for info in wwns:
            info_list = info.split(Division)[0:-1]
            info_list[0] = trans_wwn(info_list[0])
            wwn_info_list.append(info_list)
        return wwn_info_list
    else:
        #printd("%s: not get wwns\n" % ipaddr)
        return None

def get_solaris_wwn(ipaddr, username, password):
    """
    get solaris server wwn/manufacturer/port_state
    parameter: ip address, username, password
    return: a list with wwn/manufacturer/port_state
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds([""" fcinfo hba-port | egrep "HBA Port|Manufacturer|State" """])
    if output:
        lines = output.strip().splitlines()
        lines = [line.split(": ")[-1] for line in lines]
        wwns = zip([trans_wwn(line) for line in lines[::3]], lines[1::3], lines[2::3])
        return wwns
    else:
        #printd("%s: not get wwns\n" % ipaddr)
        return None

def get_vmware_wwn(ipaddr, username, password):
    """
    get vmware server wwn/manufacturer/port_state
    parameter: ip address, username, password
    return: a list with wwn/manufacturer/port_state
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        esxcfg-scsidevs -a | grep fc[\.][0-9] | awk '{printf("%s@#$",substr($4,21));for(i=6;i<NF;i++) printf("%s ",$i); printf("@#$%s",$3);print ""}' 
        """])
    if output:
        lines = output.strip().splitlines()
        wwns = []
        for info in lines:
            info_list = info.strip().split(Division)
            info_list[0] = trans_wwn(info_list[0])
            wwns.append(info_list)
        return wwns
    else:
        #printd("%s: not get wwns\n" % ipaddr)
        return None

def get_hpux_wwn(ipaddr, username, password):
    """
    get hpux server wwn/manufacturer/port_state
    parameter: ip address, username, password
    return: a list with wwn/manufacturer/port_state
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        i=0;while ((i<15));do /opt/fcms/bin/fcmsutil /dev/fcd$i 2>/dev/null | grep -E "rt Port World|Local N_Port_id|Driver state" | cut -d = -f 2; i=$(($i+1)); done; i=0;while ((i<15));do /opt/fcms/bin/fcmsutil /dev/fclp$i 2>/dev/null | grep -E "rt Port World|Local N_Port_id|Driver state" | cut -d = -f 2; i=$(($i+1)); done; i=0;while ((i<15));do /opt/fcms/bin/fcmsutil /dev/fcoc$i 2>/dev/null | grep -E "rt Port World|Local N_Port_id|Driver state" | cut -d = -f 2; i=$(($i+1)); done;
        """])
    #no manufacturer
    if output:
        lines = output.strip().splitlines()
        wwns_lines = []
        for line in lines:
            wwns_lines.append(trans_wwn(line.strip()))
        wwns = zip(wwns_lines[1::3], wwns_lines[::3], wwns_lines[2::3])
        return wwns
    else:
        #printd("%s: not get wwns\n" % ipaddr)
        return None

def get_aix_wwn(ipaddr, username, password):
    """
    get aix server wwn/manufacturer/port_state
    parameter: ip address, username, password
    return: a list with wwn/manufacturer/port_state
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        for i in `lsdev -Cc adapter -S a | grep fcs | grep Available | cut -d " " -f 1`; do echo $(lscfg -vpl $i | grep "Network" | awk -F. '{print $NF}')'@#$'$(lscfg -vpl $i | grep "Model" | cut -d : -f 2)'@#$online'; done
        """])
    #no manufacturer
    if output:
        lines = output.strip().splitlines()
        wwns = []
        for line in lines:
            wwns.append([trans_wwn(info.strip()) for info in line.split(Division)])
        return wwns
    else:
        #printd("%s: not get wwns\n" % ipaddr)
        return None


def get_linux_info(ipaddr, username, password):
    """
    get linux server information include server vender/server model/CPU/memory/OS
    parameter: ip address, username, password
    return: a list with vender/server model/CPU/memory/OS
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        echo -n "$(dmidecode -t system | grep Manufacturer | awk -F:    '{print $2 }')@#$"
        echo -n "$(dmidecode -t system | grep "Product Name" |  awk -F: '{print $2}')@#$"
        echo -n "$(cat /proc/cpuinfo  | grep "model name" | head -1 | awk -F: '{print $2}'| sed "s/ /_/g")@#$"
        echo -n "$(cat /proc/meminfo  | grep MemTotal | awk -F: '{print $2}')@#$"
        lsb_release -a | grep Description |awk -F: '{print $2}'
         """])
    #for lsb_release, not default installed to all dev 
    if output:
        info_list = [info.strip() for info in output.split(Division)]
        return info_list
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None

def get_solaris_info(ipaddr, username, password):
    """
    get solaris server information include server vender/server model/CPU/memory/OS
    parameter: ip address, username, password
    return: a list with vender/server model/CPU/memory/OS
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        echo -n "$(prtconf  |  grep "System Configuration" | awk -F: '{print $2}')@#$" 
        `uname -p` == "sparc" && echo -n "$(uname -i)@#$"  ||  echo -n "$( prtdiag | grep "System Configuration"  | awk -F: '{print $2}')@#$"
        `uname -p` == "sparc" &&  echo -n "@#$"  ||  echo -n "$(prtdiag  | grep CPU)@#$"
        echo -n "$(prtconf  | grep "Memory size"  | awk -F: '{print $2}')@#$"
        echo  "$(uname -srp)"
        """])
    if output:
        info_list = [info.strip() for info in output.split(Division)]
        return info_list
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None

def get_vmware_info(ipaddr, username, password):
    """
    get vmware server information include server vender/server model/CPU/memory/OS
    parameter: ip address, username, password
    return: a list with vender/server model/CPU/memory/OS
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""esxcfg-info > /tmp/host_info""",
        """echo -n "@#$";echo -n "$( grep "Product Name" /tmp/host_info | sed 's/\.\+/ /' | awk '{for ( i= 3; i <= NF ; i++)  printf ("%s ",$i) }')@#$";echo -n "$( vim-cmd hostsvc/hosthardware | grep description | head -1 | awk -F= '{print $2}' | sed 's/ \+/ /g')@#$";echo -n "$( grep "Total Memory" /tmp/host_info  | head -1 | sed 's/\.\+/ /' | awk '{ print $3,$4 }')@#$";echo "$(vmware -v)"
        """])
        #no vender info
    if output:
        info_list = [info.strip() for info in output.split(Division)]
        return info_list
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None

def get_hpux_info(ipaddr, username, password):
    """
    get hpux server information include server vender/server model/CPU/memory/OS
    parameter: ip address, username, password
    return: a list with vender/server model/CPU/memory/OS
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds([""" 
        echo  "***@#$"
        echo "$(model)@#$"
        echo "$(/usr/contrib/bin/machinfo | sed -n '2p')@#$"
        echo "$(/usr/contrib/bin/machinfo | grep Memory | cut -d : -f 2)@#$"
        /usr/contrib/bin/machinfo | grep Release | cut -d : -f 2
        """])
        #no vender info
    if output:
        info_list = [info.strip() for info in output.split(Division)]
        return info_list
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None

def get_aix_info(ipaddr, username, password):
    """
    get aix server information include server vender/server model/CPU/memory/OS
    parameter: ip address, username, password
    return: a list with vender/server model/CPU/memory/OS
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds([""" 
        echo '***@#$'$(uname -Mu)'@#$'$(lsattr -El proc0 | grep type | awk '{print $2}')'@#$'$(bootinfo -r)'Kb@#$'$(oslevel)
        """])
        #no vender info
    if output:
        info_list = [info.strip() for info in output.split(Division)]
        return info_list
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None


#def get_brocade_name(ipaddr, username, password):
#    """
#    get brocade switch information include fabric id/model
#    parameter: ip address, username, password
#    return: a list with fabric id/model
#            None if not get
#    """
#    con = Connection(ipaddr, username, password)
#    output = con.ssh_cmds(["""switchname"""])
#    if output:
#        return output
#    else:
#        #printd("%s: not get info\n" % ipaddr)
#        return None
def get_brocade_info(ipaddr, username, password):
    """
    get brocade switch information include switchname/fabric id/wwns
    parameter: ip address, username, password
    return: a list with switchname/fabric id/wwns
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        switchname;echo "@#$"; switchshow | grep "FID:"; echo "@#$"; switchshow | grep Online | grep -v "switchState"; echo "@#$"; fcoe --loginshow
        """])
    if output:
        switchname, fid, wwns, fcoe_wwns = [t.strip() for t in output.split(Division)]
        if fid:
            fid = fid.split("FID: ")[1].split(",")[0]
        t_wwns = []
        if wwns:
            for line in wwns.splitlines():
                if "FCoE" in line:
                    continue
                port_index = line.split()[0] 
                m = re.search(r" (\w{2}:){7}\w{2}", line)
                if m:
                    t_wwns.append([port_index, "FC", "fid"+fid, m.group().strip()])
        if fcoe_wwns:
            for line in fcoe_wwns.splitlines():
                port_index = line.split()[0]
                m = re.search(r" (\w{2}:){7}\w{2}", line)
                if m:
                    t_wwns.append([port_index, "FCoE", "fid"+fid, m.group().strip()])
        return switchname, fid, t_wwns
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None

def get_cisco_info(ipaddr, username, password):
    """
    get cisco switch information include switchname/vsan id/wwns
    parameter: ip address, username, password
    return: a list with switchname/vsan id/wwns
            None if not get
    """
    con = Connection(ipaddr, username, password)
    output = con.ssh_cmds(["""
        terminal length 0 ; show switchname ; echo "@#$" ; show flogi database | grep fc
        """])
    if output:
        switchname, wwns = output.split(Division)
        t_wwns = []
        for line in wwns.strip().splitlines():
            t_line = line.split()
            t_wwns.append([t_line[0], None, "vsan"+t_line[1], t_line[3]])
        return switchname, None, t_wwns
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None

def nodefind_brc(ipaddr, username, password, wwns):
    """
    nodefind in brocade
    parameter: ip address, username, password
               wwns: a list of wwn need to be found
    return: a list of status for each wwn
            [[switchid, port, fabric]...]
    """
    con = Connection(ipaddr, username, password)
    wwns_for_cmd = " ".join(wwns)
    cmds = """configshow | grep "Fabric ID"; echo "@#$+@#$"; for i in """ + wwns_for_cmd + """; do nodefind $i | grep -E "$i|Index" | grep -v "Port Name"; echo '@#$'; done"""
    output = con.ssh_cmds([cmds])
    if output:
        fid_info, wwns_info = output.strip()[:-3].split(Division + "+" + Division)
        fid = "fid"+fid_info.split("=")[-1].strip() if fid_info.strip() else None
        wwn_status = []
        switchid_for_cmds = []
        wwn_info_list = wwns_info.strip().split(Division)
        for wwn_info in wwn_info_list:
            if wwn_info.strip():
                wwn_tmp = wwn_info.strip().split()
                switchid = "fffc" + wwn_tmp[1][0:2]
                wwn_status.append([switchid, wwn_tmp[-1], fid])
                switchid_for_cmds.append(switchid)
            else:
                wwn_status.append(None)
                switchid_for_cmds.append("alsdkfjalskdfj")
        sw_ids = " ".join(switchid_for_cmds)
        cmds = """for i in """ + sw_ids + """; do fabricshow | grep $i; echo "@#$"; done"""
        output = con.ssh_cmds([cmds])
        if output:
            switch_id_lines = output.strip()[:-3].split(Division)
            switch_ids = [l.strip().split()[3] if l.strip() else None for l in switch_id_lines]
            for i in xrange(len(switch_ids)):
                if wwn_status[i]:
                    wwn_status[i][0] = switch_ids[i]
        return wwn_status
    else:
        return None

def nodefind_cis(ipaddr, username, password, wwns):
    """
    nodefind in cisco
    parameter: ip address, username, password
               wwns: a list of wwn need to be found
    return: a list of status for each wwn
            [[ip, port, fabric]...]
    """
    con = Connection(ipaddr, username, password)
    pre_cmd = """echo "@#$" ; show fcns database detail | grep -A 14 -B 2 "port-wwn (vendor)           :"""
    post_cmd = """" | egrep "VSAN|nterface|IP"; """
    cmds = map(lambda x: pre_cmd + x + post_cmd, wwns)
    output = con.ssh_cmds(cmds)
    if output:
        wwns_info_list = output.strip()[3:].split(Division)
        wwn_status = []
        for wwn_info in wwns_info_list:
            if wwn_info.strip():
                wwn_tmp = wwn_info.strip().splitlines()
                fabric = "vsan" + wwn_tmp[0].split()[0].split(":")[1]
                #port = wwn_tmp[2].split(":")[-1].split()[-1].strip("()")
                #sw_ip = wwn_tmp[1].split(":")[-1]
                if len(wwn_tmp) < 3:
                    sw_ip = None
                else:
                    sw_ip = wwn_tmp[2].split(":")[-1].split()[-1].strip("()")
                port = wwn_tmp[1].split(":")[-1]
                wwn_status.append([sw_ip, port, fabric])
            else:
                wwn_status.append(None)
        return wwn_status
    else:
        #printd("%s: not get info\n" % ipaddr)
        return None

def del_zone_brc(ipaddr, username, password, zonename, fabric, fid):
    """
    delete zone in brocade
    parameter: ip address, username, password, zonename, fabric
    return: a list of status for zone delete
            [True/False, "logs"]
    """
    con = Connection(ipaddr, username, password)
    cmd1 = 'cfgremove ' + fabric + ', ' + zonename + '; zonedelete ' + zonename + '; echo y | cfgsave; echo y | cfgenable ' + fabric
    cmd2 = "zoneshow " + zonename
    output = con.ssh_cmds([cmd1, cmd2])
    if output:
        if "does not exist" in output:
            return [True, output]
        else:
            return [False, output]
    else: 
        return None

def zone_brc(ipaddr, username, password, zonename, wwns, fabric, fid):
    """
    zone in brocade
    parameter: ip address, username, password, zonename, wwns, fabric
               wwns: a list of wwn need to be zone
    return: a list of status for zone
            [True/False, "logs"]
    """
    def zone_ext_brc(ipaddr, username, password, zonename):
        con = Connection(ipaddr, username, password)
        cmd = "zoneshow " + zonename
        output = con.ssh_cmds([cmd])
        if output:
            if "does not exist" in output:
                return [True, "zone does not exist"]
            else: 
                return [False, "exist: " + output]
        else:
            return None
    output = zone_ext_brc(ipaddr, username, password, zonename)
    if output:
        if output[0]:
            con = Connection(ipaddr, username, password)
            cmd1 = 'zonecreate ' + zonename + ', "' + ";".join(wwns) + '"; cfgadd ' + fabric + ", " + zonename + "; echo y | cfgsave; echo y | cfgenable " + fabric 
            cmd2 = "cfgactvshow | grep " + zonename
            output1 = con.ssh_cmds((cmd1, cmd2))
            if output1:
                #return output1
                if 'zone:\t' + zonename + '\t\n' in output1:
                    return [True, output1]
                else: 
                    return [False, output1]
            else:
                return None
        else:
            return output
    else:
        return None

def del_zone_cis(ipaddr, username, password, zonename, fabric, vsan):
    """
    delete zone in cisco
    parameter: ip address, username, password, zonename, fabric, vsan
    return: a list of status for zone delete
            [True/False, "logs"]
    """
    con = Connection(ipaddr, username, password)
    cmd1 = 'config t ; zoneset name ' + fabric + ' vsan ' + vsan + ' ; no member ' + zonename + ' ; exit ; zoneset activate name ' + fabric + ' vsan ' + vsan + ' ; no zone name ' + zonename + ' vsan ' + vsan + ' ; zone commit vsan ' + vsan + ' ; copy running-config startup-config ; exit'
    cmd2 = "show zone name " + zonename + " vsan " + vsan
    output = con.ssh_cmds([cmd1, cmd2])
    if output:
        if "Zone not present" in output:
            return [True, output]
        else:
            return [False, output]
    else: 
        return None

def zone_cis(ipaddr, username, password, zonename, wwns, fabric, vsan):
    """
    zone in cisco
    parameter: ip address, username, password, zonename, wwns, fabric, vsan
               wwns: a list of wwn need to be zone
    return: a list of status for zone
            [True/False, "logs"]
    """
    def zone_ext_cis(ipaddr, username, password, zonename, vsan):
        con = Connection(ipaddr, username, password)
        cmd = "show zone name " + zonename + " vsan " + vsan
        output = con.ssh_cmds([cmd])
        if output:
            if "Zone not present" in output:
                return [True, "zone does not exist"]
            else: 
                return [False, "exist: " + output]
        else:
            return None
    output = zone_ext_cis(ipaddr, username, password, zonename, vsan)
    if output:
        if output[0]:
            con = Connection(ipaddr, username, password)
            cmd1 = 'config t ; zone name ' + zonename + ' vsan ' + vsan + ' ; member pwwn ' + ' ; member pwwn '.join(wwns) + ' ; exit ; zoneset name ' + fabric + ' vsan ' + vsan + ' ; member ' + zonename + ' ; exit ; zoneset activate name ' + fabric + ' vsan ' + vsan + ' ; zone commit vsan ' + vsan + ' ; copy running-config startup-config ; exit' 
            cmd2 = 'show zone active vsan ' + vsan + ' | grep ' + zonename
            output1 = con.ssh_cmds((cmd1, cmd2))
            if output1:
                #return output1
                if 'zone name ' + zonename + ' vsan ' + vsan in output1:
                    return [True, output1]
                else: 
                    return [False, output1]
            else:
                return None
        else:
            return output
    else:
        return None

def zone_search_brc(ipaddr, username, password, keyword, vsan):
    """
    zone keyword search in brocade
    parameter: ip address, username, password, keyword, vsan
    return: a list of zone with keyword
            [[zonename, activateORnot, [wwn1, wwn2, ...], ...]
            []
            None
    """
    con = Connection(ipaddr, username, password)
    cmd = 'cfgactvshow | grep "zone:" | grep "' + keyword + '"; echo "@#$"; zoneshow | grep "zone:" | grep "' + keyword + '"'
    output = con.ssh_cmds([cmd])
    zone_info_list = []
    if output:
        act_zones, zones = output.split("@#$\n")
        if act_zones:
            act_zones = act_zones.splitlines()
            for i in xrange(len(act_zones)):
                act_zones[i] = act_zones[i].split('\t')[1]
        else:
            act_zones = []
        if zones:
            zones = zones.splitlines()
            for i in xrange(len(zones)):
                zones[i] = zones[i].split('\t')[1]
        else:
            zones = []
            return []
        for zonename in act_zones:
            zone_info_list.append([zonename, "yes"])
        for zonename in zones:
            if zonename not in act_zones:
                zone_info_list.append([zonename, "no"])
            else:
                continue

        con = Connection(ipaddr, username, password)
        #cmd = "zoneshow " + "; zoneshow ".join([zone_info_list[i][0] for i in xrange(len(zone_info_list))])
        cmd = "zoneshow *" + keyword + "*"
        output = con.ssh_cmds([cmd])
        if output:
            zone_wwns = output.strip().split("\n zon")
            for i in xrange(len(zone_info_list)):
                for zone_wwn in zone_wwns:
                    if "\t"+zone_info_list[i][0]+"\t" in zone_wwn:
                        wwns = zone_wwn.split("\t"+zone_info_list[i][0]+"\t")[-1].split(";")
                        wwns = [wwns[j].strip() for j in xrange(len(wwns))]
                        zone_info_list[i].append(wwns)
                    else:
                        continue
            return zone_info_list
        else:
            return None
    else:
        return None

def zone_search_cis(ipaddr, username, password, keyword, vsan):
    """
    zone keyword search in cisco
    parameter: ip address, username, password, keyword, vsan
    return: a list of zone with keyword
            [[zonename, activateORnot, [wwn1, wwn2, ...], ...]
            []
            None
    """
    con = Connection(ipaddr, username, password)
    cmd = 'show zone active vsan ' + vsan + ' | grep "zone name" | grep "' + keyword + '" ; echo "@#$" ; show zone vsan ' + vsan + ' | grep "zone name" | grep "' + keyword + '"'
    output = con.ssh_cmds([cmd])
    zone_info_list = []
    if output:
        act_zones, zones = output.split("@#$\n")
        if act_zones:
            act_zones = act_zones.splitlines()
            for i in xrange(len(act_zones)):
                act_zones[i] = act_zones[i].split()[2]
        else:
            act_zones = []
        if zones:
            zones = zones.splitlines()
            for i in xrange(len(zones)):
                zones[i] = zones[i].split()[2]
        else:
            zones = []
            return []
        for zonename in act_zones:
            zone_info_list.append([zonename, "yes"])
        for zonename in zones:
            if zonename not in act_zones:
                zone_info_list.append([zonename, "no"])
            else:
                continue

        con = Connection(ipaddr, username, password)
        join_str = " vsan " + vsan + " ; show zone name "
        cmd = "show zone name " + join_str.join([zone_info_list[i][0] for i in xrange(len(zone_info_list))])
        output = con.ssh_cmds([cmd])
        if output:
            zone_wwns = output.strip().split("\nzone")
            for i in xrange(len(zone_info_list)):
                for zone_wwn in zone_wwns:
                    if " "+zone_info_list[i][0]+" " in zone_wwn:
                        wwns = zone_wwn.split(" pwwn ")[1:]
                        wwns = [wwns[j].strip().split()[0] for j in xrange(len(wwns))]
                        zone_info_list[i].append(wwns)
                    else:
                        continue
                if len(zone_info_list[i]) < 3:
                    zone_info_list[i].append([])
            return zone_info_list
        else:
            return None
        
    else:
        return None


if __name__ == "__main__":
    #out = get_linux_wwn("10.108.106.69", "root", "#1Danger0us")
    #print out
    #out = get_linux_info("10.108.105.67", "root", "#1Danger0us")
    #print out
    #out = get_solaris_info("10.108.103.215", "root", "#1Danger0us")
    #print out
    #out = get_solaris_wwn("10.108.103.215", "root", "#1Danger0us")
    #print out
    #out = get_vmware_info("10.108.220.122", "root", "#1Danger0us")
    #print out
    #out = get_vmware_wwn("10.108.220.122", "root", "#1Danger0us")
    #print out
    #out = get_brocade_info("10.108.104.121", "user_platform", "password")
    #print out
    #out = get_cisco_info("10.108.104.13", "emc", "Emc12345")
    #print out
    #out = get_hpux_info("10.108.178.233", "root", "hp")
    #print out
    #out = get_hpux_wwn("10.108.178.233", "root", "hp")
    #print out
    #out = get_aix_info("10.108.119.73", "root", "1bmaix")
    #print out
    #out = nodefind_brc("10.108.104.124", "user_platform", "password", ["21:00:00:0e:1e:09:97:bc", "21:00:00:0e:11:09:97:bc", "21:00:00:0e:1e:09:97:bd"])
    #out = nodefind_brc("10.108.179.33", "hp", "password", ["50:06:0b:00:00:1c:c2:dc", "50:06:0b:00:00:1c:c2:de", "50:06:0b:00:00:1d:22:fc", "50:06:0b:00:00:1d:22:fe", "50:06:0b:00:00:c7:dd:80", "50:06:0b:00:00:c7:dd:82", "50:06:0b:00:00:2e:c9:e4"])
    #print out
    #out = nodefind_cis("10.108.104.13", "emc", "Emc12345", ["10:00:00:05:33:26:e9:b8", "10:00:00:03:c9:56:1f:42", "10:00:00:00:c9:56:1f:42"])
    #print out
    #out = nodefind_cis("10.103.116.38", "emc", "Emc12345", ["c0:50:76:02:1d:3d:00:2e",  "c0:50:76:02:1d:3d:00:2c","c0:50:76:02:1d:3d:00:2e",  "c0:50:76:02:1d:3d:00:2c"])
    # session will close in this switch
    out = zone_search_bro("10.103.116.49", "cd", "password", "jiadi", "5")
    print out
