import pathlib
import os
import xarray as xr
import re
import numpy as np
import multiprocessing
import datetime
import logging
from functools import partial

class DataRetriever:
    """
    A class to handle variable extraction and processing from simulation output files.

    :param case_path: Path to the directory containing case files.
    :type case_path: str
    :param debug_mode: Optional flag to enable debug mode for logging, defaults to False.
    :type debug_mode: bool, optional
    """
    
    def __init__(self, case_path, debug_mode=False):
        """
        Initialize the VVMTools class.

        This constructor initializes key class attributes, including dictionaries for variable types,
        spatial dimensions, and initial profiles. It also handles time-related data and enables logging
        when debug mode is activated. Helper methods are called to set up variable type dictionaries, 
        load topographic variables, establish spatial dimensions, and create a time array.

        :param case_path: The path to the directory containing the case files.
        :type case_path: str
        :param debug_mode: Flag indicating whether to enable debug logging. Defaults to False.
        :type debug_mode: bool, optional
        :ivar VARTYPE: Variable type for VVM tools.
        :ivar DIM: Dimension for VVM simulations. There will be `xc`, `yc` `zc` (grid center), `zz` (grid upper) inside
        :ivar INIT: There will be 
        :ivar time_array_str: String array for time values.
        :ivar DEBUGMODE: Flag for debug mode.
        :ivar CASEPATH: Path for case files.

        The constructor performs the following actions:
        
        - Initializes `VARTYPE`, `DIM`, and `INIT` dictionaries to hold variable types, dimensions, and initial profile data respectively.
        - Calls the following helper methods:
            - `_build_variable_type_dict`: To construct a dictionary of variable types.
            - `_load_topo_variables`: To load topographic variables from the case directory.
            - `_get_initial_profile`: To read and store the initial atmospheric profile.
            - `_get_date_time`: To generate an array of time points from 05:00 to 05:00 of the next day.
            - `_build_dimension`: To extract and store the spatial dimensions (`xc`, `yc`, `zc`).
        - Sets up logging based on the `debug_mode` parameter. If `debug_mode` is True, logging level is set to DEBUG.
        """
        self.CASEPATH = case_path
        self.DEBUGMODE = debug_mode

        self.VARTYPE = {}
        self.DIM = {}
        self.INIT = {}
        
        self._build_variable_type_dict()
        self._load_topo_variables()
        self._get_initial_profile()        
        self._get_date_time()
        self._build_dimension()

        if debug_mode:
            logging.basicConfig(level=logging.DEBUG)


    def _get_date_time(self):
        """
        Generate a time array from 05:00 to the next day's 05:00.

        The generated array contains string representations of times at 2-minute intervals.
        """
        start_time = datetime.datetime.strptime("05:00", "%H:%M")
        end_time = start_time + datetime.timedelta(days=1)  
        steps = 721
        time_delta = (end_time - start_time) / steps
        self.time_array_str = [(start_time + i * time_delta).strftime("%H:%M") for i in range(steps)]

    def _extract_file_info(self, filename):
        """
        Extracts case name, variable type, and time information from the given filename.

        :param filename: The name of the file to extract information from.
        :type filename: str
        :return: Tuple containing case name, variable type, and time information. 
                 Returns None for each element if the pattern does not match.
        :rtype: tuple(str, str, str)
        """
        match = re.match(r'(\w+)\.[CL]\.(\w+)-(\d+)\.nc', filename)
        if match:
            case_name = match.group(1)
            variable_type = match.group(2)
            time_info = match.group(3)
            return case_name, variable_type, time_info
        return None, None, None

    def _record_variables_in_dict(self, file_path, variable_type):
        """
        Records variables from a NetCDF file into the `VARTYPE` dictionary.

        :param file_path: Path to the NetCDF file.
        :type file_path: str
        :param variable_type: Type of the variable to categorize.
        :type variable_type: str
        """
        not_important_variables = {"time", "xc", "yc", "lon", "lat", "zc", "lev"}
        try:
            with xr.open_dataset(file_path) as ds:
                for variable in ds.variables:
                    if variable in self.VARTYPE:
                        if variable in not_important_variables:
                            continue
                        logging.warning(f"{variable} already exists in {self.VARTYPE[variable]}, renaming as {variable}_2 in {variable_type}.")
                        self.VARTYPE[f"{variable}_2"] = variable_type
                        
                    else:
                        # Add the variable and its type to the dictionary
                        self.VARTYPE[variable] = variable_type
                ds.close()
        except Exception as e:
            logging.error(f"Error reading {file_path}: {e}")

    def _build_variable_type_dict(self):
        """
        Walk through the case directory and build a dictionary of variables and their types.

        It searches for NetCDF files and processes files where the time step is '000000' 
        to record their variables in the `VARTYPE` dictionary.
        """
        for root, dirs, files in os.walk(self.CASEPATH):
            for filename in files:
                if filename.endswith(".nc"):  # Search for all .nc files
                    case_name, variable_type, time_info = self._extract_file_info(filename)
                    if time_info == "000000":  # Only process files with time 000000
                        file_path = os.path.join(root, filename)
                        self._record_variables_in_dict(file_path, variable_type)

    def _build_dimension(self):
        """
        Build the spatial dimensions (`xc`, `yc`, `zc`) and save them into the `DIM` dictionary.
        """
        self.DIM["xc"] = self.get_var("xc", 0).to_numpy()
        self.DIM["yc"] = self.get_var("yc", 0).to_numpy()
        self.DIM["zc"] = self.INIT["ZC"]
        self.DIM["zz"] = self.INIT["ZZ"]
        return

    def _load_topo_variables(self):
        """
        Load variables from the 'TOPO.nc' file and add them to the `VARTYPE` dictionary.

        If 'TOPO.nc' is not found, it logs a warning.
        """
        topo_file = os.path.join(self.CASEPATH, 'TOPO.nc')
        if not os.path.exists(topo_file):
            logging.warning(f"TOPO.nc not found in {self.CASEPATH}")
            return

        try:
            with xr.open_dataset(topo_file) as ds:
                for variable in ds.variables:
                    self.VARTYPE[variable] = "TOPO"  # Label these variables as "TOPO"
        except Exception as e:
            logging.error(f"Error reading {topo_file}: {e}")

    def _get_variable_file_type(self, variable_name):
        """
        Get the type of the file associated with the given variable.

        :param variable_name: The name of the variable.
        :type variable_name: str
        :return: The type of file in which the variable is stored or "Variable not found" if unavailable.
        :rtype: str
        """
        return self.VARTYPE.get(variable_name, "Variable not found")

    def _Range_tuple_check(self, Range):
        """
        Check if the range is a tuple or list with exactly six elements (k1, k2, j1, j2, i1, i2).

        :param Range: The range to validate.
        :type Range: tuple or list
        :raises ValueError: If `Range` is not a tuple/list or does not have six elements.
        """
        if not isinstance(Range, (tuple, list)) or len(Range) != 6:
            raise ValueError("Range must be a tuple or list with 6 elements (k1, k2, j1, j2, i1, i2).")

    # Read initial profile and save to self.INIT
    def _get_initial_profile(self):
        """
        Read the initial profile from the 'fort.98' file and store the extracted data in the `INIT` dictionary.

        It parses columns such as RHO, THBAR, PBAR, PIBAR, and QVBAR, stopping when the 'UG(K)' section is found.
        """
        data_array = []
        
        # Open the file for reading
        with open(self.CASEPATH + "/fort.98", 'r') as file:  # Replace 'datafile.txt' with your actual file name
            reading_data = False
            flag = False
            for line in file:
                # Check for the start of the data section
                if re.match(r'^\s*K,\s*RHO\(K\)', line):
                    reading_data = True
                    flag = False
                    continue
        
                # Stop reading data when the next set of equal signs appears
                if reading_data and re.match(r'^\s*={5,}', line):  # Matches a line with 5 or more "="
                    continue
        
                # Read and process data lines after the header
                if reading_data:
                    if re.match(r'^\s*\d+\s+', line):  # Matches lines with data starting with a number
                        # Split the line into values
                        values = line.split()
                        # Convert values to appropriate types (float)
                        values = list(map(float, values))
                        # Append to the data array
                        data_array.append(values)

                if re.match(r'^\s*K,\s*UG\(K\)', line):
                    break

        data_array = np.array(data_array)
        self.INIT["RHO"] = data_array[:, 1]
        self.INIT["THBAR"] = data_array[:, 2]
        self.INIT["PBAR"] = data_array[:, 3]
        self.INIT["PIBAR"] = data_array[:, 4]
        self.INIT["QVBAR"] = data_array[:, 5]

        # get zc and zz
        with open(self.CASEPATH + "/fort.98", 'r') as file:
            in_data_section = False
            out_data_section = False
            zc_zt_data = []
            for line in file:
                # Skip the ===== after the header
                if out_data_section:
                    out_data_section = False
                    continue

                if re.match(r'^\s*K,\s*ZZ\(K\)', line):
                    in_data_section = True
                    out_data_section = True
                    continue

                # Stop processing if we reach the end marker for the section
                if in_data_section and re.match(r'^\s*={5,}', line):  # Matches a line with 5 or more "="
                    break

                # If we're in the data section, extract relevant ZC and ZT values
                if in_data_section:
                    # Match columns based on expected data format
                    match = re.match(r"\s*\d+\s+([0-9.]+)\s+([0-9.]+)", line)
                    if match:
                        zc_value = float(match.group(1))  # ZC (ZZ(K)) column
                        zt_value = float(match.group(2))  # ZT (ZT(K)) column
                        zc_zt_data.append([zc_value, zt_value])
        zc_zt_data = np.array(zc_zt_data)
        self.INIT["ZC"] = np.array(zc_zt_data)[:-1,0]
        self.INIT["ZZ"] = zc_zt_data[:-1,1]

    def get_var(self, 
                var, 
                time, 
                domain_range=(None, None, None, None, None, None), # (k1, k2, j1, j2, i1, i2)
                numpy=False, 
                compute_mean=False, 
                axis=None):
        """
        Get a variable's data at a specified time and domain range.

        This function searches for the appropriate file based on variable type and time step. 
        It supports optional domain range filtering, and the result can be returned as a NumPy array.

        :param var: Name of the variable to retrieve.
        :type var: str
        :param time: Time step for which the variable data is requested.
        :type time: int
        :param domain_range: Tuple specifying the range in each dimension (k1, k2, j1, j2, i1, i2), defaults to (None, None, None, None, None, None).
        :type domain_range: tuple, optional
        :param numpy: Whether to return the data as a NumPy array, defaults to False.
        :type numpy: bool, optional
        :param compute_mean: Whether to compute the mean of the variable data, defaults to False.
        :type compute_mean: bool, optional
        :param axis: Axis or axes along which the mean is computed, defaults to None.
        :type axis: int or tuple of ints, optional
        :return: The variable data, either as a NumPy array or as xarray data depending on options.
        :rtype: numpy.ndarray or xarray.DataArray

        Example:
            >>> import numpy as np
            >>> import vvmtools
            >>> my_vvmtool = vvmtools.analyze.DataRetriever(case_path="path/to/case")
            >>> u = my_vvmtool.get_var("u", 0, numpy=True)
            >>> u_mean = my_vvmtool.get_var("u", 0, numpy=True, compute_mean=True)
            >>> u_mean_along_x = my_vvmtool.get_var("u", 0, numpy=True, compute_mean=True, axis=1)
        """
        
        # Find the file associated with the given variable and time
        self._Range_tuple_check(domain_range)
        
        variable_type = self._get_variable_file_type(var)
        if self.DEBUGMODE:
            print(f"Variable type: {variable_type}")
        if variable_type == "Variable not found":
            print(f"Variable {var} not found in the dataset.")
            return None
        

        if variable_type == "TOPO":
            # Special case for TOPO variables, always in TOPO.nc
            topo_file = os.path.join(self.CASEPATH, 'TOPO.nc')
            try:
                ds = xr.open_dataset(topo_file)
                if var in ds.variables:
                    variable_data = ds[var].copy()  # Get the variable data
                    ds.close()
                    return variable_data
                else:
                    ds.close()
            except Exception as e:
                print(f"Error reading {topo_file}: {e}")
                return None
        else:
            
            # Construct the expected filename pattern for the given variable and time
            file_pattern = f"{variable_type}-{'{:06d}'.format(time)}.nc"
            regex_pattern = f".*{file_pattern}$"  # Convert glob pattern to regex
            if self.DEBUGMODE:
                print(f"Regex Pattern: {regex_pattern}")


            # Search for the file in the case path
            for root, dirs, files in os.walk(self.CASEPATH):
                for filename in files:
                    if re.match(regex_pattern, filename):
                        if self.DEBUGMODE:
                            print(f"File found: {filename}")
                        # Uncomment the following block to open and read the file
                        file_path = os.path.join(root, filename)
                        try:
                            ds = xr.open_dataset(file_path)
                            if var == "eta_2":
                                var = "eta"
                            if var in ds.variables:
                                k1, k2, j1, j2, i1, i2 = domain_range

                                dims = len(ds[var].indexes)
                                if any(r is not None for r in domain_range):
                                    if dims == 4:
                                        variable_data = ds[var][0, k1:k2, j1:j2, i1:i2].copy()
                                    elif dims == 3:
                                        variable_data = ds[var][0, j1:j2, i1:i2].copy()
                                    else:
                                        print("Please check the variables dimension")
                                else:
                                    variable_data = ds[var].copy()  # Get the variable data
                                ds.close()

                                if numpy:
                                    data = np.squeeze(variable_data.to_numpy())

                                    if compute_mean and axis is not None:
                                        return np.mean(data, axis=axis)
                                    elif compute_mean:
                                        return np.mean(data)
                                    else:
                                        return data

                                
                                return variable_data
                            else:
                                ds.close()
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
                            return None

        print(f"No file found for variable {var} at time {time}.")
        return None


    # Call self.get_var in parallel
    def get_var_parallel(self, 
                         var, 
                         time_steps, # array or list of time
                         domain_range=(None, None, None, None, None, None),  # (k1, k2, j1, j2, i1, i2)
                         compute_mean=False,
                         axis=None, # axis for mean. e.g. (0, 1)
                         cores=5):
        """
        Get variable data for multiple time steps in parallel.

        Uses multiprocessing to parallelize the retrieval of variable data across time steps.

        :param var: The variable name.
        :type var: str
        :param time_steps: List or array of time steps for which to retrieve the variable data.
        :type time_steps: list or array-like
        :param domain_range: Tuple specifying the range in each dimension (k1, k2, j1, j2, i1, i2), defaults to (None, None, None, None, None, None).
        :type domain_range: tuple, optional
        :param compute_mean: Whether to compute the mean of the variable data, defaults to False.
        :type compute_mean: bool, optional
        :param axis: Axis or axes along which the mean is computed, defaults to None.
        :type axis: int or tuple of ints, optional
        :param cores: Number of CPU cores to use for parallel processing, defaults to 5.
        :type cores: int, optional
        :return: The retrieved variable data across time steps.
        :rtype: numpy.ndarray
        :raises TypeError: If `time_steps` is not a list or tuple of integers.

        Example:
            >>> import numpy as np
            >>> import vvmtools
            >>> my_vvmtool = vvmtools.analyze.DataRetriever(case_path="path/to/case")
            >>> domain_range = (None, None, None, None, 64, 128)
            >>> time_steps = np.arange(0, 721, 1)
            >>> u_tzyx = my_vvmtool.get_var_parallel("u", time_steps=time_steps, domain_range=domain_range)
            >>> u_tz_xymean_subdomain = my_vvmtool.get_var_parallel("u", time_steps=time_steps, domain_range=domain_range, compute_mean=True, axis=(1,2))
        """
        self._Range_tuple_check(domain_range)

        if type(time_steps) == np.ndarray:
            time_steps = time_steps.tolist()
        
        if not isinstance(time_steps, (list, tuple)):
            raise TypeError("time_steps must be a list or tuple of integers.")
        
        # Use multiprocessing to fetch variable data in parallel
        with multiprocessing.Pool(processes=cores) as pool:
            results = pool.starmap(self.get_var, [(var, time, domain_range, True, compute_mean, axis) for time in time_steps])
        
        # Combine and return the results
        return np.squeeze(np.array(results))



    def func_time_parallel(self, 
                           func, 
                           time_steps=None, # Signature shows np.arange(0, 721, 1)
                           func_config=None,
                           cores=5):
        """
        Applies a time-dependent function `func` in parallel over a list of time steps. 
        The result is returned as a NumPy array.

        :param func: The time-dependent function to be parallelized. It should accept two arguments: 
                     the time step `t` and a config object (containing any additional parameters).
        :type func: callable
        :param time_steps: List or array of time steps over which to apply the function. Defaults to `np.arange(0, 721, 1)`.
        :type time_steps: list or array-like, optional
        :param func_config: A dictionary or object containing additional parameters for the function.
        :type func_config: dict or object, optional
        :param cores: The number of CPU cores to use for parallel processing, defaults to 20.
        :type cores: int, optional
        :return: The combined result of applying the function to all time steps.
        :rtype: numpy.ndarray
        :raises TypeError: If `time_steps` is not a list or array-like of integers.

        Example:
            >>> import numpy as np
            >>> import vvmtools
            >>> def cal_TKE_land(t, func_config):
            >>>     u = np.squeeze(my_vvmtool.get_var("u", t, numpy=True, domain_range=func_config["domain_range"]))
            >>>     v = np.squeeze(my_vvmtool.get_var("v", t, numpy=True, domain_range=func_config["domain_range"]))
            >>>     w = np.squeeze(my_vvmtool.get_var("w", t, numpy=True, domain_range=func_config["domain_range"]))
            >>>     u_inter = (u[:, :, 1:] + u[:, :, :-1])[1:, 1:] / 2
            >>>     v_inter = (v[:, 1:] + v[:, :-1])[1:, :, 1:] / 2
            >>>     w_inter = (w[1:] + w[:-1])[:, 1:, 1:] / 2
            >>>     TKE = np.mean(u_inter ** 2 + v_inter ** 2 + w_inter ** 2, axis=(1, 2))
            >>>     return TKE
            >>> my_vvmtool = vvmtools.analyze.DataRetriever(case_path="path/to/case")
            >>> func_config = {"domain_range": (None, None, None, None, 64, 128)}
            >>> TKE_land = my_vvmtool.func_time_parallel(func=cal_TKE_land, time_steps=list(range(0, 721, 1)), func_config=func_config)
        """

        # If time_steps is None, use np.arange(0, 721, 1)
        if time_steps is None:
            time_steps = np.arange(0, 721, 1)
        
        if type(time_steps) == np.ndarray:
            time_steps = time_steps.tolist()
            
        if not isinstance(time_steps, (list, tuple)):
            raise TypeError("time_steps must be a list or tuple of integers.")

        # Create a partial function that pre-binds the config to the func
        func_with_config = partial(func, func_config=func_config)

        # Use multiprocessing to fetch variable data in parallel
        with multiprocessing.Pool(processes=cores) as pool:
            results = pool.starmap(func_with_config, [(time, ) for time in time_steps])
        
        # Combine and return the results
        return np.squeeze(np.array(results))
