git submodule update --recursive --remote
cp -r -v ./bond ./producer/bond
cp -r -v ./bond ./consumer/bond
git push
git push resin master
