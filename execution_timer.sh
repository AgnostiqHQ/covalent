#!/bin/bash
echo 'Starting Covalent'
covalent start
retVal=$?
if [ $retVal != 0 ]
then
  echo "Covalent failed to start"
else
  echo 'Covalent is running'
fi

echo 'Starting Dispatch...'

python3 tests/example_dispatch.py # path to dispatch file
echo 'Execution timer succeeded'
echo 'Collecting Data...'

log_files=('covalent_data/out.log' 'covalent_dispatcher/out.log' 'covalent_queuer/out.log' 'covalent_results/out.log'
'covalent_runner/out.log' 'covalent_ui/out.log')
for i in "${!log_files[@]}"; do
  lines_with_metadata=0
  while IFS= read -r line; do
    if [[ $line =~ "Metadata" ]]; then
      lines_with_metadata=$((lines_with_metadata+1))
    fi
  done < "${log_files[i]}"
  echo
  echo "#metadata lines in ${log_files[i]}, $lines_with_metadata " >> timer_output.csv
done

# TO DO: Export the total execution time per endpoint

