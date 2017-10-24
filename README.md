# offline-searcher
An offline web page searcher for user's who can only access local network. It will support searching web page from site man.org and stackoverflow

# man7.org web crawler
Using man7crawler.py script to fetch all manpages. These web pages will store in the same relative path like man7 web server.
You need to config local_root_path in cfg.json which set manpages location.

# search man pages
Once fetched all manpages you need to import all of them into stackdump database and solr server:<br>
run solr server first:<br>
`./start_solr.sh`<br>
then import:<br>
`./manage.sh import_site --mode manpages --base-url "linux.manpage" --dump-date "August 2017" --site-name "manpages" --site-key "man" --site-desc "linux manpages" "/home/nortrom/vmshare/work/manpages/linux/man-pages/man7"`

And for original stackdump, the command also becomes a little different:<br>
`./manage.sh import_site --mode stackoverflow --base-url datascience.stackexchange.com --dump-date "August 2017" ~/vmshare/datascience.stackexchange.com/ --site-name "datascience" --site-key "ds" --site-desc "data science"`

When import finished, you can start web to enjoy offline searching:<br>
`./start_web.sh`
