#!/usr/bin/python

import os
import time
import MySQLdb
import BaseHTTPServer

HOST_NAME = '192.168.200.165'
PORT_NUMBER = 8000

# pass/fail params
FAIL_LOADAVG=0.2
FAIL_MYSQL_CONNS=200

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()

        loadavg_onemin=os.getloadavg()[0]

        conn = MySQLdb.connect(host='localhost', user='root', passwd='')
        cursor = conn.cursor()

        cursor.execute("show slave status")
        row = cursor.fetchone()
        mysql_behind_master = str(row[32])

        cursor.execute("show slave status")
        row = cursor.fetchone()
        Slave_SQL_Running = str(row[10])

        cursor.execute("show slave status")
        row = cursor.fetchone()
        Slave_IO_Running = str(row[11])

        cursor.execute("show status like 'Threads_connected'")
        row = cursor.fetchone()
        mysql_threads_connected = row[1]

        cursor.close()
        conn.close()

        if loadavg_onemin > FAIL_LOADAVG and mysql_threads_connected > FAIL_MYSQL_CONNS:
                                  CHECK_RESULT='fail'
        else:
                                  CHECK_RESULT='pass'

        s.wfile.write("<html><head><title>mysql health check.</title></head>")
        s.wfile.write("<body><p><strong>mysql health check:</strong> " + CHECK_RESULT + "</p>")
        s.wfile.write("<p>one minute loadavg: " + str(loadavg_onemin) + "</p>")
        s.wfile.write("<p>mysql threads connected: " + mysql_threads_connected + "</p>")
        s.wfile.write("<p>mysql seconds_behind_master: " + mysql_behind_master + "</p>")
        s.wfile.write("<p>Slave SQL Running?: " + Slave_SQL_Running + "</p>")
        s.wfile.write("<p>Slave SQL Running?: " + Slave_IO_Running + "</p>")
        s.wfile.write("</body></html>")

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
                                                             
