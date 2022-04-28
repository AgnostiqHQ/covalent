const $ = require('jquery');
const workflowDict = require('./test.json');

$(function(){
    const workflows = Object.entries(workflowDict).forEach(([dispatch_id,dict])=>{
        console.log(dispatch_id,dict);

        const wrapper = $('<div style="margin: 2rem"></div>')
        const table = $('<table></table>');

        const columns = $('<tr></tr>');
        Object.keys(dict).forEach(col_label => {
            columns.append($('<th></th>').text(col_label));
        })

        const rows = $('<tr></tr>');

        Object.values(dict).forEach(row_val => {
            rows.append($('<td></td>').text(row_val));
        })

        table.append(columns);
        table.append(rows);


        wrapper.append('<h3></h3>').text(`Workflow #${dispatch_id}`)
        wrapper.append(table);
        $('#reports').append(wrapper);
    })

});
