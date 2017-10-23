import os
import sys
import subprocess
import re
import json
from collections import deque, namedtuple
import urllib

def start_crawl(root_path, root_node, local_root_path):
    """
    looping logic
    1. extract an webpage node from queue
    2. download the webpage into the right path
    3. parse its node and inserting to the queue
          print all the node for debug purpose
          check if it is already in the set, if yes then discard and continue
          check if it is in the forbidden set, if yes then discard and continue
              (not in the range of webpage set you want to fetch)
          each element in queue: <relative path>
          each element in set: <relative path>
    :param root_path: man7 path
    :param root_node: relative path of the first html to crawl
    :param local_root_path: path to store downloaded html files/dirs
    :return:
    """

    qu = deque([])  # html queue
    html_set = set()    # html set(used for check repetition)
    css_set = set()     # css set(used for check repetition)
    node_path_set = set()   # node path set(used for check dir repetition when mkdir)
    qu.append(root_node)
    node_path_set.add(local_root_path)
    node_cant_handle = set()    # html do not handle set

    while len(qu) != 0:
        # 1.get a html from queue
        node = qu.popleft()
        print "parsing node: ", node

        # split html name
        # local_node: dir_section_2.html
        # local_relative_path: linux/man-pages/
        # local_root_path: /home/nortrom/vmshare/ (your own path)
        ri = node.rfind('/')
        if ri != -1:
            local_node = node[ri + 1:]
            local_relative_path = node[:ri + 1]
        else:
            local_node = node
            local_relative_path = ""
        print "html: ", local_node, " path: ", local_relative_path

        # 2.move html file to local dir
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

        # 3.parse html
        # read the content in the webpage and extract useful information
        content = urllib.urlopen(local_root_path + node).read()
        url_list = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')", content)

        for link in url_list:
            url_suffix = link[-4:]
            url_prefix = link[:4]

            # what not handle:
            # if begin with absolute path which means a outside link, then do not handle
            if url_prefix == "http":
                print ("do not handle: %s yet" %(link))
                if link not in node_cant_handle:
                    node_cant_handle.add(link)
                continue

            # what to handle:
            # then it is a relative path to the node
            # need convert it to relative path to root path
            if url_suffix == "html" or url_suffix == ".css":
                # concat html name
                # local_relative_path + link + local_root_path
                # /home/nortrom/vmshare/linux/man-pages/man7/write.html
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


with open('cfg.json') as cfg_file:
    cfg = json.load(cfg_file, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
start_crawl(cfg.root_path, cfg.root_node, cfg.local_root_path)
