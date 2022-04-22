from __future__ import annotations
import numpy as np
from typing import Tuple, List
from scipy.stats import norm
from scipy.optimize import minimize
import covalent as ct

def create_particle(id: int, mass: float, coordinate: Tuple[float], velocity: Tuple[float]):
    """
    Return a new particle with coordinates in range x=(0, 1) and y=(0, 1)
    The velocity of the particle is randomly initialized from a normal distribution
    """
    random_x = coordinate[0]
    random_y = coordinate[1]
    random_vx = velocity[0]
    random_vy = velocity[1]
    return Particle(id, mass, random_x, random_y, random_vx, random_vy, 0.0, 0.0)

def pbc(x: float, L: float):
    if (x >= 0.5*L):
        return x - L
    elif (x < -0.5*L):
        return x + L
    else:
        return x

class SimulationBox(object):
    """
    A 2D Simulation domain
    """
    def __init__(self, xlo: float, xhi: float, ylo: float, yhi: float):
        self.xlo: float
        self.xhi: float
        self.ylo: float
        self.yhi: float

    def lx(self):
        return self.xhi - self.xlo

    def ly(self):
        return self.yhi - self.ylo

    def __repr__(self):
        return f"SimulationBox(xlo={self.xlo}, xhi={self.xhi}, ylo={self.ylo}, yhi={self.yhi})"

class Particle(object):
    """
    Base simulation particle
    """
    def __init__(self, id: int, mass: float, coordinates: Tuple[float], velocity: Tuple[float]):
        self.id = id
        self.mass = mass
        self.x = coordinates[0]
        self.y = coordinates[1]
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.fx = 0.0
        self.fy = 0.0

    def __eq__(self, other: Particle):
        return self.id == other.id and self.mass == other.mass

    def __repr__(self):
        return f"Particle(id={self.id}, mass={self.mass}, x={self.x}, y={self.y},\
                vx={self.vx}, vy={self.vy}, fx={self.fx}, fy={self.fy})"

class Potential(object):
    def __init__(self):
        pass
    
    def __call__(self):
        raise NotImplementedError
    
    def force(self, x: float):
        raise NotImplementedError

class Soft(Potential):
    def __init__(self, a: float, rc: float):
        self.a = a
        self.rc = rc

    def __call__(self, dr: float) -> float:
        if dr < self.rc:
            return self.a*(1+ np.cos((np.pi*dr)/(self.rc)))
        else:
            return 0.0

    def force(self, dr: float):
        return (np.pi/self.rc)*self.a*np.sin((np.pi*dr)/self.rc)

class LJ(Potential):
    def __init__(self, epsilon: float, sigma: float, rc: float):
        self.epsilon = epsilon
        self.sigma = sigma
        self.rc = rc

    def __call__(self, dr: float) -> float:
        if dr < self.rc:
            return 4*self.epsilon*((self.sigma/dr)**12 - (self.sigma/dr)**6)
        else:
            return 0.0

    def force(self, dr: float):
        return -self.epsilon*((6*self.sigma**6/dr**7) - (12*self.sigma**12/dr**13))

class Simulation(object):
    """
    Base simulation class that contains contains all the particles, domain and interaction potential
    """
    def __init__(self, timestep: float, particles: List[Particle], box: SimulationBox, potential: Potential):
        self.particles: List[Particle] = particles
        self.box = box
        self.potential = potential
        self.dt = timestep

    #@ct.electron
    def _compute_forces(self):
        for i in self.particles:
            i.fx = 0.0
            i.fy = 0.0

            i.x = pbc(i.x, self.box.lx)
            i.y = pbc(i.y, self.box.ly)

            for j in self.particles:
                if i == j:
                    continue
                else:
                    j.x = pbc(j.x, self.box.lx)
                    j.y = pbc(j.y, self.box.ly)

                    dx = i.x - i.x
                    dy = i.y - i.y

                    if (dx > 0.5*self.box.lx):
                        dx = dx - self.box.lx
                    elif (dx <= -0.5*self.box.lx):
                        dx = dx + self.box.lx

                    if (dy > 0.5*self.box.ly):
                        dy = dy - self.box.ly
                    elif (dy <= -0.5*self.box.ly):
                        dy = dy + self.box.ly

                    dr = np.sqrt(dx**2 + dy**2)

                    i.fx += self.potential.force(dr)
                    i.fy += self.potential.force(dr)

    #@ct.electron
    def _update_positions(self, step: int):
        org_particles = [p for p in self.particles]
        if step == 0:
            for p in self.particles:
                p.x = p.x + p.vx*self.dt + 0.5*p.fx*self.dt**2
                p.y = p.y + p.vy*self.dt + 0.5*p.fy*self.dt**2
        else:
            for i, p in enumerate(self.particles):
                p.x = 2*p.x - org_particles[i].x + p.fx*self.dt**2
                p.y = 2*p.y - org_particles[i].y + p.fy*self.dt**2

    #@ct.electron
    def _dump(self, filename: str):
        with open(filename, "w") as f:
            for p in self.particles:
                f.write(f"{p.id}, {p.x}, {p.y}, {p.fx}, {p.fy}\n")
            f.close()

    #@ct.lattice
    def run(self, nsteps: int):
        for i in range(nsteps):
            self._compute_forces()
            self._update_positions()
            self._dump(f"/home/venkat/simulation-{i}.txt")