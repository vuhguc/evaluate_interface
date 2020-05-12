#!/bin/bash
setenforce 0
CUR_ABS_PATH="$(realpath "$0")"
CUR_ABS_DIR="$(dirname "$CUR_ABS_PATH")"
APP_NAME="$(xmllint --xpath "/config/app_name/text()" config.xml)"
MAIN_ABS_PATH="$CUR_ABS_DIR/$(xmllint --xpath "/config/main_rel_path/text()" config.xml)"
STATIC_ABS_PATH="$CUR_ABS_DIR/$(xmllint --xpath "/config/static_rel_path/text()" config.xml)"
HTTPD_CONF_ABS_PATH="$(xmllint --xpath "/config/httpd_conf_abs_dir/text()" config.xml)/$APP_NAME.conf"
chown -R apache:apache "$CUR_ABS_DIR"
chmod -R a=r,u+w,a+X "$CUR_ABS_DIR"
chmod 755 "$CUR_ABS_PATH" "$MAIN_ABS_PATH"
cat > "$HTTPD_CONF_ABS_PATH" <<EOF
LoadModule wsgi_module modules/mod_wsgi.so

WSGIScriptAlias /$APP_NAME "$MAIN_ABS_PATH/"

Alias /$APP_NAME/static "$STATIC_ABS_PATH/"
AddType text/html .py

<Directory "$CUR_ABS_DIR/">
  Order deny,allow
  Allow from all
</Directory>

WSGIApplicationGroup %{GLOBAL}
EOF
systemctl restart httpd