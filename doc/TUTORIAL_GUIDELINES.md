# Tutorial guidelines

The most important principles to follow when writing a tutorial is that:

1. It should be as self contained as possible.
2. It should be clear and easy to understand.
3. It should execute without any errors.

## Guidelines

### Folder structure and file naming

Every tutorial should be inside a folder corresponding to the _tutorial name_ and contain:
1. A subfolder named `assets`
2. Jupyter notebook called `source.ipynb`
3. A requirements file, `requirements.txt` will every required python package and version number to execute the tutorial.

```
- tutorial_example
    - assets
        - data.npy
        - requirements.txt
        - figures.png
    - source.ipynb
```

```{note}
Covalent should be added as a requirement in `requirements.txt` but without a version number.
```

For example, here's an example `requirement.txt`:

```
covalent
matplotlib==3.6.3
pennylane==0.25.1
scikit-learn==1.0.2
torch==1.13.1
```

### Tutorial requirements

1. Include a print statement listing the packages in the requirements file before the import statements via:

```{code}
with open("./requirements.txt", "r") as file:
    for line in file:
        print(line.rstrip())

```

2. There should be a commented out line in the cell below that installs all the packages listed in `requirements.txt`:

```{code}
# Install necessary packages
# !pip install -r ./requirements.txt

```

Here's an example from a tutorial:

```{figure} ./_static/tutorial_guideline_requirements.png
---
height: 150px
name: requirements-fig
---
Here is my figure caption!
```




1. `requirements.txt` files with all required packages and version numbers in the assets folder corresponding to the tutorial.
2. The contents of `requirements.txt` file also need to be printed out in one of the tutorial cells at the top.
3. There should be no hard coded file paths.
4. Read in all required environment variables at one of the top cells using `os.getenv()`.
5. Ensure that default values or placeholders are set for each of the environment variables that are being read in.
6. Specify the memory and compute resources required when starting Covalent.
7. For every `covalent.get_result()` query, there should be a corresponding `assert result.status` statement to ensure that the workflow execution was successful.
8. If AWS resources (for example s3 bucket with training and test dataset for a machine learning workflow) are required to run the tutorial, then there should be a step where the data is being uploaded before it is used.
9. Check that the notebook is well formatted.
10. Ensure that there are no empty cells lingering at the end of the tutorial.
