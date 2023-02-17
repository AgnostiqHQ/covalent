# Tutorial guidelines

The most important principles to follow when writing a tutorial is that:

1. It should be as self contained as possible. (I don't mean the technical material but rather the Covalent/Executor/Python package resources).
2. It should be clear and easy to understand.
3. It should execute without any errors.

## Guidelines

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
