const $ = require('jquery');
const workflowDict = require('./experiment_results.json');

$(function(){
    const workflows = Object.entries(workflowDict).forEach(([dispatch_id,dict])=>{
        console.log(dispatch_id,dict);

        const wrapper = $('<div style="margin: 2rem"></div>')
        const table = $('<table></table>');

        const columns = $('<tr></tr>');
        const rows = $('<tr></tr>');

        columns.append('<th>Task</th>');
        columns.append('<th>Time</th>')


        Object.entries(dict).forEach(([label,value]) => {
            rows.append($('<th></th>').text(label));
            rows.append($('<th></th>').text(value));
        })



        table.append(columns);
        table.append(rows);


        wrapper.append(`<h2>Workflow #${dispatch_id}</h2>`)
        wrapper.append(table);
        $('#reports').append(wrapper);
    })

});
