#!/usr/bin/env python
# Copyright 2021 Agnostiq Inc.
#
# This file is part of Covalent.
#
# Licensed under the Apache License 2.0 (the "License"). A copy of the
# License may be obtained with this software package or at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Use of this file is prohibited except in compliance with the License.
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
