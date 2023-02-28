#####################
Troubleshooting guide
#####################

This page is dedicated to solutions to common issues encountered when using the Covalent platform.

------------------
Covalent debugging
------------------

Users can get more information on the status of their Covalent workflow by starting the Dispatcher server with `covalent start -d` and then running the following command in the terminal:

```{code-block}
covalent logs
```

Note that in the future, these logs will be available in the Covalent UI.

--------------------------------------------
Increase open file limit for large workflows
--------------------------------------------

MacOS users can experience errors of the form `Too many open files in system`. In order to resolve this issue simply change the open file limit via the terminal command `ulimit -n 10240` and restart Covalent.


--------------------------
Dask cluster worker memory
--------------------------

Some tasks can fail to execute due to insufficient memory allocated to each worker. This can be resolved by increasing the memory allocated to each worker via:

```{code-block}
covalent start -n 4 -m "2GB" -d
```
