## Code Files and Datasets

**Google OR.py:** This file contains the constraint programming model built using Google OR-Tools solver to find matches.

**Gurobi.py:** This file contains the constraint programming model built using the Gurobi solver to find matches.

**Data generator.py:** This file contains the Python code synthetic data creation.

**Data_preprocesser.py:** This file contains the Python code for the data preprocessor.

**Datasets:** The "Datasets" folder contains datasets of different sizes for testing.

**Postcode Datasets:** The "Datasets" folder contains a dataset of Postcodes for data_genrator.

## Usage Instructions- Solvers

### Step 1: Edit the Code
- Open the Python code file you wish to use in a text editor or integrated development environment (IDE) of your choice.

### Step 2: Specify the Dataset
- In the code, locate the following lines:

    ```python
    drivers_df = pd.read_excel('Datasets/Filtered(15).xlsx', sheet_name='Driver')
    riders_df = pd.read_excel('Datasets/Filtered(15).xlsx', sheet_name='Rider')
    shifters_df = pd.read_excel('Datasets/Filtered(15).xlsx', sheet_name='Shifter')
    ```

- Replace `'Datasets/Filtered(15).xlsx'` with the path to the dataset you want to use. For example, if you want to use "Filtered(100).xlsx," change it to `'Datasets/Filtered(100).xlsx'`.

### Step 3: Set the Tolerance
- You can adjust the tolerance level for distance comparisons. In the `solve` function call, there's a parameter named `tolerance`. Change its value to control the acceptable distance for matching (default is set to 1 km).

### Step 4: Run the Code
- Open a terminal or command prompt.

### Step 5: Execute the Code
- Run the code using the Python interpreter with the following command:

    ```bash
    python file_name.py
    ```

  Replace `file_name.py` with the name of the Python script file.

### Step 6: View the Output
- The code will execute and print results to the terminal or command prompt.
- You'll see information about the optimal solution found, the objective value, the number of nodes explored, and the assignments of drivers, riders, and shifters.

Repeat these steps for each dataset you want to analyze. The code should work with datasets of varying sizes as long as they have the same format as "Filtered(15).xlsx" and are named accordingly.

## Usage Instructions- Data

### Data generator: To create a new synthetic dataset, just run the script with the required amount of entries in the 'num_entries' option.
### Data preprocessing: To preprocess the dataset, just locate the following lines:

```python
drivers_df = pd.read_excel(Dataset.xlsx', sheet_name='Driver')
riders_df = pd.read_excel('Dataset.xlsx', sheet_name='Rider')
shifters_df = pd.read_excel('Dataset.xlsx', sheet_name='Shifter')
```
- Replace `'Dataset.xlsx'` with the path to the dataset you want to preprocess. For example, if you want to use "Dataset(100).xlsx," change it to `'Dataset(100).xlsx'`.
