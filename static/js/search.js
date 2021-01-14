$(function () {
    $('#search_nickname').keyup(function () {
        let search
        let nb_member
        let scanned_member
        let elem

        search = $('input[id="search_nickname"]').val().toLowerCase()
        nb_member = $('tr[id^="member_list_tr_"]')
        for (let i = 1; i <= nb_member.length; i++) {
            scanned_member = "member_list_tr_" + i
            elem = $(`tr[id="${scanned_member}"] td[id="member_nickname"]`).text().toLowerCase()
            $(`select[id="${name}"]`).hide()
            if (elem.startsWith(search)) {
                $(`tr[id="${scanned_member}"]`).show()
            } else {
                $(`tr[id="${scanned_member}"]`).hide()
            }
        }
    });
});

$(function () {
    $('#search_id_match').keyup(function () {
        let search

        search = parseInt($('input[id="search_id_match"]').val())
        if (Number.isInteger(search)) {
            $('#button_search_id_match').prop("disabled", false)
        } else {
            $('#button_search_id_match').prop("disabled", true)
        }
    })
})