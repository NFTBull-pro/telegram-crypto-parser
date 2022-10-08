$(document).ready(function () {
    "use strict";
    var path = window.location.href;
    $("#layoutSidenav_nav .sb-sidenav a.nav-link").each(function () {
        if (this.href === path) {
            $(this).addClass("active");
        }
    });

    $("#sidebarToggle").on("click", function (e) {
        e.preventDefault();
        $("body").toggleClass("sb-sidenav-toggled");
    });
    $("#search_input").on("keyup", function () {

        var txtValue;
        var filter = $(this).val().toUpperCase();
        var code = document.getElementsByTagName('code');

        for (let i = 0; i < code.length; i++) {
            txtValue = code[i].textContent || code[i].innerText;
            if (txtValue.toUpperCase().indexOf(filter) > -1) {
                code[i].style.display = "";
            } else {
                code[i].style.display = "none";
            }
        }
    });

    var d = $('#code_logs');
    d.scrollTop(d.prop("scrollHeight"));
});