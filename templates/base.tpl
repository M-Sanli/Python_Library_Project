<!--
This base template will be the base file that all other
templates will use. That way, we can include things
like Bootstrap (https://getbootstrap.com/) only in one
place, and all pages will have it.

See https://bottlepy.org/docs/dev/stpl.html#stpl.rebase

This is the starter template offered by Bootstrap so that Bootstrap can work in our page.
We got it from https://getbootstrap.com/docs/5.0/getting-started/introduction/#starter-template
We just changed the title and of course the content of the body, which will be what other templates
we create, like home.tpl, will provide.

-->

<!doctype html>
<html lang="en">
  <head>
    <!-- Required meta tags -->
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-giJF6kkoqNQ00vy+HMDP7azOuL0xtbfIcaT9wjKHr8RbDVddVHyTfAAsrekwKmP1" crossorigin="anonymous">

    <!-- FontAwesome   -->
    <script src="https://kit.fontawesome.com/f4002e2afc.js" crossorigin="anonymous"></script>

    <title>Online Library</title>
  </head>
  <body>
    <!--
    This is what allows Bottle to understand that what will be in other templates will be in here.
    See https://bottlepy.org/docs/dev/stpl.html#stpl.rebase
    -->
    {{!base}}

    <!-- Optional JavaScript-->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/js/bootstrap.bundle.min.js" integrity="sha384-ygbV9kiqUc6oa4msXn9868pTtWMgiQaeYH7/t7LECLbyPA2x65Kgf80OJFdroafW" crossorigin="anonymous"></script>
  </body>
</html>
