git submodule update --recursive --remote
cp -v ./bond/certificate_of_origin/build/contracts/AssetConsumingRegistryLogic.json ./bond/assets/
cp -v ./bond/certificate_of_origin/build/contracts/AssetProducingRegistryLogic.json ./bond/assets/
cp -v ./bond/certificate_of_origin/build/contracts/AssetLogic.json ./bond/assets/
git push
git push resin master
