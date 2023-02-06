#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
from pathlib import Path

import pandas as pd
import yaml

# In[57]:


benchmarks = os.listdir("benchmark_results")

for benchmark_name in benchmarks:
    benchmark_dir = Path("benchmark_results") / benchmark_name
    ct_results = []
    noct_results = []

    if not benchmark_dir.is_dir():
        print("Skipping {} as it is not a directory".format(benchmark_name))
        continue

    for branch in os.listdir(benchmark_dir):
        branch_dir = benchmark_dir / branch
        if not branch_dir.is_dir():
            continue
        for filename in os.listdir(branch_dir):
            if os.path.isdir(branch_dir / filename):
                continue
            with open(branch_dir / filename, "r") as f:
                d = yaml.safe_load(f)
                d["branch"] = branch
                if d["ct"]:
                    ct_results.append(d)
                else:
                    noct_results.append(d)

    results = ct_results + noct_results
    csvfile = f"{benchmark_name}_ttwc.csv"
    if results:
        pd.DataFrame(results).to_csv(benchmark_dir / csvfile, index=False)
        print("Writing results for {} to {}".format(benchmark_name, csvfile))
