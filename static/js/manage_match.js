

// REGISTER MATCH

used_id = {"1" : "None", "2" : "None", "3" : "None", "4" : "None", "5" : "None"}

///////////////////////////////////////////////////////////////////////////////////

function show_nb_vab(nb_vab) {
    let name

    for (let i = 1; i <= 5; i++)
    {
        name = "ally_" + i
        if (i <= nb_vab) {
            $(`label[for="${name}"]`).show();
            $(`select[id="${name}"]`).show();
        }
        else {
            $(`label[for="${name}"]`).hide();
            $(`select[id="${name}"]`).hide();
            $(`select[id="${name}"]`).val("")
            change_player_list("None", i)
            used_id[i] = "None"
        }
    }
}

///////////////////////////////////////////////////////////////////////////////////

function make_options_invisible(id_player) {
    for (let i = 1; i <= 5; i++) {
        $(`select[id="ally_${i}"] option[value="${id_player}"]`).hide();
    }}

function make_options_visible(id_player) {
    for (let i = 1; i <= 5; i++) {
        $(`select[id="ally_${i}"] option[value="${id_player}"]`).show();
    }
}

function change_player_list(id_player, nb_select) {
    let options

    for (let i = 1; i <= 5; i++) {
        options = document.getElementById("ally_" + i).options
        if (nb_select === i) {
            if (used_id[i] !== "None")
                make_options_visible(used_id[i])
        }
        else if (id_player !== "None") {
            make_options_invisible(id_player)
        }
    }
    used_id[nb_select] = `${id_player}`
}

///////////////////////////////////////////////////////////////////////////////////

function get_match_datas() {
    let match = {}

    match["atk_def"] = $('select[id = "atk_def"]').val()
    match["nb_ally"] = $('select[id = "nb_ally"]').val().split("_")[2]
    match["nb_vab"] = $('select[id = "nb_vab"]').val().split("_")[2]
    match["nb_ennemy"] = $('select[id = "nb_ennemy"]').val().split("_")[2]
    match["entity"] = $(`select[id = "entity"]`).val()
    match["ally_1"] = $('select[id = "ally_1"]').val()
    match["ally_2"] = $('select[id = "ally_2"]').val()
    match["ally_3"] = $('select[id = "ally_3"]').val()
    match["ally_4"] = $('select[id = "ally_4"]').val()
    match["ally_5"] = $('select[id = "ally_5"]').val()
    match["bonus_mult"] = $('select[id = "bonus_mult"]').val()
    return match
}

function check_match(match, mode) {
    let player
    let screen

    if (match["nb_vab"] > match["nb_ally"])
        return ("Tu as mis plus de Vàb que d'alliers")
    for (let i = 1; i <= match["nb_vab"]; i++) {

        if (match["ally_" + i] === "None" || match["ally_" + i] == null) {
            return ("Il manque un nom dans la liste des alliers")
        }
        player = match["ally_" + i]
        for (let k = 1; k <= match["nb_vab"]; k++) {
            if (match["ally_" + k] === "None" || match["ally_" + k] != null) {
                if (match["ally_" + k] === player && k !== i)
                    return ("Il y a plusieurs fois le même pseudo")
            }
        }
    }
    if (mode != "ADMIN") {
        screen = $('input[id = screen]').val();
        if (screen.length === 0)
            return ("Il manque ton screen")
        if (screen.substr(screen.length - 4) !== ".jpg" &&
            screen.substr(screen.length - 4) !== ".png")
            return ("Ton fichier est invalide, seul les fichier png et jpg sont acceptés");
    }
    return ("None")
}

function button_confirm() {
    let match
    let res

    match = get_match_datas();
    if ((res = check_match(match, "None")) !== "None") {
        alert(res)
    }
    else {
        $('div[name = validate_match]').show();
        document.getElementById("confirm_match").disabled = true;
        document.getElementById("modify_match").disabled = false;
        document.getElementById("validate_button").disabled = false;
        document.getElementById("fieldset_register").setAttribute("disabled", true)
    }
}

///////////////////////////////////////////////////////////////////////////////////

function button_modify() {
    document.getElementById("confirm_match").disabled = false;
    document.getElementById("modify_match").disabled = true;
    document.getElementById("validate_button").disabled = true;
    document.getElementById("fieldset_register").removeAttribute("disabled")
}

///////////////////////////////////////////////////////////////////////////////////

function button_validate() {
    // document.getElementById("validate_button").disabled = true;
    document.getElementById("modify_match").disabled = true;
    // document.getElementById("confirm_match").disabled = false;
    document.getElementById("fieldset_register").removeAttribute("disabled")
}

///////////////////////////////////////////////////////////////////////////////////

function nb_vab_ops(nb_vab_str) {

    let nb_vab = parseInt(nb_vab_str.split('_')[2])
    let nb_ally = parseInt($('select[id="nb_ally"] option:selected').text())
    show_nb_vab(nb_vab)
    if (nb_ally < nb_vab)
        $('select[id="nb_ally"]').val("nb_ally_" + nb_vab);
}

///////////////////////////////////////////////////////////////////////////////////

function nb_ally_ops(nb_ally_str) {

    let nb_ally = parseInt(nb_ally_str.split('_')[2])
    let nb_vab = parseInt($('select[id="nb_vab"] option:selected').text())
    if (nb_ally < nb_vab) {
        $('select[id="nb_vab"]').val("nb_vab_" + nb_ally);
        show_nb_vab(nb_ally)
    }
}

///////////////////////////////////////////////////////////////////////////////////

function init_register_match() {
    nb_vab_ops($('select[id="nb_vab"]').val())
    nb_ally_ops($('select[id="nb_ally"]').val())
    document.getElementById("confirm_match").disabled = false;
    document.getElementById("modify_match").disabled = true;
    document.getElementById("validate_button").disabled = true;
}

// COPIE DU CLIPBOARD POUR UPLOAD

const fileInput = document.getElementById("screen");

window.addEventListener('paste', e => {
    fileInput.files = e.clipboardData.files;
});








// MODIFY MATCH

function modify_button_confirm() {
    let match
    let res

    match = get_match_datas();
    if ((res = check_match(match, "ADMIN")) !== "None") {
        alert(res)
    }
    else {
        // $('div[name = validate_match]').show();
        document.getElementById("confirm_match").disabled = true;
        document.getElementById("modify_match").disabled = false;
        document.getElementById("submit_modify_match").disabled = false;
        document.getElementById("fieldset_register").setAttribute("disabled", true)
    }
}

function modify_button_modify() {
    document.getElementById("confirm_match").disabled = false;
    document.getElementById("modify_match").disabled = true;
    document.getElementById("submit_modify_match").disabled = true;
    document.getElementById("fieldset_register").removeAttribute("disabled")
}

function modify_button_validate() {
    // document.getElementById("validate_button").disabled = true;
    document.getElementById("modify_match").disabled = true;
    // document.getElementById("confirm_match").disabled = false;
    document.getElementById("fieldset_register").removeAttribute("disabled");
}

function cancel_delete_match() {
    $("#alert_delete_msg").hide()
    $("#submit_delete_match").hide()
    $("#js_cancel_delete_match").hide()
}

function delete_match() {
    $("#alert_delete_msg").show()
    $("#submit_delete_match").show()
    $("#js_cancel_delete_match").show()
}

function init_modify_match(ally_1, ally_2, ally_3, ally_4, ally_5, nb_ally,
                           nb_vab, nb_ennemy, side, entity, commentary) {

    $('select[id="nb_ally"]').val("nb_ally_" + nb_ally)
    $('select[id="nb_vab"]').val("nb_vab_" + nb_vab)
    $('select[id="nb_ennemy"]').val("nb_ennemy_" + nb_ennemy)
    $('select[id="side"]').val(side)
    $('select[id="entity"]').val(entity)
    $('select[id="bonus_mult"]').val("1")
    nb_vab_ops($('select[id=nb_vab]').val())
    nb_ally_ops($('select[id=nb_ally]').val())
    if (commentary != "None") {
        $('input[id="commentary"]').val(commentary)
    }

    $(`select[id="ally_1"]`).val(ally_1)
    change_player_list(ally_1, 1)
    used_id[1] = ally_1

    $(`select[id="ally_2"]`).val(ally_2)
    change_player_list(ally_2, 2)
    used_id[1] = ally_2

    $(`select[id="ally_3"]`).val(ally_3)
    change_player_list(ally_3, 3)
    used_id[1] = ally_3

    $(`select[id="ally_4"]`).val(ally_4)
    change_player_list(ally_4, 4)
    used_id[1] = ally_4

    $(`select[id="ally_5"]`).val(ally_5)
    change_player_list(ally_5, 5)
    used_id[1] = ally_5

}