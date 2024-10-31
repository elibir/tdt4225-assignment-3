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
git clone https://github.com/elibir/tdt4225-assignment-3
```

### Navigate to Project Directory
```bash
cd tdt4225-assignment-3
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