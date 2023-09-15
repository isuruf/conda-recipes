mkdir $PREFIX/Library
cp -R $SRC_DIR/binary/* $PREFIX/Library/
test -d $PREFIX/Library/usr
rm -rf $PREFIX/Library/usr/lib/python3.11/site-packages/__pycache__/
