import toml
import cv2
import argparse
import os
from typing import Union, Tuple

def parseInput():
    """ Makes a the arguments in terminal for running the simulation """
    parser = argparse.ArgumentParser(description="Input config file name with -c or --config, folder with -f --folder and all files in folder with --find_all")
    parser.add_argument("--config_file", "-c", help="Path to the config file.", default="input.toml")
    parser.add_argument("--find_all", action="store_true", help="Run all config files in the folder.")
    parser.add_argument("--folder", "-f", help="Folder to search for config files.", default="")
    args = parser.parse_args()
    return args

class ReadConfig:
    """ A class that defines a config file """
    def __init__(self, conf_path: str) -> None:
        try:
            with open(conf_path, "r") as file:
                conf = toml.load(file)
        except:
            raise FileNotFoundError(f"The {conf_path} toml file does not exist")
        
        # Checking if config file has required keys """
        required_keys = ["settings", "geometry", "IO"]
        for section in required_keys:
            if section not in conf:
                raise ValueError(f"Missing required section: {section}")

        # Makes the folder with config files name
        self._toml_name = os.path.splitext(os.path.basename(conf_path))[0]
        os.makedirs(self._toml_name, exist_ok=True)

        # Define different sections in toml file
        self._settings = conf.get("settings", {})
        self._geometry = conf.get("geometry", {}) 
        self._io = conf.get("IO", {})


        self._logname = self._io.get("logName")
        self._logname = f"{self._toml_name}\{self._logname}"
        # If logname is not given
        if self._logname == None: self._logname = f"{self._toml_name}\logfile"

        self._restart_file = self._io.get("restartFile")
        self._frequency = self._io.get("writeFrequency")

    @property
    def frequency(self) -> int:
        """ Returns the frequency of plotting """
        return self._frequency

    @property
    def toml_name(self) -> str:
        """ Returns the name of config file """
        return self._toml_name

    @property
    def logname(self) -> str:
        """ Returns the logname given by the config file """
        return self._logname

    def settings(self, key: str) -> Union[str, int]:
        """ Returns a parameter asked for in the settings section """
        parameter = self._settings.get(key)
        if parameter == None:
            raise ValueError(f"The specified toml file has a inconsistent/missing entry, {key}")
        return parameter
    
    def geometry(self, key: str) -> Union[str, list]:
        """ Returns a parameter asked for in the geometry section """
        parameter = self._geometry.get(key)
        if parameter == None:
            raise ValueError(f"The specified toml file has a inconsistent/missing entry, {key}")
        return parameter

    def find_solution(self) -> Tuple[float, list[float]]:
        """ Restarts the simulation with the solution values provided in a restart file 
        when the parameter restartFile and t_start is provided. If not provided time_start = 0.0"""
        time_start = self._settings.get("tStart")
        
        if (time_start == None and self._restart_file != None) or (time_start != None and self._restart_file == None):
            raise ValueError("If the restart file is provided, a start time must be provided and vice-versa")
        
        if time_start == None:
            time_start = 0.0
        
        if self._restart_file != None:
            with open(self._restart_file, "r") as file:
                lines = file.readlines()
                oil_list = []
                for line in lines:
                    oil = float(line.strip())
                    oil_list.append(oil)
        else: # restartfile was not provided
            oil_list = []
        
        return time_start, oil_list
            

    def store_solutions(self, msh) -> None:
        """ Stores the oil distribution list over mesh in a txt file"""
        try:    # Updated the given txt file
            with open(self._restart_file, "w") as file:
                for oil in msh.oil_list:
                    file.write(f"{oil}\n")
        except: # Makes a new one if txt file is not provided
            with open(f"{self._toml_name}\solution.txt", "w") as file:
                for oil in msh.oil_list:
                    file.write(f"{oil}\n")

        
    def create_video(self) -> None:
        """ Creates a video of the images saved if frequency is provided"""
        if self._frequency != None:

            images = [os.path.join("imgs", filename)
            for filename in os.listdir("imgs") if filename.startswith("oil_dist_") and filename.endswith(".png")]

            frame = cv2.imread(images[0])

            height, width, layers = frame.shape

            fourcc = cv2.VideoWriter_fourcc(*"DIVX")
            video = cv2.VideoWriter(f"{self._toml_name}\simulation_for_{self._toml_name}.AVI", fourcc, 5, (width, height))

            for image in images:
                video.write(cv2.imread(image))

            cv2.destroyAllWindows()
            video.release()