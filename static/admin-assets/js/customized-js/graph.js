
function GetGraphData(){
    var url = $("#Url").attr("data-url");
    $.ajax({
        url: url,
        dataType: 'json',
        data: {
            'month': $('#months').val(),
            'year': $('#years').val(),
        },
        success: function (data) {
            Highcharts.chart("chart-container", data['users']);
            $('#selected_year').text(data['selected_year']);
            $('#selected_month').text(data['month_name']);
            $("#years option[value='"+data['selected_year']+"']").attr("selected","selected");
            $("#months option[value='"+data['selected_month']+"']").attr("selected","selected");
        }
    });
}
GetGraphData();


for (i = new Date().getFullYear(); i > new Date().getFullYear() - 5; i--)
{
    $('#years').append($('<option />').val(i).html(i));
    $('#r_years').append($('<option />').val(i).html(i));
}


function GetRentersGraphData(){
    var url = $("#Url1").attr("data-url");
    $.ajax({
        url: url,
        dataType: 'json',
        data: {
            'month': $('#r_months').val(),
            'year': $('#r_years').val(),
        },
        success: function (data) {
            Highcharts.chart("chart-container1", data['users']);
            $('#r_selected_year').text(data['selected_year']);
            $('#r_selected_month').text(data['month_name']);
            $("#r_years option[value='"+data['selected_year']+"']").attr("selected","selected");
            $("#r_months option[value='"+data['selected_month']+"']").attr("selected","selected");
        }
    });
}
GetRentersGraphData();