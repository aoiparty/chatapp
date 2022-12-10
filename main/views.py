from django.shortcuts import render,redirect
from django.http import HttpResponse

from django.contrib.auth import views as auth_views #Django標準機能から便利機能をインポート

from django.contrib import auth  

from .forms import SignUpForm,LoginForm,TalkForm,UsernameChangeForm,EmailChangeForm

from .models import User #models.pyからUser情報を

from django.contrib.auth.decorators import login_required

# Create your views here.


def index(request):
    return render(request,"main/index.html")
    #urls.pyからindex関数を呼び出す→mainのindex.htmlを表示


class LoginView(auth_views.LoginView):#継承　#クラスにはas_views(関数化)が必要
    authentication_form = LoginForm  # ログイン用のフォームを指定
    template_name = "main/login.html"  # テンプレートを指定

#def login(request): 上のクラスと同じ
    #return render(request, "main/login.html")


def signup(request):
#会員登録の流れの関数
    if request.method == "GET":
        form = SignUpForm()
    elif request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            # モデルフォームは form の値を models にそのまま格納できる
            #入力情報の条件を満たしているか

            # save() メソッドがあるので便利
            form.save()
            #ツーざー情報を保存

            # フォームから username と password を読み取る
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]

            # 認証情報のセットを検証するには authenticate() を利用します。
            # このメソッドは認証情報をキーワード引数として受け取ります。
            user = auth.authenticate(username=username, password=password)
            #ユーザー情報をデーターベースから取り出す
            #(username=username, password=password)...４０、４１へ

            # 検証する対象はデフォルトでは username と password であり、
            # その組み合わせを個々の認証バックエンドに対して問い合わせ、
            # 認証バックエンドで認証情報が有効とされれば User オブジェクトを返します。
            # もしいずれの認証バックエンドでも認証情報が有効と判定されなければ
            # PermissionDenied エラーが送出され、None が返されます。
            # つまり、autenticate メソッドは"username"と"password"を受け取り、
            # その組み合わせが存在すればその User を返し、不正であれば None を返します。
            if user:
                # あるユーザーをログインさせる場合は、login() を利用します。
                # この関数は HttpRequest オブジェクトと User オブジェクトを受け取ります。
                # ここでの User は認証バックエンド属性を持ってる必要があり、
                # authenticate() が返す User は user.backend（認証バックエンド属性）を持つので連携可能。
                auth.login(request, user)
                #ログインする

            return redirect("index")
            #index.htmlを表示

    context = {"form": form}
    #html内で{{form}}→SignUpForm()のこと（）２７,２９へ

    return render(request, "main/signup.html", context)

@login_required
def friends(request):#友達一覧の関数
    #friends_list=User.objects.all()#Userのオブジェクトを全て
    friends_list=User.objects.exclude(id=request.user.id)#リクエスト者（自分）のid以外のオブジェクト
    context={"friends_list":friends_list}
    return render(request, "main/friends.html",context)

# ...

# 以下を追加。機能は後で作るので今アクセスしてもエラーになります。
def talk_room(request, user_id):
    
 # get_object_or_404 は、第一引数にモデル名、その後任意の数のキーワードを受け取り、
    # もし合致するデータが存在するならそのデータを、存在しないなら 404 エラーを発生させます。
    friend = get_object_or_404(User, id=user_id)


    #friend = User.Objects.filter(
        #Q(sender = request.user, recierver = friend)
         #Q(sender = friend, reciever = request.user)
         #QオブジェクトでAND検索
   # ).oeder_by("time")


   # 自分が送信者で上の friend が受信者であるデータ、または friend が送信者で friend が受信者であるデータをすべて取得します。
    talks = Talk.objects.filter(
        Q(sender=request.user, receiver=friend)
        | Q(sender=friend, receiver=request.user)
    ).order_by("time")
    

    if request.method == "GET":
        form = TalkForm()
        #友達一覧から友達を選択したとき
        #フォームは空で
        
    elif request.method == "POST":
        # 送信内容を取得
        form = TalkForm(request.POST)
        #request.POST...送信内容
        if form.is_valid():
            # トークを仮作成（フォームが条件を満たすとき）
            new_talk = form.save(commit=False)
            # 　commit=False...保存手前で止める（送信者、送信先も保存するため）
            new_talk.sender = request.user
            #「ログインしている人」が送信者に
            new_talk.receiver = friend
            #「一覧で押した人」が受信者に
            new_talk.save()
            #ついに内容、送信者、送信先、日時を保存
            return redirect("talk_room", user_id)

    context={
        "form":form,
        "friend":friend,
        "talks":talks,
    }
    
    return render(request, "main/talk_room.html")



@login_required
def settings(request):
    return render(request, "main/settings.html")

# ...
# 以下を追加
@login_required
def username_change(request):
    if request.method == "GET": 
        #単純なページ遷移
        # instance を指定することで、指定したインスタンスのデータにアクセスできます
        form = UsernameChangeForm(instance=request.user)
         #instance=request.user ...名前を変更するユーザは自分
    elif request.method == "POST":
        form = UsernameChangeForm(request.POST, instance=request.user)
        #request.POST...ユーザー名
        if form.is_valid():
            #ユーザー名が条件(フォーマールール？)を満たしているとき
            form.save()
            # 保存後、完了ページに遷移します
            return redirect("username_change_done")
            #"username_change_done/"にページ遷移

    context = {"form": form}
    return render(request, "main/username_change.html", context)


@login_required
#ログインしていることが条件
def username_change_done(request):
    return render(request, "main/username_change_done.html")
    #htmlに反映

def email_change(request):
    if request.method == "GET": 
        #単純なページ遷移
        # instance を指定することで、指定したインスタンスのデータにアクセスできます
        form = EmailChangeForm(instance=request.user)
        #元々のログインしたユーザーの情報を取り出す
    elif request.method == "POST":
        form = EmailChangeForm(request.POST, instance=request.user)
        #request.POST...新しいユーザー名
        if form.is_valid():
            form.save()
            # 保存後、完了ページに遷移します
            return redirect("email_change_done")
            #"emailname_change_done/"にページ遷移
            #変更完了サインを出す

    context = {"form": form}
    #以上の内容をcontextに
    return render(request, "main/email_change.html", context)

@login_required
#ログインしていることが条件
def email_change_done(request):
    return render(request, "main/email_change_done.html")
    #htmlに反映


# ...
from django.urls import reverse_lazy  # 追加
# ...
# 以下を追加
class PasswordChangeView(auth_views.PasswordChangeView):
    #auth_view...便利機能を継承

    """Django 組み込みパスワード変更ビュー

    template_name : 表示するテンプレート
    success_url : 処理が成功した時のリダイレクト先
    """

    template_name = "main/password_change.html"
    success_url = reverse_lazy("password_change_done")
    #reverse_lazy...あとで読み込ませる（password_change_doneをまだ知らない）


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    """Django 標準パスワード変更ビュー"""

    template_name = "main/password_change_done.html"


# ...
# 以下を追加
class LogoutView(auth_views.LogoutView):
    pass

#settings.pyの135行目へ

