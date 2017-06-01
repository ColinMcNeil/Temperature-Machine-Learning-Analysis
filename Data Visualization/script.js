
$.get('accuracies.csv', function (raw_data) {
    var data = d3.csvParse(raw_data);
    console.log(data)
});