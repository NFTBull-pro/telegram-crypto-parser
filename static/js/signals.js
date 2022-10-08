var table = null;

$(document).ready(function () {
    table = $('#signals-data-table').DataTable({
        "order": [[0, "desc"]],
        "columnDefs": [
            {
                'targets': [0],
                'orderable': true,
            },
            {
                'targets': '_all',
                'orderable': false,
            }
        ]
    });

    // Add event listener for opening and closing details
    $('#signals-data-table tbody').on('click', 'tr.main-signal-tr', function () {
        var tr = $(this).closest('tr');
        var signal_id = $(tr).data("signal_id");
        var row = table.row(tr);

        if (row.child.isShown()) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            // row.child( format(row.data()) ).show();
            // tr.addClass('shown');
            if (signal_id) {
                fetch(window.location.href + `/${signal_id}`)
                    .then((response) => {
                        return response.json();
                    })
                    .then((data) => {
                        if (data['status'] == 200) {

                            var child_table = `<table class="signal-open-table" cellpadding="5" cellspacing="0" border="0" style="width: 100%;">`;

                            child_table += '<div class="signal-open-table-header">Info about signal</div>'

                            if ('json' in data) {
                                Object.entries(data['json']).forEach(([key, value]) => {
                                    child_table +=
                                        '<tr>' +
                                        '<td>' + key + '</td>' +
                                        '<td>' + value + '</td>' +
                                        '</tr>';

                                });
                            }

                            if ('error' in data) {
                                child_table +=
                                    '<tr>' +
                                    '<td>Error</td>' +
                                    '<td style="white-space: pre-wrap;">' + data['error'] + '</td>' +
                                    '</tr>';
                            }

                            child_table +=
                                '<tr>' +
                                '<td>Message Text</td>' +
                                '<td style="white-space: pre-wrap;">' + data['text'] + '</td>' +
                                '</tr>';

                            child_table += `</tbody></table></div>`;

                            row.child(child_table, 'p-0 signal-open-tr').show();
                            tr.addClass('shown');
                        } else {
                            alert('Произошла ошибка');
                        }
                    });
            };
        }
    });

    $('#channel_filter').change(function () {
        var channel = $(this).val();
        table.column(1).search(channel).draw();
    });

    $('#response_filter').change(function () {
        $.fn.dataTable.ext.search.pop();

        var response_status = $(this).val();
        if (response_status == 'success') {
            $.fn.dataTable.ext.search.push(success_response_filter);
        } else if (response_status == 'error') {
            $.fn.dataTable.ext.search.push(error_response_filter);
        }

        table.draw();
    });
});

var success_response_filter = function (settings, searchData, index, rowData) {
    var row = table.row(index);
    return !row.nodes().to$().hasClass('error-signal');
}

var error_response_filter = function (settings, searchData, index, rowData) {
    var row = table.row(index);
    return row.nodes().to$().hasClass('error-signal');
}