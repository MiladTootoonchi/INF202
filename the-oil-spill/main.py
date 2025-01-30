from config import ReadConfig, parseInput
from src.Simulation.solver import Solver
import logging
import os

""" setting up logger """
def make_logger(file_name):
    logger = logging.getLogger(file_name)
    handler = logging.FileHandler(f"{file_name}.log", mode="w")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s -%(message)s")

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger

def run(conf_path) -> Solver:
    """ a for loop that runs the simulation with time and config"""
    conf = ReadConfig(conf_path)

    # Making logger
    logger = make_logger(conf.logname)
    logger.info(f"Running simulation for config file: {conf_path}")

    # settings parameters
    time_start, old_solution = conf.find_solution()
    logger.info(f"time_start = {time_start}")

    time_end = conf.settings("tEnd")
    logger.info(f"time_end = {time_end}")

    nSteps = conf.settings("nSteps")
    logger.info(f"Number of steps = {nSteps}")

    dt = (time_end-time_start) / nSteps

    # Geometry parameters
    borders = conf.geometry("borders")
    logger.info(f"Border with x and y intervals = {borders}")

    mesh_file = conf.geometry("meshName")
    logger.info(f"Mesh Name = {mesh_file}")

    # Running simulation
    msh = Solver(mesh_file, borders, old_solution, time_start)
    for _ in range(nSteps):
        print(f"nSteps = {_}")
        if conf.frequency != None:
            if _ % conf.frequency == 0:
                msh.plot()
        oil = msh.solve(dt)
        logger.info(f"Time = {msh.time} | Amount of oil in fishing grounds = {oil}")

    # Plotting last picture, Storing solution, Creating Video
    msh.plot(conf.toml_name) # In config_name folder
    msh.plot()              # In video imgs folder
    conf.store_solutions(msh)
    conf.create_video()

    logger.info(f"Simulation completed. Results saved in folder: {conf.toml_name}")


if __name__ == "__main__":
    args = parseInput()

    if args.find_all:
        folder = args.folder
        config_files = [f for f in os.listdir(folder) if f.endswith('.toml')]
        for conf in config_files:
            conf_path = os.path.join(folder, conf)
            run(conf_path)

    if args.config_file:
        conf = args.config_file
        folder = args.folder
        conf_path = os.path.join(folder, conf)
        run(conf_path)
