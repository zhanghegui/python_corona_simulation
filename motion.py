'''
file that contains all function related to population mobility
and related computations
'''

import numpy as np

def update_positions(population):
    '''update positions of all people

    Uses heading and speed to update all positions for
    the next time step

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information
    '''

    #update positions
    #x
    population[:,1] = population[:,1] + (population[:,3] * population[:,5])
    #y
    population[:,2] = population[:,2] + (population [:,4] * population[:,5])

    return population


def out_of_bounds(population, xbounds, ybounds):
    '''checks which people are about to go out of bounds and corrects

    Function that updates headings of individuals that are about to 
    go outside of the world boundaries.
    
    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information

    xbounds, ybounds : list or tuple
        contains the lower and upper bounds of the world [min, max]
    '''
    #update headings and positions where out of bounds
    #update x heading
    #determine number of elements that need to be updated

    shp = population[:,3][(population[:,1] <= xbounds[:,0]) &
                            (population[:,3] < 0)].shape
    population[:,3][(population[:,1] <= xbounds[:,0]) &
                    (population[:,3] < 0)] = np.clip(np.random.normal(loc = 0.5, 
                                                                      scale = 0.5/3,
                                                                      size = shp),
                                                        a_min = 0.05, a_max = 1)

    shp = population[:,3][(population[:,1] >= xbounds[:,1]) &
                            (population[:,3] > 0)].shape
    population[:,3][(population[:,1] >= xbounds[:,1]) &
                    (population[:,3] > 0)] = np.clip(-np.random.normal(loc = 0.5, 
                                                                       scale = 0.5/3,
                                                                       size = shp),
                                                        a_min = -1, a_max = -0.05)

    #update y heading
    shp = population[:,4][(population[:,2] <= ybounds[:,0]) &
                            (population[:,4] < 0)].shape
    population[:,4][(population[:,2] <= ybounds[:,0]) &
                    (population[:,4] < 0)] = np.clip(np.random.normal(loc = 0.5, 
                                                                      scale = 0.5/3,
                                                                      size = shp),
                                                        a_min = 0.05, a_max = 1)

    shp = population[:,4][(population[:,2] >= ybounds[:,1]) &
                            (population[:,4] > 0)].shape
    population[:,4][(population[:,2] >= ybounds[:,1]) &
                    (population[:,4] > 0)] = np.clip(-np.random.normal(loc = 0.5, 
                                                                       scale = 0.5/3,
                                                                       size = shp),
                                                        a_min = -1, a_max = -0.05)

    return population


def out_of_bounds_polygon(population, polygon):
    '''checks who is outside of the given polygon and adjusts their heading
    
    '''
    #find those outside 
    mask = ~ray_trace_polygon(population[:,1], 
                              population[:,2], 
                              polygon)   
    
    outside = population[mask]

    
    #define size of polygon
    x_scale = np.ptp(polygon[:,0])
    y_scale = np.ptp(polygon[:,1])
    
    #define random points around mean of polygon on x/y
    x_mean = np.min(polygon[:,0]) + (x_scale / 2)
    y_mean = np.min(polygon[:,1]) + (y_scale / 2)
    
    #x_dests = np.clip(np.random.normal(loc = x_mean,
    #                                   scale = x_scale / 3,
    #                                   size = len(outside)),
    #                  a_min = -1, a_max = 1)
    
    #y_dests = np.clip(np.random.normal(loc = y_mean,
    #                                   scale = y_scale / 3,
    #                                   size = len(outside)),
    #                  a_min = -1, a_max = 1)

    
    x_dests = np.clip(((x_mean + x_scale / 2) - (x_mean - x_scale / 2)) * np.random.random(size = len(outside)) + (x_mean - x_scale / 2),
                      a_min = -1, a_max = 1)
    
    y_dests = np.clip(((y_mean + y_scale / 2) - (y_mean - y_scale / 2)) * np.random.random(size = len(outside)) + (y_mean - y_scale / 2),
                      a_min = -1, a_max = 1)

    
    outside[:,3] = x_dests - outside[:,1] #heading x
    outside[:,4] = y_dests - outside[:,2] #headings y
    
    population[mask] = outside
    
    return population   


def update_randoms(population, pop_size, speed=0.01, heading_update_chance=0.02, 
                   speed_update_chance=0.02, heading_multiplication=1,
                   speed_multiplication=1):
    '''updates random states such as heading and speed
    
    Function that randomized the headings and speeds for population members
    with settable odds.

    Keyword arguments
    -----------------
    population : ndarray
        the array containing all the population information
    
    pop_size : int
        the size of the population

    heading_update_chance : float
        the odds of updating the heading of each member, each time step

    speed_update_chance : float
        the oodds of updating the speed of each member, each time step

    heading_multiplication : int or float
        factor to multiply heading with (default headings are between -1 and 1)

    speed_multiplication : int or float
        factor to multiply speed with (default speeds are between 0.0001 and 0.05

    speed : int or float
        mean speed of population members, speeds will be taken from gaussian distribution
        with mean 'speed' and sd 'speed / 3'
    '''

    #randomly update heading
    #x
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,3][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                        scale = 1/3,
                                                        size = shp) * heading_multiplication
    #y
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,4][update <= heading_update_chance] = np.random.normal(loc = 0, 
                                                        scale = 1/3,
                                                        size = shp) * heading_multiplication
    #randomize speeds
    update = np.random.random(size=(pop_size,))
    shp = update[update <= heading_update_chance].shape
    population[:,5][update <= heading_update_chance] = np.random.normal(loc = speed, 
                                                        scale = speed / 3,
                                                        size = shp) * speed_multiplication

    population[:,5] = np.clip(population[:,5], a_min=0.0001, a_max=0.05)
    return population


def get_motion_parameters(xmin, ymin, xmax, ymax):
    '''gets destination center and wander ranges

    Function that returns geometric parameters of the destination
    that the population members have set.

    Keyword arguments:
    ------------------
        xmin, ymin, xmax, ymax : int or float
        lower and upper bounds of the destination area set.

    '''

    x_center = xmin + ((xmax - xmin) / 2)
    y_center = ymin + ((ymax - ymin) / 2)

    x_wander = (xmax - xmin) / 2
    y_wander = (ymax - ymin) / 2

    return x_center, y_center, x_wander, y_wander


def ray_trace_polygon(x,y,poly):
    '''find who is inside or outside polygon
    
    Function that determines which population members are inside or
    outside the polygon (province) in a fast way analogous to ray tracing.
    
    Adapted from https://stackoverflow.com/a/57999874
    
    Keyword arguments
    -----------------
    x : int, float, ndarray
        x position(s) of population
        
    y : int, float, ndarray
        y position(s) of population
        
    poly : ndarray
        points describing the polygon. Lower point counts
        dramatically affect performance, especially on larger populations
        
    Returns
    -------
    mask : ndarray
        ndarray containing boolean values, true for those inside, 
        false for those outside polygon.
    '''
    
    n = len(poly)
    inside = np.zeros(len(x),np.bool_)
    p2x = 0.0
    p2y = 0.0
    xints = 0.0
    p1x,p1y = poly[0]
    
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        idx = np.nonzero((y > min(p1y,p2y)) & (y <= max(p1y,p2y)) & (x <= max(p1x,p2x)))[0]
    
        if p1y != p2y:
            xints = (y[idx] - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
        
        if p1x == p2x:
            inside[idx] = ~inside[idx]
        
        else:
            idxx = idx[x[idx] <= xints]
            inside[idxx] = ~inside[idxx]    

        p1x,p1y = p2x,p2y
    
    return inside   