const $ = require('jquery');
const workflowDict = require('./experiment_results.json');

const _get = require('lodash.get');
const _set = require('lodash.set');

const workflowPerformanceMetadata = {};

METADATA_LS_KEY = 'workflowMetadata'

if(!window.localStorage.getItem(METADATA_LS_KEY)){
    window.localStorage.setItem(METADATA_LS_KEY, JSON.stringify({}))
}


// let chartDict = {
//     "label_1": {
//         data: [
//             {
//                 x: 10,
//                 y: 20
//             }, {
//                 x: 15,
//                 y: 10
//             }
//         ],
//     }
// }


$(function(){

    const chartDom = $('#graph');
    const chart = new Chart(chartDom, {
        type: 'scatter',
        data: {
            datasets: []
        },
        responsive: false
    });

    const updateGraph = () => {

        let chartDict = {};
        // chartDict = { label: { data: [{x,y}] }}

        const metadata = JSON.parse(window.localStorage.getItem(METADATA_LS_KEY));

        const colourMap = {
            'vertical': 'red',
            'horizontal': 'blue',
            'hagrid': 'green'
        }

        Object.keys(metadata)
        .filter(dispatchId => dispatchId !== 'None')
        .forEach(dispatchId => {
            const label = _get(metadata,`${dispatchId}.label`, null);
            const numElectrons = _get(metadata,`${dispatchId}.num_electrons`, 0);
            const elapsedTimeInMs = _get(metadata, `${dispatchId}.elapsedTimeInMs`,0)
            if(label && numElectrons && elapsedTimeInMs){
                let dataArr = _get(chartDict, `${label}.data`);
                if(!Array.isArray(dataArr)){
                    dataArr = []
                }
                dataArr.push({
                    x: numElectrons,
                    y: elapsedTimeInMs/1000 // seconds
                })
                _set(chartDict,`${label}.data`,dataArr)
            }
        })

        const datasets = Object.keys(chartDict).map(plotLabel => {
            return ({
                label: plotLabel,
                fill: false,
                borderColor: colourMap[plotLabel] || 'grey',
                tension: 0.1,
                data: chartDict[plotLabel].data
            })
        })
        chart.data.datasets = datasets;
        chart.update();
    }


    const updateWorkflowMetadata = (dispatchId, key, value) => {
        const metadata = JSON.parse(window.localStorage.getItem(METADATA_LS_KEY));
        _set(metadata,`${dispatchId}.${key}`, value)
        window.localStorage.setItem(METADATA_LS_KEY, JSON.stringify(metadata))
        updateGraph()
    }

    const getWorkflowMetadata = (dispatchId, key) => {
        const metadata = JSON.parse(window.localStorage.getItem(METADATA_LS_KEY));
        return _get(metadata, `${dispatchId}.${key}`);
    }

    Object.entries(workflowDict).forEach(([dispatch_id, taskMetadataDict])=>{
        console.log(dispatch_id,taskMetadataDict);

        const wrapper = $('<div style="margin: 2rem"></div>')
        const table = $('<table></table>');

        const columns = $('<tr></tr>');

        columns.append('<th>Service</th>');
        columns.append('<th>Endpoint</th>');
        columns.append('<th>Task</th>');
        columns.append('<th>Time (ms)</th>');

        table.append(columns);

        if(!workflowPerformanceMetadata[dispatch_id]) {
            workflowPerformanceMetadata[dispatch_id] = {
                elapsedTimeInMs: 0
            };
        }

        let startTimeInSeconds = 0;
        let endTimeInSeconds = 0;
        let excludedTimeInMs = 0;

        Object.entries(taskMetadataDict).forEach(([label,value_dict]) => {

            if(label.startsWith('$')) return;
            const endpoint = value_dict.endpoint;
            const task = value_dict.label
            const service = value_dict.service;
            const time_in_ms = value_dict.value*1000;
            const isInitialTask = value_dict.is_initial_task;
            const isFinalTask = value_dict.is_final_task;
            const isExcludedTask = value_dict.is_excluded_task;

            if(isInitialTask){
                startTimeInSeconds = value_dict.start_time_unix;
            }

            if(isFinalTask){
                endTimeInSeconds = value_dict.end_time_unix;
            }

            if(isExcludedTask){
                excludedTimeInMs += time_in_ms;
            }

            console.log(label,value_dict)

            const row = $('<tr></tr>');
            row.append($('<th></th>').text(service));
            row.append($('<th></th>').text(endpoint));
            row.append($('<th></th>').text(task));

            row.append($(`<th style="color: ${time_in_ms>50 ? 'red': 'black'}"></th>`).text(String(time_in_ms)));
            table.append(row);
        })

        workflowPerformanceMetadata[dispatch_id].elapsedTimeInMs = (endTimeInSeconds - startTimeInSeconds)*1000 - (excludedTimeInMs);

        updateWorkflowMetadata(dispatch_id,'elapsedTimeInMs', workflowPerformanceMetadata[dispatch_id].elapsedTimeInMs)

        wrapper.append(`<h2>Workflow #${dispatch_id}</h2>`)
        wrapper.append(`<h3>Elapsed Time [ms]: ${workflowPerformanceMetadata[dispatch_id].elapsedTimeInMs}<h3/>`);


        const inputWrapper = $('<div></div>')
        numElectronsInput = $('<input>').attr({
            type: 'number',
            id: `${dispatch_id}-num-electrons`,
            placeholder: "# of Electrons",
            value:  getWorkflowMetadata(dispatch_id, "num_electrons") || ""
        }).on('keyup',function(e){
            const numElectrons = e.target.value;
            updateWorkflowMetadata(dispatch_id, 'num_electrons', numElectrons)
        })

        labelInput = $('<input>').attr({
            type: 'text',
            id: `${dispatch_id}-label`,
            placeholder: "Plot Label",
            value: getWorkflowMetadata(dispatch_id, "label") || ""
        }).on('keyup',function(e){
            const label = e.target.value;
            updateWorkflowMetadata(dispatch_id, 'label', label)
        })

        inputWrapper.append(labelInput)
        inputWrapper.append(numElectronsInput)

        wrapper.append(inputWrapper);
        wrapper.append(table);
        $('#reports').append(wrapper);
    });



});
