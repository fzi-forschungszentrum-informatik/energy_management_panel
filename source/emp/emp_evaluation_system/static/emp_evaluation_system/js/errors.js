var alert_element_before_message = '<div class="alert alert-danger alert-dismissible fade show" role="alert"><strong>Error:</strong> '
var alert_element_after_message = '<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button></div>'

/**
 * Prints a message as alert in the 'errir.field' div.
 * Therefore, all old alters are appended by the new alert and printed.
 * @param {*} message Takes a alert message
 */
function showError(message) {
    $('#error-field').html($('#error-field').html() + createAlertElement(message));
}

/**
 * Builds an alert element out of a message.
 * @param {*} message The alert message.
 */
function createAlertElement(message) {
    return alert_element_before_message + message + alert_element_after_message;
}