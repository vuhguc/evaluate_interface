setenforce 0
CUR_PATH = $(dirname '$(readlink -f "$0")')
chown -R apache:apache "$CUR_PATH"
chmod -R a=r,u+w,a+X "$CUR_PATH"
cat > /etc/httpd/conf.d/evaluate_interface.conf <<EOF
LoadModule wsgi_module modules/mod_wsgi.so

WSGIScriptAlias /evaluate_interface "$CUR_PATH/server_app/main.py/"

Alias /evaluate_interface/static "$CUR_PATH/server_app/static/"
AddType text/html .py

<Directory $CUR_PATH/>
  Order deny, allow
  Allow from all
</Directory>
EOF
systemctl restart httpd