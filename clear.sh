docker system prune -af

rm -rf ./consumer/assets
rm -rf ./consumer/certificate_of_origin
rm -rf ./consumer/core
rm -rf ./consumer/requirements.txt
rm -rf ./consumer/LICENSE

rm -rf ./producer/assets
rm -rf ./producer/certificate_of_origin
rm -rf ./producer/core
rm -rf ./producer/requirements.txt
rm -rf ./producer/LICENSE

cp -r -v ./bond/* ./producer/
cp -r -v ./bond/* ./consumer/