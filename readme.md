## Structure

* DDL.sql - sql scripts
* main.py - main file
* docker-comppose.yml - 3 DB deployment file

## Requirements

docker, python3, pip3


## Install

```bash
python -m venv .venv
source ./env/bin/activate

pip install -r requirements.txt

docker-compose up

OR

docker run -d --name db1 -e POSTGRES_USER=app -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=fly -v $(pwd)/data/db1:/var/lib/postgresql/data -p 5431:5432 postgres -c 'max_prepared_transactions=3' 

docker run -d --name db2 -e POSTGRES_USER=app -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=hotel -v $(pwd)/data/db2:/var/lib/postgresql/data -p 5432:5432 postgres -c 'max_prepared_transactions=3' 

docker run -d --name db3 -e POSTGRES_USER=app -e POSTGRES_PASSWORD=secret -e POSTGRES_DB=account -v $(pwd)/data/db3:/var/lib/postgresql/data -p 5433:5432 postgres -c 'max_prepared_transactions=3' 

```

## How to

```
python main.py

    --help
        show this info page

    --clean
        drop all tabels

    --migrate
        create all tables insert account with some amount

    --set-amount <sum>
        update/insert account's amount
    
    --get-amount
        gets test accout amount

    --book <sum>
        hotel and flight withdrawing sum
    
    --repair
        rolback all failed transaction
        
    --fail
        fail scenario
```