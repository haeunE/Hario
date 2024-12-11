from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from apps.app import db
from apps.crud.models import User, Userinfo, UserRole
from apps.auth.forms import UserForm, UserinfoForm
from flask_login import login_user, logout_user

auth = Blueprint("auth", __name__, template_folder="templates/auth", static_folder="static")


@auth.route("/signup/check", methods=["POST"])
def uni_num_check():
    uniquenum = request.form.get("uniquenum")
    
    if len(uniquenum) == 6 and uniquenum.isdigit():  # 유효한 숫자 입력 확인
        uniquenum = int(uniquenum)
        userinfo = Userinfo.query.filter_by(uniquenum=uniquenum).first()

        if userinfo:
            flash("고유번호가 확인되었습니다. 회원가입을 계속 진행하세요.")
            session['userinfo_exists'] = True
            session['uniquenum'] = uniquenum
        else:
            flash("고유번호가 존재하지 않습니다. 개인정보를 입력해주세요.")
            session['userinfo_exists'] = False
            session['uniquenum'] = uniquenum

        return redirect(url_for("auth.signup"))
    
    flash("유효한 고유번호 6자리를 입력해주세요.")
    return redirect(url_for("auth.signup"))


def process_userinfo(uniquenum, info):
    """사용자 정보 등록 및 고유번호 처리 메서드"""
    userinfo = Userinfo(
        uniquenum=uniquenum,  # 고유번호를 등록할 때 uniquenum을 함께 저장
        name=info.name.data,
        birthdate=info.birthdate.data,
        tel=info.tel.data,
        email =info.email.data,
        department_id=99  # '소속없음'으로 설정
    )
    db.session.add(userinfo)
    db.session.commit()
    return userinfo


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    # 폼 초기화
    form = UserForm()
    info = UserinfoForm()

    userinfo_exists = session.get('userinfo_exists', False)
    uniquenum = session.get('uniquenum')

    if request.method == "POST":
        if not userinfo_exists and info.validate_on_submit():
            existing_user = Userinfo.query.filter(
                (Userinfo.tel == info.tel.data) | (Userinfo.email == info.email.data)
            ).first()

            if existing_user:
                if existing_user.tel == info.tel.data:
                    flash("이미 등록된 전화번호입니다. 다른 번호를 사용해주세요.", "error")
                if existing_user.email == info.email.data:
                    flash("이미 등록된 이메일입니다. 다른 이메일을 사용해주세요.", "error")
                return redirect(url_for("auth.signup"))

            # 중복이 없을 경우 사용자 정보 처리 및 저장
            process_userinfo(uniquenum, info)

            flash("개인정보가 등록되었습니다. 회원 정보를 입력해주세요.")
            session['userinfo_exists'] = True
            return redirect(url_for("auth.signup"))

        if userinfo_exists and form.validate_on_submit():
            # 회원 정보 등록
            userinfo = Userinfo.query.filter_by(uniquenum=uniquenum).first()

            if userinfo:
                # 이미 등록된 사용자 체크
                exist_user = User.query.filter_by(userinfo_id=userinfo.id).first()
                if exist_user:
                    flash("이미 회원가입된 회원입니다. 로그인 해주세요.")
                    session.pop('userinfo_exists', None)
                    session.pop('uniquenum', None)
                    return redirect(url_for("auth.login"))

                # 고유번호와 부서에 따른 역할 처리
                if userinfo.department_id == 99:
                    # 취준생일 경우
                    user = User(
                        username=form.username.data,
                        password=form.password.data,
                        userinfo_id=userinfo.id
                    )
                else:
                    # 일반 근로자일 경우
                    user = User(
                        username=form.username.data,
                        password=form.password.data,
                        role=UserRole.WORKER,
                        userinfo_id=userinfo.id
                    )

                # 아이디 중복 체크
                if user.is_duplicate_username():
                    flash("아이디는 중복 불가능합니다.")
                else:
                    db.session.add(user)
                    db.session.commit()
                    login_user(user)
                    flash("회원가입이 완료되었습니다.")
                    session.pop('userinfo_exists', None)
                    session.pop('uniquenum', None)
                    return redirect(url_for("crud.index"))
            else:
                flash("유효한 고유번호로 회원 정보를 찾을 수 없습니다.")
                return redirect(url_for("auth.signup"))

    return render_template("signup.html", form=form, info=info, userinfo_exists=userinfo_exists, uniquenum=uniquenum)



@auth.route("/login", methods=["GET", "POST"])
def login():
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for("crud.index"))
        
        flash("아이디 또는 비밀번호가 일치하지 않습니다.")
    return render_template("login.html", form = form)

@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("crud.index"))
