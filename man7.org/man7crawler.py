import os
import sys
import subprocess
import re
from collections import deque
import urllib


# set root path and insert to the queue
root = "http://man7.org/linux/man-pages/dir_section_2.html"
root_path = "http://man7.org/"
root_node = "linux/man-pages/dir_section_2.html"
local_root_path = "/home/nortrom/vmshare/"
qu = deque([])
html_set = set()
css_set = set()
node_path_set = set()
qu.append(root_node)
node_path_set.add(local_root_path)
node_cant_handle = set()
#qu.popleft

while len(qu) != 0:
# looping logic
# 1. extract an webpage node from queue
# 2. download the webpage into the right path
# 3. parse its node and inserting to the queue
#       print all the node for debug purpose
#       check if it is already in the set, if yes then discard and continue
#       check if it is in the forbidden set, if yes then discard and continue
#           (not in the range of webpage set you want to fetch)
#       each element in queue: <relative path>
#       each element in set: <relative path>
# 4. parse its resources and download if not exist
#       each existing resources in set: <relative path>
# 5. do some modification if needed
    # suppose all the node has relative path pattern
    # node aaa/bbb/xxx.html
    # local_node xxx.html
    # local_relative path aaa/bbb/
    node = qu.popleft()
    print "parsing node: ", node

    # also using rindex or rfind or node.split('/')[-1]
    ri = node.rfind('/')
    if ri != -1:
        local_node = node[ri + 1:]
        local_relative_path = node[:ri + 1]
    else:
        local_node = node
        local_relative_path = ""
    print local_node, local_relative_path

    # put in the right location if it do not exist yet(maybe we download it last time)
    if not os.path.exists(local_root_path + node):
        try:
            subprocess.check_output(["wget %s" %(root_path + node)], shell=True)
            if not ((local_root_path + local_relative_path) in node_path_set):
                subprocess.check_output(["mkdir -p %s" %(local_root_path + local_relative_path)], shell=True)
                if local_relative_path != "":
                    subprocess.check_output(["mv %s %s" %(local_root_path + local_node, local_root_path + node)], shell=True)
        except subprocess.CalledProcessError as e:
            print e
            continue

    # read the content in the webpage and extract useful information
    content = urllib.urlopen(local_root_path + node).read()
    url_list = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')", content)

    # category the url first
    # add something we want to the node queue
    for link in url_list:
        url_suffix = link[-4:]
        url_prefix = link[:4]

        # if begin with absolute path which means a outside link, then do not handle
        if url_prefix == "http":
            print ("do not handle: %s yet" %(link))
            if link not in node_cant_handle:
                node_cant_handle.add(link)
            continue
        # then it is a relative path to the node
        # need convert it to relative path to root path
        if url_suffix == "html" or url_suffix == ".css":
            print local_relative_path, link
            tmpnode = os.path.relpath(local_relative_path + link, local_root_path)
            # if itself has link error then continue
            # since the relative must be an inner path in local_root_path
            if tmpnode[:2] == "..":
                continue
            # ignore the node if it is already in the set
            if url_suffix == "html":
                if tmpnode in html_set:
                    continue
                else:
                    print ("adding %s into set" %(tmpnode))
                    html_set.add(tmpnode)
                    qu.append(tmpnode)
            elif url_suffix == ".css":
                if tmpnode in css_set:
                    continue
                else:
                    print ("adding %s into set" % (tmpnode))
                    css_set.add(tmpnode)
                    qu.append(tmpnode)
        else:
            print ("do not handle: %s yet" % (link))
            if link not in node_cant_handle:
                node_cant_handle.add(link)
            continue

print node_cant_handle

