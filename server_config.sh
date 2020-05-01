#!/bin/bash
setenforce 0
CUR_PATH=$(realpath "$0")
CUR_DIR=$(dirname "$CUR_PATH")
chown -R apache:apache "$CUR_DIR"
chmod -R a=r,u+w,a+X "$CUR_DIR"
chmod 755 "$CUR_PATH" "$CUR_DIR/server_app/main.py"
cat > /etc/httpd/conf.d/evaluate_interface.conf <<EOF
LoadModule wsgi_module modules/mod_wsgi.so

WSGIScriptAlias /evaluate_interface "$CUR_DIR/server_app/main.py/"

Alias /evaluate_interface/static "$CUR_DIR/server_app/static/"
AddType text/html .py

<Directory "$CUR_DIR/">
  Order deny,allow
  Allow from all
</Directory>
EOF
systemctl restart httpd