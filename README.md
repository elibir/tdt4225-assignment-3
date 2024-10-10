 ## Useful links:

 [MySql python connector docs](https://dev.mysql.com/doc/connector-python/en/connector-python-examples.html)

 [Os walk method for iterating through directories](https://www.geeksforgeeks.org/os-walk-python/)

 [Take advantage of datetime data type in your queries](https://dev.mysql.com/doc/refman/8.0/en/date-and-time-functions.html)

 [Using variables in MySQL](https://www.mysqltutorial.org/mysql-basics/mysql-variables/)

## Requirements

### Software
- python
- make
- docker desktop
- jupyter notebook

### Data
- Dataset: Ensure the required dataset is placed in the project folder

## Getting started
### Clone the Repository
```bash
git clone https://github.com/elibir/tdt4225-assignment-2
```

### Navigate to Project Directory
```bash
cd tdt4225-assignment-2
```

### Run Setup and Start Services
I use a Makefile for automating various tasks like setting up the virtual environment and the database.

Before proceeding, ensure that Docker desktop is running on your machine.

To run the entire setup and start all services:
```bash
make setup
```

### Running Queries After Initial Setup
Make sure to that the virtual envinronment is activated, if not:
```bash
myenv/Scripts/activate
```
Run the ```queries.ipynb``` jupyter notebook (use the virtual environment as the kernel.)

### Shutting Down and Cleanup
To shut down the generated Docker container and remove the virtual environment and any automatically generated Python files, use:
```bash
make down
make remove-env
```

## Useful commands:

### Access MySQL in a Running Docker Container
```bash
docker exec -it mysqldb mysql -u root -p
``` 
### Use a Database
```bash
USE testdb;
```
### Drop a Table
```bash 
DROP TABLE user;
```
### Drop a Database
```bash 
DROP DATABASE testdb;
```
### Exit MySQL
```bash
EXIT;
```
