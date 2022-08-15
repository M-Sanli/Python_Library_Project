<%
home_class = "nav-link active" if page == "home" else "nav-link"
borrow_book_class = "nav-link active" if page == "borrow_book" else "nav-link"
%>
<div class="container">
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary p-2">
    <a class="navbar-brand" href="/home">
      <img src="/static/book.svg" width="30" height="30" class="d-inline-block align-top" alt="">
      Library
    </a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        <li class="nav-item">
          <a class="{{home_class}}" href="/home">Home</a>
        </li>
        <li class="nav-item">
          <a class="{{borrow_book_class}}" href="/borrow_books">Borrow Books</a>
        </li>
      </ul>
    </div>
    <a href="/logout" class="btn btn-danger mr-2">LOGOUT</a>
  </nav>
</div>