#!/bin/sh

for plugin in /vendor/*/
do
    plugin_name=$(basename "$plugin" | tr "-" "_")
    mkdir -p $MEGU_PLUGIN_DIR/$plugin_name
    python -m pip install --upgrade $plugin --target $MEGU_PLUGIN_DIR/$plugin_name
done
