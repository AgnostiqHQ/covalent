import covalent as ct

N = 8
STALL = 1e6
X = 50


@ct.electron
def cpu_workload(stall, x):
    i = 0
    while i < stall:
        x * x
        i += 1


@ct.lattice
def workflow(iterations, stall, x):
    for _ in range(iterations):
        cpu_workload(stall, x)


n_electrons = [2**i for i in range(N)]
execution_time_taken = []
dispatch_ids = [ct.dispatch(workflow)(it, STALL, X) for it in n_electrons]

for d_id in dispatch_ids:
    result = ct.get_result(d_id, wait=True)
    execution_time_taken.append((result.end_time - result.start_time).total_seconds())


print(f"Number of electrons: {n_electrons}")
print(f"Execution time taken: {execution_time_taken}")


# with plt.xkcd():
#     plt.plot(n_electrons, execution_time_taken)
#     plt.xlabel("number of electrons")
#     plt.ylabel("execution time for each workflow")

# plt.show()
