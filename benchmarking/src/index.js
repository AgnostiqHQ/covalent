const $ = require('jquery');
const workflowDict = require('./experiment_results.json');

$(function(){
    const workflows = Object.entries(workflowDict).forEach(([dispatch_id,dict])=>{
        console.log(dispatch_id,dict);

        const wrapper = $('<div style="margin: 2rem"></div>')
        const table = $('<table></table>');

        const columns = $('<tr></tr>');

        columns.append('<th>Service</th>');
        columns.append('<th>Endpoint</th>');
        columns.append('<th>Task</th>');
        columns.append('<th>Time (ms)</th>')


        Object.entries(dict).forEach(([label,value_dict]) => {
            const endpoint = value_dict.endpoint;
            const task = value_dict.label
            const service = value_dict.service;
            const time_in_ms = value_dict.value*1000;

            console.log(label,value_dict)

            const row = $('<tr></tr>');
            row.append($('<th></th>').text(service));
            row.append($('<th></th>').text(endpoint));
            row.append($('<th></th>').text(task));


            row.append($(`<th style="color: ${time_in_ms>50 ? 'red': 'black'}"></th>`).text(String(time_in_ms)));
            table.append(row);
        })



        table.append(columns);

        wrapper.append(`<h2>Workflow #${dispatch_id}</h2>`)
        wrapper.append(table);
        $('#reports').append(wrapper);
    })

});
