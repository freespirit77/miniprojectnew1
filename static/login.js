// {% if msg %}
//     alert("{{ msg }}")
// {% endif %}
function sign_in() {
    let username = $("#input-username").val()
    let password = $("#input-password").val()

    if (username == "") {
        $("#help-id-login").text("아이디를 입력해주세요.")
        $("#input-username").focus()
        return;
    } else {
        $("#help-id-login").text("")
    }

    if (password == "") {
        $("#help-password-login").text("비밀번호를 입력해주세요.")
        $("#input-password").focus()
        return;
    } else {
        $("#help-password-login").text("")
    }
    $.ajax({
        type: "POST",
        url: "/sign_in",
        data: {
            username_give: username,
            password_give: password
        },
        success: function (response) {
            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token'], {path: '/'});
                window.location.href="/"
            } else {
                alert(response['msg'])
            }
        }
    });
}

function sign_up() {
    //인풋박스에 입력된 값을 받아서
    let username = $("#input-username").val()
    let password = $("#input-password").val()
    let password2 = $("#input-password2").val()
    // let nickname = $("#input-nickname").val()
    console.log(username, password, password2)
    //처음 검사 해주는 것은
    // 아이디를 안눌렀을 떄
    if ($("#help-id").hasClass("is-danger")) {
        alert("아이디를 다시 확인해주세요.")
        return;
    } else if (!$("#help-id").hasClass("is-success")) {//중복확인이 안되어 있을 때 (help-id가 클래스 is-success를 갖고있는지 확인~)!는 반대로
        alert("아이디 중복확인을 해주세요.")
        return;
    }
    //패스워드를 안적었을때
    if (password == "") {
        $("#help-password").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return;
    } else if (!is_password(password)) {
        $("#help-password").text("비밀번호의 형식을 확인해주세요. 영문과 숫자 필수 포함, 특수문자(!@#$%^&*) 사용가능 8-20자").removeClass("is-safe").addClass("is-danger")
        $("#input-password").focus()
        return
    } else {                                    //비밀번호형식이 맞을 때
        $("#help-password").text("사용할 수 있는 비밀번호입니다.").removeClass("is-danger").addClass("is-success")
    }
    //패스워드2
    if (password2 == "") {                      //비밀번호확인 칸에 아무것도 없을때
        $("#help-password2").text("비밀번호를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else if (password2 != password) {         //password2와 password가 다를 떄
        $("#help-password2").text("비밀번호가 일치하지 않습니다.").removeClass("is-safe").addClass("is-danger")
        $("#input-password2").focus()
        return;
    } else {                                    //맞으면 띄워줘라
        $("#help-password2").text("비밀번호가 일치합니다.").removeClass("is-danger").addClass("is-success")
    }

    $.ajax({
        type: "POST",
        url: "/sign_up/save",
        data: {
            username_give: username,
            password_give: password,
            // nickname_give: nickname
        },
        success: function (response) {
            alert("회원가입을 축하드립니다!")
            window.location.replace("/login")
        }
    });
}

//보여지고 있으면 안보이게, 안보여지면 보여지게 해라
//tomato source
function toggle_sign_up() {
    $("#sign-up-box").toggleClass("is-hidden")
    $("#div-sign-in-or-up").toggleClass("is-hidden")
    $("#btn-check-dup").toggleClass("is-hidden")
    $("#help-id").toggleClass("is-hidden")
    $("#help-password").toggleClass("is-hidden")
    $("#help-password2").toggleClass("is-hidden")
    // $("#help-nickname").toggleClass("is-hidden")
}

//아이디, 비밀번호 정규표현식
function is_nickname(asValue) {
    var regExp = /^(?=.*[a-zA-Z])[-a-zA-Z0-9_.]{2,10}$/;
    return regExp.test(asValue);
}

function is_password(asValue) {
    var regExp = /^(?=.*\d)(?=.*[a-zA-Z])[0-9a-zA-Z!@#$%^&*]{8,20}$/;
    return regExp.test(asValue);
}

//아이디 중복체크 함수!
function check_dup() {
    let username = $("#input-username").val() //유저이름을 받음
    console.log(username)
    if (username == "") {//만약에 아무것도 입력 되지 않으면" 아이디를 입력해주세요" 띄워줘라.
        $("#help-id").text("아이디를 입력해주세요.").removeClass("is-safe").addClass("is-danger")
        $("#input-username").focus()
        return;
    }
    if (!is_nickname(username)) {//is_nickname()함수에 맞지 않으면 is-safe나 is-danger를 띄워줘라!
        //hepp-id에다가 text()먹이고 is-safe없애고 is-danger 만들어서 붙여라
        $("#help-id").text("아이디의 형식을 확인해주세요. 영문과 숫자, 일부 특수문자(._-) 사용 가능. 2-10자 길이").removeClass("is-safe").addClass("is-danger")
        $("#input-username").focus()//
        return;
    }
    $("#help-id").addClass("is-loading")
    //ajax를 사용해서 똑같은 아이디가 있는지 확인해줘라!
    $.ajax({
        type: "POST",
        url: "/sign_up/check_dup",
        data: {
            username_give: username //let username = $("#input-username").val() /username은 인풋박스로 받은 값
        },
        success: function (response) {
            if (response["exists"]) {//만약에 키값으로 "exists"을 받아오면 아래 내용을 실행시켜라
                $("#help-id").text("이미 존재하는 아이디입니다.").removeClass("is-safe").addClass("is-danger")
                $("#input-username").focus()
            } else {
                $("#help-id").text("사용할 수 있는 아이디입니다.").removeClass("is-danger").addClass("is-success")
            }
            $("#help-id").removeClass("is-loading")
        }
    });
}

