#!/usr/bin/env python3

# curl -s https://raw.githubusercontent.com/yolabingo/dotcms/main/scripts/pg-cli.py | python3
# prints out psql cli command for dotcms instance using db credentials from db.properties or context.xml

import collections
import glob
import xml.etree.ElementTree as ET


Credentials = collections.namedtuple('Credentials', 'password host username database')


class DotcmsDbCreds():

    def __init__(self):
        self.creds = None
        self.db_properties = "/opt/dotcms/wwwroot/current/plugins/com.dotcms.config/ROOT/dotserver/tomcat-*/webapps/ROOT/WEB-INF/classes/db.properties"
        self.context_xml = "/opt/dotcms/wwwroot/current/plugins/com.dotcms.config/ROOT/dotserver/tomcat-*/webapps/ROOT/META-INF/context.xml"


    def set_credentials(self, password=None, host=None, username=None, database=None):
        assert password 
        assert host
        assert username
        assert database
        self.creds = Credentials(password=password, host=host, username=username, database=database)


    def print_creds(self):
        self.parse_db_properties()
        if not self.creds:
            self.parse_context_xml()
        if self.creds:
            self.print_scripts_config()
            self.print_connect()
        else:
            print("Credentials not found")


    def parse_context_xml(self):
        """ read and parse context.xml file for database credentials 
            This is the fallback if db.properties is not present.
        """
        for context_file in glob.glob(self.context_xml):
            tree = ET.parse(context_file)

        for child in tree.getroot():
            if child.tag == "Resource" and child.attrib["name"] == "jdbc/dotCMSPool":
                url = child.attrib["url"]
                if url.startswith("jdbc:postgresql://"):
                    (_, _, db_host, db_database) = url.split("/")
                    db_username = child.attrib["username"]
                    db_password = child.attrib["password"]
                    self.set_credentials(password=db_password, host=db_host, username=db_username, database=db_database)
        if self.creds:
            print("credentials found in\n  %s  " %(context_file,))

    def parse_db_properties(self):
        """ parse db.properties for database credentials """
        for db_properties_file in glob.glob(self.db_properties):
            with open(db_properties_file, "r") as fh:
                lines = fh.readlines()
        for line in lines:
            # remove all whitespace
            line = "".join(line.split())
            if "=" in line:
                k, v = line.split("=")
                if k == "username":
                    db_username = v
                elif k == "password":
                    db_password = v
                elif k == "jdbcUrl":
                    # jdbcUrl=jdbc:postgresql://db.example.com:5432/dotcms
                    jdbc_url = v.split("/")
                    if jdbc_url[0] == "jdbc:postgresql:":
                        db_host = jdbc_url[2]
                        db_database = jdbc_url[3]
        if db_username and db_password and db_host and db_database:
            print ("credentials found in\n  %s  " %(db_properties_file,))
            self.set_credentials(password=db_password, host=db_host, username=db_username, database=db_database)


    def print_connect(self):
        print("\nPGPASSWORD='%s' psql -h %s -U %s %s\n" %(self.creds.password, self.creds.host, self.creds.username, self.creds.database))


    def print_dumpt(self):
        print("\nPGPASSWORD='%s' pg_dump -h %s -U %s -d %s\n" %(self.creds.password, self.creds.host, self.creds.username, self.creds.database))


    def print_scripts_config(self):
        print("\n##  /opt/dotcms/sbin/scripts_config.sh ##")
        print('SQL_DBNAMES="%s"' %(self.creds.database,))
        print('SQL_HOSTNAME="%s"' %(self.creds.host,))
        print('SQL_USERNAME="%s"' %(self.creds.username,))
        print('SQL_PASSWORD="%s"\n' %(self.creds.password,))


if __name__ == "__main__":
    DotcmsDbCreds().print_creds()
