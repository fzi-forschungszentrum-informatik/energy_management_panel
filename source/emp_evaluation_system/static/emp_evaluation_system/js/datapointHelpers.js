function getLastDatapointValueOfSet(set) {
    return set[Object.keys(set).length - 1].value
}

function getLastXDatapointValuesOfSet(set, x) {
    var filteredSet = set.filter(function(el, index) {
        return index >= set.length - x;
    });
    return $.map(filteredSet, (n) => n.value);   
}