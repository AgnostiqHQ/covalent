#!/usr/bin/env python
# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the GNU Affero General Public License 3.0 (the "License").
# A copy of the License may be obtained with this software package or at
#
#      https://www.gnu.org/licenses/agpl-3.0.en.html
#
# Use of this file is prohibited except in compliance with the License. Any
# modifications or derivative works of this file must retain this copyright
# notice, and modified files must contain a notice indicating that they have
# been altered from the originals.
#
# Covalent is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the License for more details.
#
# Relief from the License may be granted by purchasing a commercial license.

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
