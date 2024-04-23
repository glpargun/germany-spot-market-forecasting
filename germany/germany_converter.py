import matplotlib.pyplot as plt
import re
import numpy as np
from matplotlib.path import Path

def get_sector_positions(path):
    with open(path, 'r') as file:
        data = file.read()
    strings = re.findall(r'<path(.*?)</path>', data)
    sectors = []
    fig, ax = plt.subplots()
    for string in strings[:-4]: # remove areas outside germany
        number = re.search(r'highcharts-name-(.*?)">', string).group(1)
        number = int(number)
        print(number)
        string = re.sub("L ", "", string)
        curve = re.search(r'M (.*?) Z', string).group(1)
        points = []
        if len(re.findall(r'M', curve))>0:
            curve = re.search(r'(.*?) M', curve).group(1)   
        for point_name in curve.split():
            points.append(float(point_name))
        points = np.array(points)
        x = points[::2]
        y = points[1::2]
        tup = list(zip(x, y))
        sectors.append({'x':x, 'y':y, 'tuple':tup, 'number':number})
        ax.plot(x, y)
    plt.show()
    return sectors

def get_ranges_positions(sectors):
    x_min, y_min = 1000, 1000
    x_max, y_max = 0, 0
    for sector in sectors:
        x_min_sector = np.min(sector['x'])
        y_min_sector = np.min(sector['y'])
        x_max_sector = np.max(sector['x'])
        y_max_sector = np.max(sector['y'])
        if x_min_sector < x_min:
            x_min = x_min_sector
        if y_min_sector < y_min:
            y_min = y_min_sector
        if x_max_sector > x_max:
            x_max = x_max_sector
        if y_max_sector > y_max:
            y_max = y_max_sector
    print(x_min)
    print(x_max)
    print(y_min)
    print(y_max)
    return x_min, x_max, y_min, y_max

def create_mask_from_sectors(sectors, num_pixels, x_min, x_max, y_min, y_max):
    x_grid, y_grid = np.meshgrid(np.linspace(x_min, x_max, num_pixels), np.linspace(y_min, y_max, num_pixels)) 
    x_grid, y_grid = x_grid.flatten(), y_grid.flatten()
    grid_points = np.vstack((x_grid,y_grid)).T
    mask = np.zeros((num_pixels, num_pixels)) 
    for sector in sectors:
        tup = sector['tuple']
        p = Path(tup) # make a polygon
        grid = p.contains_points(grid_points)
        mask += grid.reshape(num_pixels,num_pixels)*sector['number']
    plt.imshow(mask)
    plt.show()
    return mask


if __name__ == '__main__':
    path = r"C:\Users\113202010\Desktop\workspace6\germany\inner_html.txt"
    sectors = get_sector_positions(path)
    x_min, x_max, y_min, y_max = get_ranges_positions(sectors)
    mask = create_mask_from_sectors(sectors, 30, x_min, x_max, y_min, y_max)
    np.savetxt(r"C:\Users\113202010\Desktop\workspace6\germany\mask.csv", mask, delimiter=",")