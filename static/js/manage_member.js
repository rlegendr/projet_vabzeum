function cancel_delete_member() {
    $("#alert_delete_msg").hide()
    $("#submit_delete_member").hide()
    $("#js_cancel_delete_member").hide()
}

function delete_member() {
    $("#alert_delete_msg").show()
    $("#submit_delete_member").show()
    $("#js_cancel_delete_member").show()
}