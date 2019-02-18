#!/bin/sh

NAME="vihainen-rest"
VERSION="latest"

if ! [ -z $1 ]
then
    VERSION="$1"
fi

TAG="$NAME:$VERSION"

docker build --tag $TAG .
