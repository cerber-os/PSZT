#!/usr/bin/env python3
import argparse
import pickle
import random
import re
import requests

from bs4 import BeautifulSoup
from math import radians, sin, cos, sqrt, asin, log2
import matplotlib.pyplot as plt

##############################
# Loggers
##############################
class Term:
    red =   '\x1b[31m'
    blue = '\x1b[34m'
    green = '\x1b[32m'
    default = '\x1b[0m'

def error(*args):
    args = ('[' + Term.red + '!!!' + Term.default + ']',) + args
    print(*args)

def info(*args):
    args = ('[' + Term.green + '+' + Term.default + ']',) + args
    print(*args)

##############################
# Crawl neccessary information
##############################
class Capital:
    def __init__(self, name: str, lat: str, lon: str):
        self.name = name
        self.lat = radians(Capital._convert(lat))
        self.lon = radians(Capital._convert(lon))
    
    def __str__(self):
        return f'{self.name} - ({self.lat}, {self.lon})'

    @staticmethod
    def _convert(cord: str) -> float:
        '''
            Convert provided string representing geograhpical location
            to degrees
        '''
        positive = cord[-1] in ['N', 'E']
        match = re.match(r'(\d+).(\d+).(\d+){0,1}.*', cord)
        d, m, = float(match.group(1)), float(match.group(2))
        tmp_s = match.group(2)
        s = float(tmp_s) if tmp_s else 0
        return (d + m / 60.0 + s / 3600.0) * (1 if positive else -1)

    def distance(self, other_city: 'Capital') -> float:
        '''
            Calculate distance between two cities using Haversine formula:
                https://en.wikipedia.org/wiki/Haversine_formula
            Assume that earth radius is 6371km and it's a perfect sphere
            Returned distance is in kilometers (km)
        '''
        lat_diff = other_city.lat - self.lat
        lon_diff = other_city.lon - self.lon

        earth_radius = 6371
        a = sin(lat_diff / 2) ** 2 + cos(self.lat) * cos(other_city.lat) * (sin(lon_diff / 2) ** 2)
        d = 2 * earth_radius * asin(sqrt(a))
        return round(d)

def download_capitals_list() -> list:
    '''
        Download names and positiions of capitals of all countries located in
        both North and South America. Use wikipedia articles to gather necessary
        information
    '''
    result = []

    r = requests.get('https://en.wikipedia.org/wiki/Americas')
    if r.status_code != 200:
        error('Failed to download capitals list. Server returned:', r.status_code)
        exit(1)
    
    soup = BeautifulSoup(r.text, features="lxml")
    table = soup.find_all('table', class_="sortable")[0]
    rows = table.find_all('tr')
    for row in rows:
        tds = row.find_all('td')
        if len(tds) < 6:
            continue

        countryName = tds[0].find('a').text

        if tds[5].find('a') == None:
            continue
        capitalName = tds[5].find('a').text
        capitalLink = tds[5].find('a')['href']

        r = requests.get('https://en.wikipedia.org' + capitalLink)
        if r.status_code != 200:
            error(f'Failed to download capital details ({capitalLink}). Server returned:', r.status_code)
            exit(1)
        
        subsoup = BeautifulSoup(r.text, features="lxml")
        lat = subsoup.find_all('span', class_="latitude")[0].text
        lon = subsoup.find_all('span', class_="longitude")[0].text
        result += [Capital(capitalName, lat, lon)]

    return  result

def get_capitals_list() -> list:
    '''
        Try to read capitals list from the locally cached file.
        In case its missing, download list from the web using 
        `download_capitals_list` function
    '''
    try:
        with open('resources/capitals.pkl', 'rb') as f:
            return pickle.load(f)
    except:
        info('Downloading capitals list. This might take a while....')
        capitals = download_capitals_list()
        with open('resources/capitals.pkl', 'wb') as f:
            pickle.dump(capitals, f)
        return capitals


##############################
# Genius AI implementation
##############################

class Path:
    def __init__(self, length: int, vertices=None):
        if not vertices:
            self.vertices = [i for i in range(length)]
            random.shuffle(self.vertices)
        else:
            self.vertices = vertices

    
    def isValid(self) -> bool:
        '''
            Check if each verticle is present only once in vector
        '''
        if len(set(self.vertices)) != len(self.vertices) or len(self.vertices) != len(capitals):
            error('Path is invalid!')
            return False
        else:
            return True

    def length(self) -> float:
        total = 0.0
        for i in range(len(self.vertices) - 1):
            total += distances[(self.vertices[i], self.vertices[i+1])]
        total += distances[(self.vertices[-1], self.vertices[0])]
        return total if self.isValid() else 0.0
    
    # Mutations
    def mutate_swap(self):
        pos1 = random.randint(0, len(self.vertices) - 1)
        pos2 = random.randint(0, len(self.vertices) - 1)
        self.vertices[pos1], self.vertices[pos2] = self.vertices[pos2], self.vertices[pos1]

    # Reproductions
    def reproduce_pmx(self, parent2: 'Path') -> tuple:
        pos1 = random.randint(0, len(self.vertices) - 2)
        pos2 = random.randint(pos1, len(self.vertices) - 1)

        t1, t2 = {}, {}
        for i in range(pos1, pos2 + 1):
            t1[self.vertices[i]] = parent2.vertices[i]
            t2[parent2.vertices[i]] = self.vertices[i]

        child1, child2 = [], []

        def pos_filler(i):
            def key_finder(what, where):
                key = what
                while key in where:
                    key = where[key]
                return key

            p1 = self.vertices[i]
            p2 = parent2.vertices[i]

            if p1 in t2:
                child1.append(key_finder(p1, t2))
            else:
                child1.append(self.vertices[i])
            if p2 in t1:
                child2.append(key_finder(p2, t1))
            else:
                child2.append(parent2.vertices[i])

        # Left part
        for idx in range(0, pos1):
            pos_filler(idx)

        # Middle part - swap it
        for i in range(pos1, pos2 + 1):
            child1.append(parent2.vertices[i])
            child2.append(self.vertices[i])
        
        # Right part - the same as left part
        for idx in range(pos2 + 1, len(self.vertices)):
            pos_filler(idx)

        return Path(0, child1), Path(0, child2)


def ai_main(population_size: int, generations_count: int, mutation_factor: float):
    bests = []
    logn_population_size = int(round(log2(population_size) + 1))

    population = [Path(len(capitals)) for _ in range(population_size)]
    for generation in range(generations_count):
        population = sorted(population, key=lambda x: x.length())
        best_member = population[-1]
        
        # Reproduce best members
        best_part_population = population[:logn_population_size]
        new_population = []
        for A in best_part_population:
            for B in best_part_population:
                child1, child2 = A.reproduce_pmx(B)
                new_population.append(child1)
                new_population.append(child2)
        population = new_population[0:population_size]

        # Apply mutation
        if mutation_factor > random.uniform(0, 1):
            pos = random.randint(0, population_size - 1)
            population[pos].mutate_swap()
        
        # Record best member
        bests.append(best_member.length())
    
    info('Lowest score found:', min(bests))
    plt.scatter(range(generations_count), bests, s=1)
    plt.show()


##############################
# Entry point
##############################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Solve TSP using genetic algorithms')
    parser.add_argument('--population_size', type=int, default=10, help='The size of population used')
    parser.add_argument('--generations_count', type=int, default=1000, help='The number of algorithm iterations')
    parser.add_argument('--mutation_factor', type=float, default=0.2, help='Frequency of mutation (1 = always; 0 = never)')
    args = parser.parse_args()

    capitals = get_capitals_list()
    info(f'Loaded {len(capitals)} capitals')

    distances = {}
    for i, A in enumerate(capitals):
        for j, B in enumerate(capitals):
            distances[(i, j)] = A.distance(B)

    ai_main(args.population_size, args.generations_count, args.mutation_factor)

    info('Finished')
