# Tutorial guidelines

The most important principles to follow when writing a tutorial is that:

1. It should be as self contained as possible.
2. It should be clear and easy to understand.
3. It should execute without any errors.

## Folder structure and file naming

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

**Note**: Covalent should be added as a requirement in `requirements.txt` but without a version number.

For example, here's an example `requirement.txt`:

```
covalent
matplotlib==3.6.3
pennylane==0.25.1
scikit-learn==1.0.2
torch==1.13.1
```

## Tutorial requirements

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

Here's an example:


<div align="center">
<img src="./source/_static/tutorial_guideline_requirements.png" style="width: 60%; height: 60%" />
</div>

## File paths and other configurable values

1. File paths, provisioned cloud resource names such as AWS s3 buckets need to be configurable.

**Note**: It is imperative that there are no hard coded variables that need to be configured on an individual user basis.


2. The environment variables should be read near the top of the tutorial using `os.getenv()`. For example,

```
batch_s3_bucket_name = os.getenv("BATCH_S3_BUCKET_NAME")
image_folder = os.getenv("IMAGE_FOLDER")

```

Furthermore, include reasonable default values when reading in the environment variables.


## Memory and compute resource config values

Specify the memory and compute resources required when starting Covalent using. It's important to set the correct defaults in this case, since these values will be required when starting Covalent on the self-hosted instance where the tutorials will be run as functional tests.

```{code}
COVALENT_NUM_WORKER = os.getenv("COVALENT_NUM_WORKER", 4)
COVALENT_MEM_WORKER = os.getenv("COVALENT_MEM_WORKER", "2GB")
COVALENT_THREADS_PER_WORKER = os.getenv("COVALENT_THREADS_PER_WORKER", 1)

```

## Assert statements checking that workflow executed successfully


## Upload data if it's needed


## Tutorial cleanup and formatting

1. `requirements.txt` files with all required packages and version numbers in the assets folder corresponding to the tutorial.
2. The contents of `requirements.txt` file also need to be printed out in one of the tutorial cells at the top.
3. There should be no hard coded file paths.
4. Read in all required environment variables at one of the top cells using `os.getenv()`.
5. Ensure that default values or placeholders are set for each of the environment variables that are being read in.

7. For every `covalent.get_result()` query, there should be a corresponding `assert result.status` statement to ensure that the workflow execution was successful.
8. If AWS resources (for example s3 bucket with training and test dataset for a machine learning workflow) are required to run the tutorial, then there should be a step where the data is being uploaded before it is used.
9. Check that the notebook is well formatted.
10. Ensure that there are no empty cells lingering at the end of the tutorial.
