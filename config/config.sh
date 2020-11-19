#!/bin/sh

export OLD_LD_LIBRARY_PATH=$LD_LIBRARY_PATH
unset LD_LIBRARY_PATH
if ! echo "$0" | grep '\.sh$' > /dev/null; then
    printf 'Please run using "bash" or "sh", but not "." or "source"\\n' >&2
    return 1
fi

# Determine RUNNING_SHELL; if SHELL is non-zero use that.
if [ -n "$SHELL" ]; then
    RUNNING_SHELL="$SHELL"
else
    if [ "$(uname)" = "Darwin" ]; then
        RUNNING_SHELL=/bin/bash
    else
        if [ -d /proc ] && [ -r /proc ] && [ -d /proc/$$ ] && [ -r /proc/$$ ] && [ -L /proc/$$/exe ] && [ -r /proc/$$/exe ]; then
            RUNNING_SHELL=$(readlink /proc/$$/exe)
        fi
        if [ -z "$RUNNING_SHELL" ] || [ ! -f "$RUNNING_SHELL" ]; then
            RUNNING_SHELL=$(ps -p $$ -o args= | sed 's|^-||')
            case "$RUNNING_SHELL" in
                */*)
                    ;;
                default)
                    RUNNING_SHELL=$(which "$RUNNING_SHELL")
                    ;;
            esac
        fi
    fi
fi

# Some final fallback locations
if [ -z "$RUNNING_SHELL" ] || [ ! -f "$RUNNING_SHELL" ]; then
    if [ -f /bin/bash ]; then
        RUNNING_SHELL=/bin/bash
    else
        if [ -f /bin/sh ]; then
            RUNNING_SHELL=/bin/sh
        fi
    fi
fi

if [ -z "$RUNNING_SHELL" ] || [ ! -f "$RUNNING_SHELL" ]; then
    printf 'Unable to determine your shell. Please set the SHELL env. var and re-run\\n' >&2
    exit 1
fi

THIS_DIR=$(DIRNAME=$(dirname "$0"); cd "$DIRNAME"; pwd)
THIS_FILE=$(basename "$0")
THIS_PATH="$THIS_DIR/$THIS_FILE"
THIS_DIR_PARENT=$(dirname $(DIRNAME=$(dirname "$0"); cd "$DIRNAME"; pwd))


INTAIN_CARDEKHO_PROJECT_NAME='intain_cardekho_ai'
INTAIN_CARDEKHO_DEPLOYMENT_ROOT_DIR=$THIS_DIR_PARENT
INTAIN_CARDEKHO_DEPLOYMENT_UPLOAD_DIR_ABS="$THIS_DIR_PARENT/webserverflask/static/uploads"
INTAIN_CARDEKHO_TEMP_DIR="/tmp/$INTAIN_CARDEKHO_PROJECT_NAME"

if [ -d "$INTAIN_CARDEKHO_DEPLOYMENT_UPLOAD_DIR_ABS" ]
then
	echo "$INTAIN_CARDEKHO_DEPLOYMENT_UPLOAD_DIR_ABS directory  exists."
else
	echo "$INTAIN_CARDEKHO_DEPLOYMENT_UPLOAD_DIR_ABS directory not found. Creating it"
    mkdir -p $INTAIN_CARDEKHO_DEPLOYMENT_UPLOAD_DIR_ABS
    chmod -R 777 $INTAIN_CARDEKHO_DEPLOYMENT_UPLOAD_DIR_ABS
fi

if [ -d "$INTAIN_CARDEKHO_TEMP_DIR" ]
then
	echo "$INTAIN_CARDEKHO_TEMP_DIR directory  exists. Cleaning it."
    chmod -R 777 $INTAIN_CARDEKHO_TEMP_DIR
else
	echo "$INTAIN_CARDEKHO_TEMP_DIR directory not found. Creating it"
    mkdir -p $INTAIN_CARDEKHO_TEMP_DIR
    chmod -R 777 $INTAIN_CARDEKHO_TEMP_DIR
fi

