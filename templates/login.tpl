<!--
The Login page for users and admins of our library service.

They all rebase "base.tpl" so that we don't have to include
the same HTML code in all templates (<head>, Bootstrap, etc)

We did not write this login page. We just found a template here
https://bootsnipp.com/snippets/dldxB
and just replaced "login" by "email" since the User login is his email

See https://bottlepy.org/docs/dev/stpl.html#stpl.rebase
-->

% rebase('templates/base.tpl', title='Page Title')

<div class="container vh-100 d-flex align-items-center">
    <div class="border mx-auto p-5">
        <form action="/login" method="post">
            <div><p class="text-danger">{{!error}}</p></div>
            <div class="form-group m-2">
                <input name="email" value="{{email}}" type="email" class="form-control" id="email" aria-describedby="emailHelp" placeholder="Email">
                <small id="emailHelp" class="form-text text-muted">We'll never share your email with anyone else.</small>
            </div>
            <div class="form-group m-2">
                <input name="password" value="{{password}}" type="password" class="form-control" id="password" placeholder="Password">
            </div>
            <button type="submit" class="btn btn-primary mt-3">Login</button>
            <div> Don't have an account yet? <a href="/register">Register here</a></div>
        </form>
    </div>
</div>