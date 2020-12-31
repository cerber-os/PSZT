# PSZT - Project "Traveling Salesman America"

## Requirements

```bash
pip3 install -r requirements.txt
```


## Usage

Example:

```sh
./america.py
```

Optional arguments: 

| Parameter                 | Default       | Description   |	
| :------------------------ |:-------------:| :-------------|
| --population\_size	       |	10           |The size of population used
| --generations\_count          | 1000          |The number of algorithm iterations
| --mutation\_factor	       |	0.2           |Frequency of mutation (1 = always; 0 = never)
| --algorithm 		       | 0       | Crossover algorithm to use (0 = PMX; 1 = OX, 2 = CX)
