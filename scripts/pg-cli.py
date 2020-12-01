#!/usr/bin/env python3

# curl -s https://raw.githubusercontent.com/yolabingo/dotcms/main/scripts/pg-cli.py | python3
# prints out psql cli command for dotcms instance using db credentials from context.xml

import glob
import xml.etree.ElementTree as ET

context_path = "/opt/dotcms/wwwroot/current/plugins/com.dotcms.config/ROOT/dotserver/tomcat-*/webapps/ROOT/META-INF/context.xml"
for context in glob.glob(context_path):
    tree = ET.parse(context)

for child in tree.getroot():
    if child.tag == "Resource" and child.attrib["name"] == "jdbc/dotCMSPool":
        url = child.attrib["url"]
        if url.startswith("jdbc:postgresql://") or url.startswith("jdbc:mariadb:"):
            (_, _, db_host, db_database) = url.split("/")
            db_username = child.attrib["username"]
            db_password = child.attrib["password"]
            print ("\nPGPASSWORD='%s' psql -h %s -U %s %s\n" %(db_password, db_host, db_username, db_database))
          
