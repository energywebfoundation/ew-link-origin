# Running on x64 machine and docker
Switch to the `x64` branch and run docker compose, it will run parity on Tobalaba and will build the subcontainters for producer and consumer bond distributions. If you need to update after running `git pull`, please clean docker up. Bellow are the commands to execute this operations.

#### First run
```
git fetch
git checkout x64
docker-compose up
```
1. Edit the __PRODUCER__ and __CONSUMER__ variables in `producer/Dockerfile` and `consumer/Dockerfile`.
2. Wait until Parity syncs the chain. In short just check for latest block in [etherscan](https://tobalaba.etherscan.com/) and compare to the ones being imported by the client.

#### Update
After pulling new code updates please clear up docker. 
```
git pull
./clear.sh
docker-compose up
```