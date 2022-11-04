document.addEventListener("DOMContentLoaded", function (event) {

    const showNavbar = (toggleId, navId, bodyId, headerId) => {
        const toggle = document.getElementById(toggleId),
            nav = document.getElementById(navId),
            bodypd = document.getElementById(bodyId),
            headerpd = document.getElementById(headerId)

        // Validate that all variables exist
        if (toggle && nav && bodypd && headerpd) {
            toggle.addEventListener('click', () => {
                // show navbar
                nav.classList.toggle('show')
                // change icon
                toggle.classList.toggle('bx-x')
                // add padding to body
                bodypd.classList.toggle('body-pd')
                // add padding to header
                headerpd.classList.toggle('body-pd')
            })
        }
    }

    showNavbar('header-toggle', 'nav-bar', 'body-pd', 'header')

    /*===== LINK ACTIVE =====*/
    const linkColor = document.querySelectorAll('.nav_link')

    function colorLink() {
        if (linkColor) {
            linkColor.forEach(l => l.classList.remove('active'))
            this.classList.add('active')
        }
    }
    linkColor.forEach(l => l.addEventListener('click', colorLink))

    // Your code to run since DOM is loaded and ready
});

var activable = document.getElementById("activable"),
    activar_op = document.getElementById("activador");

function habilitar() {
    activable.classList.remove("disabled");
}

activar_op.addEventListener('click', habilitar, true)



// Form dinamico 1

let form_count = Number($("[name=extra_field_count]").val());
// get extra form count so we know what index to use for the next item.

$("#add-another").click(function () {
    form_count++;

    let element = $('<input type="text"/>');
    element.attr('name', 'extra_field_' + form_count);
    $("#forms").append(element);
    // build element and append it to our forms container

    $("[name=extra_field_count]").val(form_count);
    // increment form count so our view knows to populate 
    // that many fields for validation
})


// Form dinamico 2
const addMoreBtn = document.getElementById('add-more')
addMoreBtn.addEventListener('click', add_new_form)
function add_new_form(args) {
    console.log(args)
}