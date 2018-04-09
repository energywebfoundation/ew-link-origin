git submodule update --recursive --remote
cp -v ./certificate_of_origin/build/contracts/AssetConsumingRegistryLogic.json ./assets/
cp -v ./certificate_of_origin/build/contracts/AssetProducingRegistryLogic.json ./assets/
cp -v ./certificate_of_origin/build/contracts/AssetLogic.json ./assets/
git push
git push resin master
