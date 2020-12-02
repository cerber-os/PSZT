# PSZT
Project for Basics of Artificial Intelligence subject at Warsaw University of Technology

## Requirements
```bash
pip3 install -r requirements.txt
```
## Usage
Example:
```python
./america.py
```
Optional arguments: 

| Parameter                 | Default       | Description   |	
| :------------------------ |:-------------:| :-------------|
| --population_size	       |	10           |The size of population used
| --generations_count          | 1000          |The number of algorithm iterations
| --mutation_factor	       |	0.2           |Frequency of mutation (1 = always; 0 = never)
| --algorithm 		       | 0       | Crossover algorithm to use (0 = PMX; 1 = OX, 2 = CX)
