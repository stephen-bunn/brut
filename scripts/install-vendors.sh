#!/bin/sh

for plugin in /vendor/*/
do
  plugin_name=$(basename "$plugin" | tr "-" "_")
  mkdir -p /.config/megu/plugins/$plugin_name
  python -m pip install --upgrade $plugin --target $BRUT_MEGU_PLUGIN_DIR/$plugin_name
done
